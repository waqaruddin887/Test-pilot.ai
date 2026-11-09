"""One foreground, host-local durable fixture worker. No automatic side-effect replay."""

import argparse
import asyncio
import base64
import fcntl
import hashlib
import os
import time
from pathlib import Path

from sqlalchemy import delete, select

from testpilot.db import (
    Artifact,
    Attempt,
    Authorization,
    CaseRecord,
    Finding,
    Job,
    OperatorSession,
    OracleVersion,
    PlanStep,
    Run,
    Slot,
    StepResult,
    database,
    uid,
)
from testpilot.domain import TERMINAL, atomic_transition, digest, evidence_available, transition
from testpilot.fixtures import SOURCE_HASH
from testpilot.isolation import invoke
from testpilot.planner import plan_fixture


def cleanup(sessions, data_dir: Path):
    with sessions.begin() as db:
        for item in db.scalars(select(Artifact).where(Artifact.expires_at <= time.time())):
            (data_dir / "artifacts" / item.id).unlink(missing_ok=True)
        # Delete bytes before metadata. Preserve active cleanup obligations.
        old_runs = db.scalars(
            select(Run).where(Run.created_at < time.time() - 604800, Run.state.in_(TERMINAL))
        ).all()
        for run in old_runs:
            for item in db.scalars(select(Artifact).where(Artifact.run_id == run.id)):
                (data_dir / "artifacts" / item.id).unlink(missing_ok=True)
            db.delete(run)
        db.execute(delete(OperatorSession).where(OperatorSession.expires_at <= time.time()))


def recover_interrupted(sessions):
    """Called only after acquiring exclusive host lock; bwrap dies with prior supervisor."""
    with sessions.begin() as db:
        for run in db.scalars(select(Run).where(Run.state.not_in(TERMINAL), Run.state != "queued")):
            run.cancel_requested = False
            transition(db, run, "failed")
            run.reason = "interrupted_uncertain_outcome_no_replay"
            job = db.scalar(select(Job).where(Job.run_id == run.id))
            job.state = "failed"
        slot = db.get(Slot, 1)
        slot.active_run = None
        slot.enabled = False


