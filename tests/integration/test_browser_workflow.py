import asyncio
import time

from conftest import create_project, create_run
from sqlalchemy import select
from testpilot.db import Artifact, Finding, Run, Slot
from testpilot.worker import cleanup, execute_run


def test_control_then_defect_review_reproduction_evidence_expiry(client, store):
    sessions, directory = store
    control = create_project(client)
    run_id = create_run(client, control, key="control").json()["run_id"]
    asyncio.run(execute_run(sessions, directory, run_id))
    detail = client.get("/api/runs/" + run_id).json()
    assert detail["state"] == "completed", detail
    assert detail["assessment"] == "pass"
    assert not client.get("/api/runs/" + run_id + "/findings").json()["items"]
    seeded = create_project(client, True)
    with sessions.begin() as db:
        db.get(Slot, 1).heartbeat = time.time()
    run_id = create_run(client, seeded, key="seeded").json()["run_id"]
    asyncio.run(execute_run(sessions, directory, run_id))
    findings = client.get("/api/runs/" + run_id + "/findings").json()["items"]
    assert len(findings) == 1, client.get("/api/runs/" + run_id).json()
    finding = findings[0]
    assert finding["machine_state"] == "suspected"
    assert finding["reproduced"] and finding["evidence_available"]
    review = {
        "decision": "accepted",
        "expected_review_sequence": 0,
        "reason": "Inspected synthetic evidence",
        "inspected_manifest_sha256": finding["manifest_sha256"],
    }
    assert (
        client.post("/api/findings/" + finding["id"] + "/reviews", json=review).status_code == 409
    )
    oracle = client.get("/api/oracles").json()["items"][0]
    assert (
        client.post(
            "/api/oracles/" + oracle["ref"] + "/review",
            json={"inspected_source_sha256": oracle["source_sha256"]},
        ).status_code
        == 200
    )
    with sessions.begin() as db:
        db.get(Slot, 1).heartbeat = time.time()
    rerun = client.post(
        "/api/runs/" + run_id + "/rerun", json={}, headers={"Idempotency-Key": "reviewed-rerun"}
    )
    assert rerun.status_code == 202, rerun.text
    asyncio.run(execute_run(sessions, directory, rerun.json()["run_id"]))
    finding = client.get("/api/runs/" + rerun.json()["run_id"] + "/findings").json()["items"][0]
    assert finding["machine_state"] == "verified"
    review["inspected_manifest_sha256"] = "wrong"
    assert (
        client.post("/api/findings/" + finding["id"] + "/reviews", json=review).status_code == 409
    )
    review["inspected_manifest_sha256"] = finding["manifest_sha256"]
    assert (
        client.post("/api/findings/" + finding["id"] + "/reviews", json=review).status_code == 201
    )
    assert client.get("/api/findings/" + finding["id"]).json()["confirmed"]
    assert (
        client.post("/api/findings/" + finding["id"] + "/reviews", json=review).status_code == 409
    )
    artifact_id = finding["manifest"]["artifacts"][0]
    response = client.get("/api/artifacts/" + artifact_id)
    assert response.status_code == 200 and response.content.startswith(b"\x89PNG")
    assert response.headers["content-disposition"].startswith("attachment")
    with sessions.begin() as db:
        db.get(Artifact, artifact_id).expires_at = time.time() - 1
    assert client.get("/api/artifacts/" + artifact_id).status_code == 410
    assert not client.get("/api/findings/" + finding["id"]).json()["confirmed"]
    cleanup(sessions, directory)
    assert not (directory / "artifacts" / artifact_id).exists()
    with sessions() as db:
        assert (
            db.scalar(select(Finding).where(Finding.id == finding["id"])).machine_state
            == "verified"
        )
        assert db.get(Run, run_id).state == "completed"


def test_expired_queue_does_not_execute(client, store):
    sessions, directory = store
    project = create_project(client)
    run_id = create_run(client, project).json()["run_id"]
    with sessions.begin() as db:
        db.get(Run, run_id).created_at = time.time() - 121
    asyncio.run(execute_run(sessions, directory, run_id))
    with sessions() as db:
        assert db.get(Run, run_id).reason == "queue_timeout"
