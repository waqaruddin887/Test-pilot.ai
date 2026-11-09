import hashlib
import json
import time
from pathlib import Path

from sqlalchemy import case as sql_case
from sqlalchemy import select, update

from testpilot.db import Artifact, Finding, Job, Review, Run, RunEvent

TERMINAL = frozenset({"completed", "failed", "cancelled"})
NEXT = {
    "queued": "discovering",
    "discovering": "planning",
    "planning": "executing",
    "executing": "verifying",
    "verifying": "completed",
}


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def transition(session, run: Run, state: str):
    if run.state in TERMINAL or (
        state not in {"failed", "cancelled"} and NEXT.get(run.state) != state
    ):
        raise ValueError("invalid state transition")
    if run.cancel_requested and state != "cancelled":
        raise ValueError("cancellation has precedence")
    run.state = state
    if state in TERMINAL:
        run.ended_at = time.time()
        run.active_slot = None
    session.add(RunEvent(run_id=run.id, state=state))


def atomic_transition(session, run_id: str, expected: str, state: str, started_at=None) -> bool:
    """SQL compare-and-swap: a committed cancellation or terminal state wins."""
    if expected in TERMINAL or (
        state not in {"failed", "cancelled"} and NEXT.get(expected) != state
    ):
        raise ValueError("invalid state transition")
    statement = update(Run).where(Run.id == run_id, Run.state == expected)
    if state != "cancelled":
        statement = statement.where(Run.cancel_requested.is_(False))
    values = {"state": state}
    if state in TERMINAL:
        values.update(ended_at=time.time(), active_slot=None)
    if started_at is not None:
        values["started_at"] = started_at
    result = session.execute(
        statement.values(**values).execution_options(synchronize_session=False)
    )
    if result.rowcount != 1:
        return False
    session.add(RunEvent(run_id=run_id, state=state))
    return True


def request_cancellation(session, run_id: str) -> bool:
    statement = (
        update(Run)
        .where(Run.id == run_id, Run.state.not_in(TERMINAL))
        .values(
            cancel_requested=True,
            state=sql_case((Run.state == "queued", "cancelled"), else_=Run.state),
            ended_at=sql_case((Run.state == "queued", time.time()), else_=Run.ended_at),
            active_slot=sql_case((Run.state == "queued", None), else_=Run.active_slot),
        )
        .execution_options(synchronize_session=False)
    )
    changed = session.execute(statement).rowcount == 1
    session.expire_all()
    if changed and session.get(Run, run_id).state == "cancelled":
        session.execute(update(Job).where(Job.run_id == run_id).values(state="cancelled"))
        session.add(RunEvent(run_id=run_id, state="cancelled"))
    return changed


def evidence_available(session, finding: Finding, data_dir: Path) -> bool:
    ids = finding.manifest.get("artifacts", [])
    if len(ids) != 4 or digest(finding.manifest) != finding.manifest_sha256:
        return False
    kinds = []
    for artifact_id in ids:
        artifact = session.get(Artifact, artifact_id)
        if not artifact or artifact.run_id != finding.run_id or artifact.expires_at <= time.time():
            return False
        path = data_dir / "artifacts" / artifact.id
        if (
            not path.is_file()
            or path.stat().st_size != artifact.size
            or hashlib.sha256(path.read_bytes()).hexdigest() != artifact.sha256
        ):
            return False
        kinds.append(artifact.kind)
    return kinds.count("screenshot") == 2 and kinds.count("trace") == 2


def finding_view(session, finding: Finding, data_dir: Path):
    reviews = session.scalars(
        select(Review).where(Review.finding_id == finding.id).order_by(Review.sequence)
    ).all()
    latest = reviews[-1] if reviews else None
    available = evidence_available(session, finding, data_dir)
    return {
        "id": finding.id,
        "run_id": finding.run_id,
        "case_id": finding.case_id,
        "oracle_ref": finding.oracle_ref,
        "machine_state": finding.machine_state,
        "reproduced": finding.reproduced,
        "reason": finding.reason,
        "review_state": latest.decision if latest else "unreviewed",
        "review_sequence": latest.sequence if latest else 0,
        "confirmed": finding.machine_state == "verified"
        and available
        and latest is not None
        and latest.decision == "accepted",
        "evidence_available": available,
        "manifest": finding.manifest,
        "manifest_sha256": finding.manifest_sha256,
    }
