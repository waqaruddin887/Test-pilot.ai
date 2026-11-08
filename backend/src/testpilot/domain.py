import hashlib
import json
import time
from pathlib import Path

from sqlalchemy import select

from testpilot.db import Artifact, Finding, Review, Run, RunEvent

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
