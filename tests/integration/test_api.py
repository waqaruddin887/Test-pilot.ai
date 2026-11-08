import time

from conftest import create_project, create_run
from sqlalchemy import select
from testpilot.db import Authorization, Job, Run, Slot


def test_auth_host_csrf_and_session(client):
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/projects", headers={"Authorization": ""}).status_code == 401
    assert client.get("/api/health", headers={"Host": "evil.test"}).status_code == 403
    body = {"secret": "s" * 40}
    assert (
        client.post("/api/session/bootstrap", json=body, headers={"Authorization": ""}).status_code
        == 403
    )
    response = client.post(
        "/api/session/bootstrap",
        json=body,
        headers={"Authorization": "", "Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert "HttpOnly" in response.headers.get_list("set-cookie")[0]
    assert client.get("/api/projects", headers={"Authorization": ""}).status_code == 200
    project = {"name": "Fixture", "fixture_authorization_ref": "synthetic-control-v1"}
    assert (
        client.post(
            "/api/projects",
            json=project,
            headers={"Authorization": "", "Origin": "http://localhost:3000"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/projects",
            json=project,
            headers={
                "Authorization": "",
                "Origin": "http://localhost:3000",
                "X-CSRF-Token": client.cookies.get("tp_csrf"),
            },
        ).status_code
        == 201
    )


def test_idempotency_atomic_job_and_conflict(client, store):
    project = create_project(client)
    first = create_run(client, project)
    assert first.status_code == 202, first.text
    assert create_run(client, project).json()["run_id"] == first.json()["run_id"]
    assert create_run(client, project, "/cart").status_code == 409
    assert create_run(client, project, key="another").status_code == 429
    sessions, _ = store
    with sessions() as db:
        assert len(db.scalars(select(Run)).all()) == 1
        assert len(db.scalars(select(Job)).all()) == 1
    assert (
        client.post("/api/runs/" + first.json()["run_id"] + "/cancel", json={}).json()["state"]
        == "cancelled"
    )
    assert client.post("/api/runs/" + first.json()["run_id"] + "/cancel", json={}).json()[
        "already_terminal"
    ]
    next_run = client.post(
        "/api/runs/" + first.json()["run_id"] + "/rerun",
        headers={"Idempotency-Key": "rerun"},
        json={},
    )
    assert next_run.status_code == 202
    assert next_run.json()["run_id"] != first.json()["run_id"]


def test_unavailable_and_no_self_authorization(client, store):
    project = create_project(client)
    assert (
        client.post(
            "/api/projects", json={"name": "Evil", "fixture_authorization_ref": "http://evil.test"}
        ).status_code
        == 422
    )
    assert create_run(client, project, "/form?secret=1").status_code == 403
    sessions, _ = store
    with sessions.begin() as db:
        db.get(Slot, 1).heartbeat = 0
    assert create_run(client, project).status_code == 503
    with sessions.begin() as db:
        assert not db.scalars(select(Run)).all()
        db.get(Slot, 1).heartbeat = time.time()
        db.scalar(select(Authorization)).revoked = True
    assert create_run(client, project).status_code == 403


def test_payload_and_extra_fields(client):
    assert client.post("/api/projects", content=b"x" * 65537).status_code == 413
    response = client.post(
        "/api/projects",
        json={
            "name": "fixture",
            "fixture_authorization_ref": "synthetic-control-v1",
            "origin": "http://evil",
        },
    )
    assert response.status_code == 422
    assert set(response.json()) == {"code", "message", "run_id", "safe_details"}


def test_missing_planner_never_substitutes(client):
    project = create_project(client)
    assert (
        client.post(
            "/api/runs",
            headers={"Idempotency-Key": "planned"},
            json={
                "project_id": project,
                "target_path": "/form",
                "objective": "Check requirement",
                "mode": "planned",
            },
        ).status_code
        == 503
    )
