# ADR-013: Verify the existing application against real PostgreSQL

Date: 2026-11-09. Accepted for local integration testing.

Rechecking `podman info` outside Codex's filesystem/syscall sandbox succeeded and
reported rootless mode. The previous read-only /run/user failure was a tool-sandbox
limitation, not proof that host Podman was unusable. ADR-012 remains the correct
closed browser mode; its infrastructure observation is superseded by this check.
No host services, system packages, SELinux or firewall settings were changed.

Run the existing regression suite against a temporary PostgreSQL 17 container.
Pin the tested official image digest, publish only a randomly allocated loopback
port, use tmpfs data with configured CPU/memory/PID limits and read-only root, and
remove only the runner's generated container in finally. No persistent volume or
application data is mounted. SIGINT/SIGTERM stop the owned pytest process before
container cleanup. SIGKILL cannot execute finally; generated containers carry the
specific test-purpose label for inspection, never a broad automatic prune.

Use TESTPILOT_TEST_DATABASE_URL solely for tests. Each fixture creates and drops its
own randomly named schema. Operators must supply a disposable test database, never
production/customer credentials. Default tests remain SQLite. PostgreSQL-specific
checks are explicitly skipped without that opt-in URL. The wrapper provides it
only to its child tests, never to the browser runner or existing .env.

Acceptance: real upgrade/downgrade/reapply, migration/metadata drift check, FK/check/
unique enforcement, idempotency and concurrent admissions/claims, cancellation
precedence, and browser/evidence workflow pass. Keep measured fixture baseline and
human-review claims separate from database integration evidence.

This validates the implemented initial schema and single-host fixture runtime; it
does not implement the full normative PostgreSQL data model, Redis/RQ/outbox,
distributed fencing or production deployment. The browser namespace stays network
disabled and receives no database credentials. SQLite stays the simplest default
setup; PostgreSQL is now a tested configured adapter for the implemented subset.
