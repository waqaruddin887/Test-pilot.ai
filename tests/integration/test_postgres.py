"""Opt-in real PostgreSQL checks; each test owns only its generated schema."""

import os
import subprocess
import uuid
from pathlib import Path

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from conftest import create_project, create_run
from sqlalchemy import inspect, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import CreateSchema, DropSchema
from testpilot.db import Base, Project, Run, database

pytestmark = pytest.mark.skipif(
    not os.environ.get("TESTPILOT_TEST_DATABASE_URL"),
    reason="Explicit temporary PostgreSQL URL required",
)


def test_postgres_migration_upgrade_rollback_reapply(tmp_path):
    url = make_url(os.environ["TESTPILOT_TEST_DATABASE_URL"])
    assert url.get_backend_name() == "postgresql"
    schema = "testpilot_test_" + uuid.uuid4().hex
    admin, _ = database(url.render_as_string(hide_password=False))
    with admin.begin() as connection:
        connection.execute(CreateSchema(schema))
    isolated = url.update_query_dict({"options": f"-csearch_path={schema}"})
    target = isolated.render_as_string(hide_password=False)
    engine, _ = database(target)
    environment = {
        **os.environ,
        "TESTPILOT_DATABASE_URL": target,
        "TESTPILOT_DATA_DIR": str(tmp_path),
    }
    try:
        for command, revision in [("upgrade", "head"), ("downgrade", "base"), ("upgrade", "head")]:
            result = subprocess.run(
                [str(Path(".venv/bin/alembic").resolve()), command, revision],
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, result.stderr
            with engine.connect() as connection:
                assert ("runs" in inspect(connection).get_table_names(schema=schema)) == (
                    revision == "head"
                )
                if revision == "head":
                    assert (
                        compare_metadata(MigrationContext.configure(connection), Base.metadata)
                        == []
                    )
    finally:
        engine.dispose()
        with admin.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))
        admin.dispose()


def test_postgres_enforces_foreign_key_and_single_active_slot(client, store):
    sessions, _ = store
    project = create_project(client)
    run_id = create_run(client, project).json()["run_id"]
    with sessions() as session:
        original = session.get(Run, run_id)
        definition = {
            name: getattr(original, name)
            for name in ["project_id", "target_path", "objective", "max_cases", "mode", "policy"]
        }
    with pytest.raises(IntegrityError), sessions.begin() as session:
        session.add(Run(**definition))
        session.flush()
    with pytest.raises(IntegrityError), sessions.begin() as session:
        session.delete(session.get(Project, project))
        session.flush()
    with pytest.raises(IntegrityError) as rejected, sessions.begin() as session:
        session.add(Run(**{**definition, "max_cases": 0}, state="cancelled", active_slot=None))
        session.flush()
    assert rejected.value.orig.sqlstate == "23514"  # PostgreSQL CHECK violation
    with sessions() as session:
        assert list(session.scalars(select(Run.id))) == [run_id]


def test_postgres_duplicate_claim_has_one_winner(client, store):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from testpilot.domain import atomic_transition

    project = create_project(client)
    run_id = create_run(client, project).json()["run_id"]
    sessions, _ = store
    barrier = Barrier(2)

    def claim():
        with sessions.begin() as session:
            barrier.wait(timeout=5)
            return atomic_transition(session, run_id, "queued", "discovering")

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: claim(), range(2)))
    assert sorted(results) == [False, True]
    with sessions() as session:
        assert session.get(Run, run_id).state == "discovering"


def test_postgres_simultaneous_admission_persists_one_job(client, store):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from testpilot.db import Idempotency, Job

    project = create_project(client)
    sessions, _ = store
    barrier = Barrier(2)

    def submit(index):
        barrier.wait(timeout=5)
        return create_run(client, project, key=f"concurrent-{index}").status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(submit, range(2)))
    assert statuses.count(202) == 1
    assert all(status in {202, 409, 429} for status in statuses)
    with sessions() as session:
        assert len(list(session.scalars(select(Run)))) == 1
        assert len(list(session.scalars(select(Job)))) == 1
        assert len(list(session.scalars(select(Idempotency)))) == 1
