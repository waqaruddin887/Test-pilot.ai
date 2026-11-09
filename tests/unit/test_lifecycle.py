import pytest
from conftest import create_project, create_run
from sqlalchemy import select
from testpilot.db import Job, Run
from testpilot.domain import transition
from testpilot.worker import recover_interrupted


def test_transitions_cancellation_precedence_and_no_replay(client, store):
    project = create_project(client)
    run_id = create_run(client, project).json()["run_id"]
    sessions, _ = store
    with sessions.begin() as db:
        run = db.get(Run, run_id)
        with pytest.raises(ValueError):
            transition(db, run, "executing")
        transition(db, run, "discovering")
        db.scalar(select(Job)).intent = "possibly-sent"
    recover_interrupted(sessions)
    with sessions.begin() as db:
        run = db.get(Run, run_id)
        assert run.state == "failed"
        assert "no_replay" in run.reason
        assert run.active_slot is None
        with pytest.raises(ValueError):
            transition(db, run, "discovering")


def test_cancel_wins_over_completion(client, store):
    project = create_project(client)
    run_id = create_run(client, project).json()["run_id"]
    sessions, _ = store
    with sessions.begin() as db:
        run = db.get(Run, run_id)
        transition(db, run, "discovering")
        run.cancel_requested = True
        with pytest.raises(ValueError):
            transition(db, run, "planning")
        transition(db, run, "cancelled")


def test_committed_cancel_blocks_stale_claim(client, store):
    from testpilot.domain import atomic_transition

    project = create_project(client)
    run_id = create_run(client, project).json()["run_id"]
    sessions, _ = store
    with sessions() as stale:
        loaded = stale.get(Run, run_id)
        assert loaded.state == "queued"
        assert client.post("/api/runs/" + run_id + "/cancel", json={}).status_code == 200
        assert not atomic_transition(stale, run_id, loaded.state, "discovering")
        stale.commit()
    with sessions() as db:
        assert db.get(Run, run_id).state == "cancelled"


def test_committed_cancel_blocks_stale_completion(client, store):
    from testpilot.domain import atomic_transition

    project = create_project(client)
    run_id = create_run(client, project).json()["run_id"]
    sessions, _ = store
    with sessions.begin() as db:
        run = db.get(Run, run_id)
        for stage in ["discovering", "planning", "executing", "verifying"]:
            transition(db, run, stage)
    with sessions() as stale:
        loaded = stale.get(Run, run_id)
        assert not loaded.cancel_requested
        assert client.post("/api/runs/" + run_id + "/cancel", json={}).status_code == 200
        assert not atomic_transition(stale, run_id, loaded.state, "completed")
        stale.commit()
    with sessions() as db:
        assert db.get(Run, run_id).state == "verifying"
        assert db.get(Run, run_id).cancel_requested


def test_completion_committed_first_makes_cancel_noop(client, store):
    from testpilot.domain import atomic_transition

    project = create_project(client)
    run_id = create_run(client, project).json()["run_id"]
    sessions, _ = store
    with sessions.begin() as db:
        run = db.get(Run, run_id)
        for stage in ["discovering", "planning", "executing", "verifying"]:
            transition(db, run, stage)
        db.flush()
        assert atomic_transition(db, run_id, "verifying", "completed")
    result = client.post("/api/runs/" + run_id + "/cancel", json={}).json()
    assert result["state"] == "completed" and result["already_terminal"]
    with sessions() as db:
        assert not db.get(Run, run_id).cancel_requested
