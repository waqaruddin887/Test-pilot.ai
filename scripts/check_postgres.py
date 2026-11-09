"""Run real database regressions in a bounded, disposable rootless container.

Only generated test schemas are touched. No app database, host mounts or persistent
volumes. The image must already be pulled; its digest is pinned in the manifest.
"""

import json
import os
import secrets
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]


def podman(*arguments: str) -> str:
    result = subprocess.run(["podman", *arguments], capture_output=True, text=True, timeout=90)
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    result.check_returncode()
    return result.stdout.strip()


def main() -> int:
    os.chdir(ROOT)
    image = json.loads(Path("infra/compose/postgres-test-image.json").read_text())["image"]
    name = "testpilot-pg-test-" + secrets.token_hex(6)
    password = secrets.token_urlsafe(24)
    directory = ROOT / ".runtime"
    directory.mkdir(exist_ok=True)

    def interrupted(signum, frame):
        raise KeyboardInterrupt()

    tests_process = None
    prior = {sig: signal.signal(sig, interrupted) for sig in [signal.SIGTERM, signal.SIGINT]}
    try:
        with tempfile.TemporaryDirectory(prefix="pg-check-", dir=directory) as temporary:
            env_file = Path(temporary) / "postgres.env"
            with env_file.open("x") as output:
                env_file.chmod(0o600)
                output.write(
                    f"POSTGRES_USER=testpilot\nPOSTGRES_DB=testpilot_test\nPOSTGRES_PASSWORD={password}\nPGDATA=/var/lib/postgresql/data/pgdata\n"
                )
            podman(
                "run",
                "--detach",
                "--pull=never",
                "--name",
                name,
                "--label",
                "testpilot.purpose=disposable-integration-test",
                "--memory=512m",
                "--cpus=1",
                "--pids-limit=128",
                "--read-only",
                "--security-opt=no-new-privileges",
                "--tmpfs",
                "/var/lib/postgresql/data:rw,size=256m,mode=1777",
                "--tmpfs",
                "/var/run/postgresql:rw,size=16m,mode=1777",
                "--tmpfs",
                "/tmp:rw,size=32m,mode=1777",
                "--env-file",
                str(env_file),
                "--publish",
                "127.0.0.1::5432",
                image,
            )
            mapping = podman("port", name, "5432/tcp")
            host, port = mapping.rsplit(":", 1)
            if host != "127.0.0.1" or not port.isdecimal():
                raise RuntimeError("unexpected container publication")
            url = f"postgresql+psycopg://testpilot:{password}@127.0.0.1:{port}/testpilot_test"
            for _ in range(120):
                try:
                    with psycopg.connect(
                        host=host,
                        port=int(port),
                        user="testpilot",
                        password=password,
                        dbname="testpilot_test",
                        connect_timeout=1,
                    ) as connection:
                        version = connection.execute("SHOW server_version").fetchone()[0]
                    break
                except psycopg.OperationalError:
                    time.sleep(0.25)
            else:
                raise RuntimeError("PostgreSQL readiness deadline expired")
            print(
                f"PostgreSQL {version}; loopback-only, tmpfs data; running full suite.", flush=True
            )
            environment = {**os.environ, "TESTPILOT_TEST_DATABASE_URL": url}
            tests_process = subprocess.Popen(
                [sys.executable, "-m", "pytest", "-q"], env=environment, start_new_session=True
            )
            return tests_process.wait()
    finally:
        if tests_process is not None and tests_process.poll() is None:
            os.killpg(tests_process.pid, signal.SIGTERM)
            try:
                tests_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(tests_process.pid, signal.SIGKILL)
                tests_process.wait(timeout=5)
        try:
            podman("rm", "--force", name)
        except subprocess.CalledProcessError:
            # Absence is fine only when removal can be independently established.
            check = subprocess.run(
                ["podman", "container", "exists", name], capture_output=True, timeout=15
            )
            if check.returncode != 1:
                raise RuntimeError("container cleanup unconfirmed") from None
        finally:
            for sig, handler in prior.items():
                signal.signal(sig, handler)
        print("Temporary PostgreSQL container removed; tmpfs data discarded.", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
