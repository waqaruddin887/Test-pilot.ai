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
