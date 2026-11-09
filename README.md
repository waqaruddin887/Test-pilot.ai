# TestPilot AI

A local browser-testing prototype for **repository-owned synthetic fixtures**. It discovers a bounded interface outline, produces a strict deterministic test plan, runs Playwright in a network-disabled sandbox, reproduces requirement violations, and presents screenshots, traces and separate human review.

**This is a verified restricted demo, not the completed production MVP.** The implemented initial schema and fixture workflow are now integration-tested on PostgreSQL 17.11. A restricted single-host Redis/RQ notification transport with transactional outbox is also implemented. No live LLM, external targets, distributed queue supervision or production isolation certification is claimed. See [implementation status](docs/implementation-status.md), [security limitations](docs/security-status.md) and [actual evaluation](docs/evaluation-results.md).

## Prerequisites

Verified on this Fedora host with Python **3.14.8**, Node **22.23.1**, pnpm **12.10.1**, Playwright **1.61.0** / Chromium **149.0.7827.55**. `unshare` (util-linux), `bwrap` (bubblewrap), Chromium OS libraries and unprivileged user/network/mount namespaces must work. Other hosts/Python versions have not been verified. Docker is unnecessary for this offline mode. No setup script installs system packages, changes SELinux/firewall settings or starts system services.

If a prerequisite is missing, have the machine administrator provision it; execution fails closed. Never add `--no-sandbox`, use a host network, or broaden the fixture allowlist to work around a failure.

## Setup and start

From `/home/waqar/testpilot`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.lock
.venv/bin/pip install --no-build-isolation --no-deps -e .
pnpm install --frozen-lockfile
.venv/bin/python -m playwright install chromium
.venv/bin/python scripts/setup_local.py
.venv/bin/python scripts/probe.py
./scripts/dev.sh
```

Open **http://localhost:3000** (use this exact hostname). Unlock with `TESTPILOT_OPERATOR_SECRET` from your private `.env`; do not put it in a URL, commit it, or paste it into a run objective. `setup_local.py` generates random local credentials once, uses mode 0600, and preserves existing config. `.env.example` contains no secrets. `scripts/dev.sh` loads `.env`, applies the initial migration, seeds independent requirements, and starts API, worker and Next.js in owned process groups. Ctrl-C stops all three. It does not run after the terminal exits. Local development data is explicitly disposable; migrations do not create backups.

Create a known-good project and a seeded-defect project. Start an **explicit deterministic smoke** run for `/form`, `/email`, `/login`, `/navigation` or `/cart`. The browser origin `http://fixture.test` is virtual: reviewed static bytes are fulfilled inside its namespace; no DNS/network access or standalone fixture server is required. Fixture mutations change only the fresh page DOM. Login and cart are simulations, without sessions or purchases.

The good fixture passes; a seeded violation produces a reproduced **suspected** finding with initial/reproduction screenshots and traces. An operator must independently review the versioned requirement under Configuration, then rerun, to obtain **verified — awaiting review**. Accepting a finding additionally requires current complete evidence and an explicit inspection acknowledgment. Automated test reviews are disposable test data, not actual human validation. Expired evidence prevents current confirmation.

For a production-mode local frontend, run `pnpm build`, then replace `pnpm dev` with `pnpm --filter @testpilot/web start` in a separate terminal. API and worker commands are:

```bash
set -a; source .env; set +a
.venv/bin/python -m uvicorn testpilot.api:app --host 127.0.0.1 --port 8000
# Separate terminal, with the same .env loaded:
.venv/bin/python -m testpilot.worker
```

The API listens only on loopback. Next.js proxies `/api` to it. Direct API clients use the separate `TESTPILOT_CLI_TOKEN` bearer credential. Browser mutations require the exact configured Origin, HttpOnly session and CSRF token. Health is at `http://localhost:8000/api/health`; schema reference is at `/docs` and `/openapi.json`. See [implemented API notes](docs/api.md).

## Verification

```bash
.venv/bin/ruff check backend scripts tests
.venv/bin/ruff format --check backend scripts tests
.venv/bin/python -m pytest -q
pnpm typecheck
pnpm lint
pnpm format:check
pnpm test
pnpm build
.venv/bin/python scripts/dashboard_e2e.py
.venv/bin/python scripts/evaluate.py
```

Browser/API tests and Next compilation require ordinary local process/socket permissions. Codex's syscall sandbox denied Chromium and AnyIO IPC on this host; those checks were rerun with explicit tool permission while keeping the **application runner's** namespaces and Chromium sandbox enabled. The supported webpack build avoids a Turbopack IPC failure. No test is converted to a pass by disabling a security control.