async def execute_run(sessions, data_dir: Path, run_id: str):
    data_dir.joinpath("artifacts").mkdir(parents=True, exist_ok=True, mode=0o700)

    def cancelled():
        with sessions() as db:
            run = db.get(Run, run_id)
            auth = db.get(Authorization, run.policy["authorization_id"])
            return (
                run.cancel_requested or not auth or auth.revoked or auth.expires_at <= time.time()
            )

    def stage(state):
        with sessions.begin() as db:
            run = db.get(Run, run_id)
            if cancelled():
                raise asyncio.CancelledError()
            if not atomic_transition(db, run.id, run.state, state):
                raise asyncio.CancelledError()

    with sessions.begin() as db:
        run = db.get(Run, run_id)
        if not run or run.state != "queued":
            return
        job = db.scalar(select(Job).where(Job.run_id == run_id))
        if run.cancel_requested:
            atomic_transition(db, run.id, "queued", "cancelled")
            job.state = "cancelled"
            return
        if run.created_at < time.time() - 120:
            if not atomic_transition(db, run.id, "queued", "failed"):
                return
            run.reason = "queue_timeout"
            job.state = "failed"
            return
        started_at = time.time()
        if not atomic_transition(db, run.id, "queued", "discovering", started_at=started_at):
            return
        job.state = "claimed"
        db.get(Slot, 1).active_run = run.id
        frozen = {
            "objective": run.objective,
            "target_path": run.target_path,
            "max_cases": run.max_cases,
            "defective": run.policy["fixture"] == "synthetic-seeded-v1",
        }
        deadline = started_at + 300

    async def call(kind, **extra):
        if cancelled():
            raise asyncio.CancelledError()
        remaining = deadline - time.time()
        if remaining <= 0:
            raise TimeoutError("run_timeout")
        command = {"kind": kind, **frozen, **extra}
        with sessions.begin() as db:
            db.scalar(select(Job).where(Job.run_id == run_id)).intent = digest(command)
        return await invoke(command, cancelled=cancelled, timeout=min(40, remaining))

    try:
        observation = await call("discover")
        stage("planning")
        plan, provenance = plan_fixture(
            frozen["objective"], frozen["target_path"], observation, frozen["max_cases"]
        )
        plan_data = plan.model_dump()
        with sessions.begin() as db:
            run = db.get(Run, run_id)
            run.plan = plan_data
            run.provenance = {
                **provenance,
                "plan_sha256": digest(plan_data),
                "oracle_source_sha256": SOURCE_HASH,
                "fixture_version": "1.0.0",
                "policy_version": "offline-1",
                "seed": 0,
                "discovery": observation,
            }
            case = CaseRecord(run_id=run_id, definition=plan_data["cases"][0])
            db.add(case)
            db.flush()
            case_id = case.id
            for sequence, step in enumerate(plan_data["cases"][0]["steps"]):
                db.add(PlanStep(case_id=case_id, sequence=sequence, definition=step))
        stage("executing")

        async def attempt(kind):
            with sessions.begin() as db:
                record = Attempt(case_id=case_id, kind=kind)
                db.add(record)
                db.flush()
                attempt_id = record.id
            result = await call("execute", plan=plan_data)
            ids = []
            with sessions.begin() as db:
                record = db.get(Attempt, attempt_id)
                record.assessment = result["assessment"]
                record.receipt = {
                    k: v for k, v in result.items() if k not in {"artifacts", "steps"}
                }
                for step in result["steps"]:
                    db.add(StepResult(attempt_id=attempt_id, observation=step))
                for artifact in result["artifacts"]:
                    content = base64.b64decode(artifact["data"], validate=True)
                    if (
                        len(content) > 8 * 1024 * 1024
                        or hashlib.sha256(content).hexdigest() != artifact["sha256"]
                    ):
                        raise ValueError("artifact_integrity_failed")
                    used_bytes = sum(
                        path.stat().st_size
                        for path in (data_dir / "artifacts").iterdir()
                        if path.is_file()
                    )
                    if used_bytes + len(content) > 1024 * 1024 * 1024:
                        raise ValueError("artifact_store_quota_exceeded")
                    artifact_id = uid()
                    temporary = data_dir / "artifacts" / (artifact_id + ".tmp")
                    temporary.write_bytes(content)
                    temporary.chmod(0o600)
                    temporary.replace(data_dir / "artifacts" / artifact_id)
                    db.add(
                        Artifact(
                            id=artifact_id,
                            run_id=run_id,
                            attempt_id=attempt_id,
                            kind=artifact["kind"],
                            sha256=artifact["sha256"],
                            size=len(content),
                            expires_at=time.time() + 86400,
                        )
                    )
                    ids.append(artifact_id)
            return result, attempt_id, ids

        initial, initial_id, artifacts = await attempt("initial")
        stage("verifying")
        assessment = initial["assessment"]
        if assessment == "suspected":
            reproduction, reproduction_id, reproduction_artifacts = await attempt("reproduction")
            failed = next(s for s in initial["steps"] if s["status"] == "assertion_failed")
            reproduced = any(
                s["status"] == "assertion_failed" and s.get("oracle_ref") == failed["oracle_ref"]
                for s in reproduction["steps"]
            )
            with sessions.begin() as db:
                oracle = db.get(OracleVersion, failed["oracle_ref"])
                machine = (
                    "verified"
                    if reproduced and oracle.reviewed_at
                    else "suspected"
                    if reproduced
                    else "inconclusive"
                )
                reason = (
                    "oracle_violation_reproduced"
                    if machine == "verified"
                    else "oracle_human_review_pending"
                    if reproduced
                    else "not_reproduced"
                )
                manifest = {
                    "run_id": run_id,
                    "case_id": case_id,
                    "initial_attempt": initial_id,
                    "reproduction_attempt": reproduction_id,
                    "artifacts": artifacts + reproduction_artifacts,
                    "oracle_ref": failed["oracle_ref"],
                    "oracle_sha256": oracle.source_sha256,
                    "plan_sha256": digest(plan_data),
                    "seed": 0,
                    "reset_version": "static-fresh-context-1",
                }
                finding = Finding(
                    run_id=run_id,
                    case_id=case_id,
                    oracle_ref=failed["oracle_ref"],
                    machine_state=machine,
                    reproduced=reproduced,
                    reason=reason,
                    manifest=manifest,
                    manifest_sha256=digest(manifest),
                )
                db.add(finding)
                db.flush()
                if machine == "verified" and not evidence_available(db, finding, data_dir):
                    finding.machine_state = "suspected"
                    finding.reason = "evidence_incomplete"
                assessment = finding.machine_state
        with sessions.begin() as db:
            db.get(CaseRecord, case_id).assessment = assessment
        stage("completed")
        with sessions.begin() as db:
            db.scalar(select(Job).where(Job.run_id == run_id)).state = "succeeded"
    except asyncio.CancelledError:
        with sessions.begin() as db:
            run = db.get(Run, run_id)
            if run.state not in TERMINAL:
                transition(db, run, "cancelled")
            db.scalar(select(Job).where(Job.run_id == run_id)).state = "cancelled"
    except Exception as exc:
        with sessions.begin() as db:
            run = db.get(Run, run_id)
            if run.state not in TERMINAL:
                transition(db, run, "cancelled" if run.cancel_requested else "failed")
            run.reason = "execution_error:" + type(exc).__name__
            db.scalar(select(Job).where(Job.run_id == run_id)).state = "failed"
        print(f"Run {run_id}: {type(exc).__name__}", flush=True)
    finally:
        with sessions.begin() as db:
            db.get(Slot, 1).active_run = None


async def serve(once=False):
    _, sessions = database()
    directory = Path(os.environ.get("TESTPILOT_DATA_DIR", ".runtime"))
    with (directory / "worker.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        recover_interrupted(sessions)
        proof = await invoke({"kind": "probe"})
        negative = await invoke({"kind": "adversarial"})
        if negative["violations_executed"] or len(proof["proof"]["denied_destinations"]) != 5:
            raise RuntimeError("isolation_negative_test_failed")

        async def heartbeat():
            last_cleanup = 0
            while True:
                with sessions.begin() as db:
                    slot = db.get(Slot, 1)
                    slot.heartbeat, slot.enabled, slot.proof = (
                        time.time(),
                        True,
                        {**proof, "adversarial": negative},
                    )
                if time.time() - last_cleanup >= 60:
                    cleanup(sessions, directory)
                    last_cleanup = time.time()
                await asyncio.sleep(2)

        pulse = asyncio.create_task(heartbeat())
        try:
            while True:
                with sessions() as db:
                    run = db.scalar(
                        select(Run).where(Run.state == "queued").order_by(Run.created_at)
                    )
                    run_id = run.id if run else None
                if run_id:
                    await execute_run(sessions, directory, run_id)
                if once:
                    break
                await asyncio.sleep(0.25)
        finally:
            pulse.cancel()
            with sessions.begin() as db:
                db.get(Slot, 1).enabled = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    asyncio.run(serve(args.once))
