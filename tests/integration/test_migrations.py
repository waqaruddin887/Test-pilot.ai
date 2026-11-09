import os
import subprocess
from pathlib import Path

from sqlalchemy import create_engine, inspect


def test_fresh_migration_rollback_and_reapply(tmp_path):
    url = "sqlite:///" + str(tmp_path / "migration.db")
    environment = {**os.environ, "TESTPILOT_DATABASE_URL": url, "TESTPILOT_DATA_DIR": str(tmp_path)}
    alembic = str(Path(".venv/bin/alembic").resolve())
    for revision in ["head", "base", "head"]:
        command = "downgrade" if revision == "base" else "upgrade"
        result = subprocess.run(
            [alembic, command, revision],
            env=environment,
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == 0, result.stderr
        with create_engine(url).connect() as connection:
            tables = inspect(connection).get_table_names()
            assert ("runs" in tables) == (revision != "base")


def test_outbox_upgrade_preserves_and_backfills_existing_queued_run(tmp_path):
    from sqlalchemy import select
    from testpilot.db import Job, OutboxEvent, Project, Run, database

    url = "sqlite:///" + str(tmp_path / "backfill.db")
    environment = {**os.environ, "TESTPILOT_DATABASE_URL": url, "TESTPILOT_DATA_DIR": str(tmp_path)}
    alembic = str(Path(".venv/bin/alembic").resolve())

    def migrate(command, revision):
        result = subprocess.run(
            [alembic, command, revision],
            env=environment,
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == 0, result.stderr

    migrate("upgrade", "0001")
    engine, sessions = database(url)
    try:
        with sessions.begin() as db:
            project = Project(name="Migration fixture", fixture="synthetic-control-v1")
            db.add(project)
            db.flush()
            run = Run(
                project_id=project.id,
                target_path="/form",
                objective="Fixture check",
                max_cases=1,
                mode="smoke",
                policy={},
            )
            db.add(run)
            db.flush()
            job = Job(run_id=run.id)
            db.add(job)
            db.flush()
            job_id, run_id = job.id, run.id
        for _ in range(2):
            migrate("upgrade", "head")
            with sessions() as db:
                records = list(db.scalars(select(OutboxEvent)))
                assert len(records) == 1 and records[0].job_id == job_id
                assert records[0].state == "pending" and records[0].generation == 0
                assert db.get(Run, run_id).state == "queued"
            migrate("downgrade", "0001")
    finally:
        engine.dispose()