`dashboard_e2e.py` temporarily uses ports 3000/8000, creates disposable data and test-only credentials, and stops its services in `finally`. Stop other local app instances first. The dashboard test browser needs loopback connectivity to the trusted dashboard; it is separate from the network-disabled autonomous target runner. Synthetic UI screenshots go to ignored `.runtime/`. The evaluator runs ten independent reference checks and thirty shuffled fresh trials. Raw counters, denominators, errors and hashes are retained in [evaluation/results/latest.json](evaluation/results/latest.json). Evaluation capture bytes are discarded, not presented as indefinitely reviewable evidence.

Regenerate contracts after backend changes:

```bash
.venv/bin/python scripts/export_contracts.py
pnpm contracts
```

## Structure

- `backend/src/testpilot/`: strict contracts, policy, API, relational records, planner, supervisor/browser, independent references, lifecycle and evidence.
- `apps/web/`: Next.js/TypeScript/Tailwind UI, separate screen components; transport types generated from backend OpenAPI.
- `fixtures/`: five good/defective synthetic pairs and public versioned requirements. Variant choice and reference results never enter planner input.
- `tests/`: contract, API, lifecycle, migrations, browser isolation/cancellation and full worker/evidence checks.
- `evaluation/`: frozen development manifest and measured counters, explicitly not held-out or LLM evaluation.
- `docs/`: preserved foundations, decisions, progress, status, onboarding, demo and limitations.

PostgreSQL remains the intended application store. The implemented SQLAlchemy/psycopg schema, reversible migrations, API/lifecycle and browser/evidence workflow are tested on PostgreSQL 17.11 as well as SQLite; the full normative data model is still unfinished. Single-host Redis/RQ JSON delivery and transactional outbox are implemented; distributed fencing and the networked fixture supervisor remain unfinished. The foreground local queue is limited to one host and one pending/active run; never start multiple workers against the same store from different data directories. Artifacts expire after 24 hours; run metadata after seven days. The worker enforces expiry on retrieval immediately and performs physical cleanup each minute while running. Expired bytes can remain on disk while the worker is stopped. No automatic backups/exports exist.

Read [Fedora onboarding](docs/onboarding-fedora.md), [ADR-012](docs/decisions/012-offline-fixture-development.md), [demo outline](docs/demo.md) and [append-only progress](docs/progress.md) before expanding scope.

## Real PostgreSQL regression

Rootless Podman is available outside Codex’s restricted runtime mount; the earlier
read-only runtime error was sandbox-specific. No host reconfiguration was needed.
The pinned test container uses a random loopback port and bounded tmpfs data, with
no application data/volumes mounted. It is removed after the test run.

```bash
podman pull docker.io/library/postgres@sha256:996e9dc583ba9f0265a2c75547a9c95fb22c251e394749cab205a0a00e1856a1
.venv/bin/python scripts/check_postgres.py
```

Without TESTPILOT_TEST_DATABASE_URL, PostgreSQL-specific tests are explicitly skipped
and the rest use SQLite. The wrapper runs the full suite with an isolated PostgreSQL
schema per test. Do not supply a production database to this test-only variable.
See [ADR-013](docs/decisions/013-real-postgresql-regression.md).

## Optional Redis/RQ notification transport

Migration `0002` adds a transactional outbox and backfills existing queued jobs.
Install the updated Python lock, then apply `alembic upgrade head` (the startup
script does this). Local polling stays the default. To use an operator-provisioned
private Redis service, set these in your private `.env`:

```dotenv
TESTPILOT_QUEUE_TRANSPORT=redis
TESTPILOT_REDIS_URL=redis://:YOUR_LOCAL_REDIS_PASSWORD@127.0.0.1:6379/0
```

Start the same `scripts/dev.sh`; its foreground worker dispatches and consumes
fixed JSON notifications. **Do not start a generic `rq worker`.** The restricted
consumer never invokes a function named by queue content. It reconciles lost
notifications only for DB-queued runs, with the original deadline. Cancelled,
active and terminal runs are never automatically replayed. Keep exactly one
foreground worker on one host with one configured data directory. Distributed
leases/fencing remain unimplemented.

Run real PostgreSQL + Redis failure/restart tests with the pinned test image:

```bash
podman pull docker.io/library/redis@sha256:2e3eb11462c4e3759e6972678dd051d150ff54b1e60714b3c33b701260172a90
.venv/bin/python scripts/check_postgres.py --with-redis
```

This creates only temporary authenticated loopback services with tmpfs data,
including a real Redis restart test, and cleans up its owned containers. The default
suite skips external-service checks explicitly. See [ADR-014](docs/decisions/014-transactional-rq-notifications.md).
