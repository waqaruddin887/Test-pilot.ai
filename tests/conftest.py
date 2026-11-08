import time

import pytest
from fastapi.testclient import TestClient
from testpilot.api import create_app
from testpilot.db import Base, OracleVersion, Slot, database
from testpilot.fixtures import ORACLES, SOURCE_HASH


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setenv("TESTPILOT_DATA_DIR", str(tmp_path))
    engine, sessions = database("sqlite:///" + str(tmp_path / "test.db"))
    Base.metadata.create_all(engine)
    with sessions.begin() as db:
        db.add(Slot(id=1, enabled=True, heartbeat=time.time()))
        for ref, oracle in ORACLES.items():
            db.add(OracleVersion(id=ref, specification=oracle, source_sha256=SOURCE_HASH))
    yield sessions, tmp_path
    engine.dispose()


@pytest.fixture
def client(store, monkeypatch):
    sessions, directory = store
    monkeypatch.setenv("TESTPILOT_CLI_TOKEN", "c" * 40)
    monkeypatch.setenv("TESTPILOT_OPERATOR_SECRET", "s" * 40)
    app = create_app(sessions, directory)
    with TestClient(
        app, base_url="http://localhost:8000", headers={"Authorization": "Bearer " + "c" * 40}
    ) as client:
        yield client


def create_project(client, seeded=False):
    response = client.post(
        "/api/projects",
        json={
            "name": "Test fixture",
            "fixture_authorization_ref": "synthetic-seeded-v1"
            if seeded
            else "synthetic-control-v1",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_run(client, project, path="/form", key="test-run"):
    return client.post(
        "/api/runs",
        headers={"Idempotency-Key": key},
        json={
            "project_id": project,
            "target_path": path,
            "objective": "Check fixture requirement",
            "max_cases": 1,
            "mode": "smoke",
        },
    )
