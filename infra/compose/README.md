# Local infrastructure verification

Rootless Podman works outside Codex's restricted runtime mount. The earlier
read-only `/run/user/1000/libpod` failure was sandbox-specific, not a host blocker.
No system configuration changes were necessary.

`postgres-test-image.json` pins the official PostgreSQL 17 image digest actually
used by `scripts/check_postgres.py`. Pull it explicitly, then run:

```bash
podman pull docker.io/library/postgres@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1
.venv/bin/python scripts/check_postgres.py
```

The script owns one generated container, binds a random loopback port, uses tmpfs
instead of a persistent volume, configures memory/CPU/PID limits and read-only root,
runs real database tests, then removes the container. It does not modify .env or
connect to an existing application database. Tests get unique disposable schemas.
Normal SIGINT/SIGTERM invoke cleanup; SIGKILL cannot. Inspect the precise
`testpilot.purpose=disposable-integration-test` label if a force-killed run requires
manual cleanup. Never prune unrelated containers or volumes.

A full web/API/Postgres/Redis Compose deployment and distributed recovery remain
unfinished. The network-disabled browser worker is unchanged. Do not treat a
normal container bridge as browser egress isolation. See ADR-012 and ADR-013.

## Redis transport integration

redis-test-image.json pins the authenticated temporary Redis service used by
`scripts/check_postgres.py --with-redis`. The suite tests actual Redis restart with
persistence deliberately disabled and reconstructs queued notifications from the
outbox. No production Redis durability configuration is implied. Both services
have configured resource bounds and tmpfs storage; cleanup attempts both even if
removing the first fails. The browser remains in a separate network-disabled
namespace. See ADR-014 for the restricted RQ consumer contract.
