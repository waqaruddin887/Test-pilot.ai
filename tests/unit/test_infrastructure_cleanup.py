import subprocess
from types import SimpleNamespace

import pytest

from scripts import check_postgres


def test_cleanup_attempts_postgres_even_if_redis_cleanup_fails(monkeypatch):
    calls = []

    def remove(*arguments):
        calls.append(arguments[-1])
        if arguments[-1] == "owned-redis":
            raise RuntimeError("synthetic tool error")

    monkeypatch.setattr(check_postgres, "podman", remove)
    with pytest.raises(RuntimeError, match="owned-redis"):
        check_postgres.remove_owned_containers(["owned-redis", "owned-postgres"])
    assert calls == ["owned-redis", "owned-postgres"]


def test_cleanup_accepts_verified_absence_after_remove_error(monkeypatch):
    def missing(*arguments):
        raise subprocess.CalledProcessError(1, "podman rm")

    monkeypatch.setattr(check_postgres, "podman", missing)
    monkeypatch.setattr(
        check_postgres.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=1)
    )
    check_postgres.remove_owned_containers(["already-absent", None])
