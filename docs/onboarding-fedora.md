# Fedora developer onboarding

Follow the root README from the repository root. The tested host has Python 3.14,
Node 22, pnpm 12, Git, bubblewrap, util-linux and cached Chromium 149. Python and
JavaScript dependencies are pinned in requirements.lock and pnpm-lock.yaml.
No sudo/system package/service/SELinux/firewall changes were made.

1. Inspect `AGENTS.md`, this README and `docs/README.md`. Preserve uncommitted work.
2. Create `.venv`, install the Python lock then the editable local distribution,
   install the pnpm lock and matching Playwright Chromium. Use an ordinary terminal
   with network permission for dependency downloads.
3. Generate private `.env` with `scripts/setup_local.py`. Never use actual provider,
   production-login or customer credentials for fixture runs.
4. Run `scripts/probe.py`. It must report a distinct network namespace, denied
   destinations, private home absent, and a successful sandboxed browser. A failure
   is a blocker; no fallback to an unrestricted browser exists.
5. Run `scripts/dev.sh`, unlock the exact localhost UI origin, and create fixtures.
6. Run the test/check commands in the README. Stop development servers before the
   UI E2E test, which owns temporary loopback ports and cleans up its processes.

Podman exists here but fails initializing a read-only `/run/user/1000/libpod` path.
Docker, psql and redis-server are absent on PATH. This does not prove no remote
service exists; no unrelated service or account was probed. Do not change runtime
directories or install/configure containers to bypass permission boundaries.

The SQLite adapter is local/disposable and cannot establish PostgreSQL correctness.
Use `alembic upgrade head` for a fresh schema. Reversible downgrade/reapply is tested
only on disposable databases; do not downgrade valuable data. An explicit private
backup/retention decision is required before a future non-disposable migration.

Troubleshooting:

- Worker unavailable: run the probe from an ordinary shell and inspect the worker's
  safe error class. Host namespace/browser prerequisites must pass.
- 401: unlock with local operator secret; browser session lasts eight hours.
- 403: use exactly http://localhost:3000; check authorization expiry/revocation.
- 409 source changed: create a newly versioned fixture authorization; do not edit a
  published requirement under the same revision during active execution.
- 429: one pending/active run is allowed; inspect/cancel the current run.
- Planned mode 503: intentional; live provider and spending policy are unconfigured.
- Build fails on local IPC: webpack is already the selected supported path. In Codex,
  explicit process/socket permission was still needed for a successful build.
