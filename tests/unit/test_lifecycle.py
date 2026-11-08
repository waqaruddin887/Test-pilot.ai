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
