# Implementation progress (append only)

## 2026-11-08 — Initial inspection

- Repository has no application code or commits. Existing AGENTS.md and docs/ are untracked user material; preserved.
- Read foundation review and all 14 active foundations. Canonical docs/ and archived exports already exist; no Docs/ or root Agents.md remains. Archive has 17 files, no attachment directories.
- Read normative plan, safety, data, jobs, finding/evaluation and HTTP contracts. ADR-012 records the local offline fallback rather than silently overriding v0.2.
- Installed tools: Python 3.14.8, Node 22.23.1, pnpm 12.10.1, Git; Playwright 1.61.0 and Chromium cache present. No Docker, psql or redis-server. Podman initialization fails on read-only runtime path.
- unshare user/network and minimal bubblewrap mounts succeeded. Chromium sandbox probe failed with EPERM in Codex sandbox; isolated escalation probe pending. No browser test success claimed.
- Started project virtualenv dependency installation with registry permission; no system packages/services/settings changed.
- Next: strict contracts/policy, fixtures/reference tests, persistence/API, isolated runner, worker and UI. Browser admission stays disabled unless real probe passes.

## 2026-11-08 — Restricted vertical slice and first verification

- Added canonical strict Pydantic plan/parser, duplicate-key/depth/size limits, exact fixture path/operation/synthetic-value policy, deterministic smoke planner, 5 good/seeded fixture pairs, and independently handwritten browser reference checks.
- Added SQLAlchemy records, frozen reversible Alembic initial migration, local durable job/slot admission, idempotency, finite transitions, conservative interruption handling, cancellation, artifact hashes/TTL/quota, append-only reviews, authenticated FastAPI and OpenAPI exports.
- Added network-disabled unshare/bubblewrap browser supervisor: clean environment, minimal readonly mounts, Chromium sandbox enabled, CPU/file/time/output limits, 256 MiB tmpfs, 1 GiB RSS/64-process polling watchdog. No cgroup hard limits claimed.
- Isolated Chromium 149.0.7827.55 probe passed outside Codex syscall sandbox. Direct loopback/metadata/private/public/IPv6 connections denied; private home absent. Browser off-origin navigation negatives and cancellation teardown passed.
- First regression run: 53 unit/API/lifecycle tests passed, followed by 5 real browser/security/workflow tests. Full suite after reversible migration test: **59 passed in 28.17s**.
- Next.js 16.4.5 / React 19.3.1 dashboard implemented. TypeScript and ESLint passed; frontend status test passed. Turbopack build failed on blocked local IPC; supported webpack build passed outside Codex sandbox. No security control disabled.
- Dashboard E2E passed with temporary loopback services and disposable synthetic credentials: login, project creation, run, actual worker, reproduced finding, evidence previews, mobile-width check, blocked premature acceptance. Inspected desktop/mobile screenshots. Test services terminated afterward.
- Earlier failed checks: sandboxed AnyIO TestClient hung in thread portal; isolated Chromium was blocked by syscall policy. Reruns outside Codex sandbox passed with application browser restrictions intact. E2E initially found a missing virtualenv uvicorn entrypoint and an ambiguous test locator; corrected to python -m uvicorn and scoped navigation locator, then passed.
- Fixed 30-trial development benchmark ran all ten handwritten reference checks first. 30/30 valid plans, 153/153 attempted steps completed, 5/5 seeded families reproduced, 0/15 control claims, 15/15 reproductions and complete capture descriptors. Median trial latency 5.318s. Raw counters in evaluation/results/latest.json. No live provider calls. Human oracle review pending: zero machine-verified/human-confirmed evaluation claims; precision on those axes N/A.
- Baseline user documentation recorded separately in local commit 818d9fa. New implementation remains under review; no remote push.
- Remaining: finish source modularization/docs and final regression. PostgreSQL/Redis/RQ integration, networked fixture supervision, live provider adapter/spend policy, cgroup hardening and independent human oracle review remain incomplete.

## 2026-11-08 — Final-review race found and corrected

- After minimal runner mount changes, 59 tests passed in 35.54s and the modularized dashboard production build/E2E passed.
- A subsequent final benchmark attempt aborted during reference checks: child exit raced /proc status reading and raised ProcessLookupError in the resource watchdog. No final-trial results were produced by that attempt. Its failure is recorded in evaluation/results/interrupted-evaluation.json; unknown partial reference counts are explicitly null, not reconstructed. The earlier completed benchmark is preserved in initial-baseline.json.
- Corrected only the vanished-process exception handling (permission errors still fail closed), added a focused regression, and made the evaluation persist incremental reference/error records before trial execution. Final rerun pending; no new score claimed yet.
- Terminated three task-owned pytest processes left hung by the earlier Codex-sandbox AnyIO issue. Temporary dashboard services were stopped by their test harness.

## 2026-11-08 — Regression closure and delivery preparation

- Watchdog race regression: full suite **60 passed in 28.90s**, committed as 09312cb.
- Added structured 503 storage-unavailable handling and immutable oracle-source seeding checks. Full suite **61 passed in 30.39s**, committed as cbd2a9f. No tests skipped in that run.
- Corrected seeding to require migrations rather than create an unversioned schema. The empty development DB created by this session had zero projects/runs and no schema differences; stamped its matching initial migration after verifying equality. Fresh migration → seed commands executed successfully.
- New setup README, Fedora onboarding, actual API differences, security/control status, implementation matrix and four-minute demo distinguish implemented/tested/partial/planned work. Original archive hashes still match all 16 source records. Historical design docs now link current implementation status without implying their full hardened contracts have shipped.
- Final benchmark is running against committed backend cbd2a9f with source hashes. A fresh isolated virtualenv setup/check is also running to verify the lock does not rely on preinstalled global packages. No final values asserted before completion.

## 2026-11-09 — Final verified restricted demo

- Final completed benchmark on frozen backend cbd2a9f: 30/30 valid and accepted plans, 153/153 completed attempted safe steps (including reproductions), 5/5 seeded families reproduced, 0/15 control-trial flags, 15/15 reproductions and complete capture descriptors. Median 5.261 seconds; total including ten independent reference checks 187.437 seconds. Raw source hashes/counters and the earlier failed attempt are preserved. No live LLM was invoked. Actual human oracle review remains pending; verified/confirmed claims stay zero, precision N/A on those axes.
- Fresh user-owned virtualenv installed all 32 locked packages and the editable project from README commands. Unit/API subset: **55 passed in 1.29s**, one unsuppressed Starlette/httpx deprecation warning. No global package dependency was needed.
- Final lifecycle review found that an in-memory cancellation check alone could race a queued claim/completion write. Replaced those writes with SQL compare-and-swap predicates and atomic cancellation updates, including authorization revocation. Added stale-claim, stale-completion and completion-first regressions. Full latest suite: **64 passed in 29.95s**, no skipped tests. These changes do not alter the renderer/planner/policy or the measured fixture scoring; benchmark snapshot attribution remains cbd2a9f.
- Frontend production build (webpack), strict TypeScript, ESLint, Prettier and status test passed. Modularized dashboard E2E passed with actual API/worker execution and desktop/mobile/evidence screenshots; inspected rendered screenshots, including both failed-assertion previews. All E2E-owned services stopped afterward.
- Full hardened MVP is not declared complete: PostgreSQL/Redis/RQ/outbox/distributed fencing, live provider adapter/spending policy, cgroup hard limits/complete networked-target isolation matrix, independent human oracle review and public-deployment assessment are unfinished. No push, publication, deployment, sudo/system package installation or global security change occurred.
- Next reviewer action: follow README, start scripts/dev.sh, inspect the synthetic good/seeded runs and independently review an oracle if desired. Next engineering milestone: provision and verify intended Postgres/RQ/supervisor infrastructure while preserving this closed fixture mode.

## 2026-11-09 — Resumed closeout after interruption

- Verified that both pending commits completed before interruption: 17e1b31 (atomic cancellation fencing) and c9b241e (dashboard/setup/measured delivery). The working tree was clean on resume.
- Exercised the actual documented `scripts/dev.sh`: migration/seed succeeded, isolated worker and Next.js dashboard became ready, and SIGTERM cleanup stopped both loopback ports. Private `.env` was created by the documented helper, is Git-ignored and has mode 0600; no credential values were printed or committed.
- Next dev generated apps/web/AGENTS.md and changed next-env.d.ts. Read its scoped framework guidance and the installed Next.js TypeScript/CLI documentation. Preserved generated framework instructions, excluded the managed type file from Git, and changed typecheck to `next typegen && tsc --noEmit` so clean checkouts generate required types independently.
- Updated typecheck, ESLint, Prettier check and shell syntax verification passed. Backend source and measured fixture pipeline are unchanged by this closeout.

## 2026-11-09 — Real PostgreSQL integration

- Rechecked Podman outside Codex's restricted runtime mount: rootless mode works. The earlier read-only /run/user failure was tool-sandbox-specific, not a host blocker. Corrected documentation with ADR-013; no system configuration/security change was needed.
- Downloaded official PostgreSQL 17, recorded/pinned its immutable digest, and built scripts/check_postgres.py. It owns a generated rootless container, publishes a random loopback port, uses tmpfs/read-only root with configured CPU/memory/PID limits, and removes its container/test data afterward. It does not alter .env or persistent application data.
- Test stores now optionally use explicit TESTPILOT_TEST_DATABASE_URL with one generated schema per test; setup/teardown drop only that schema. Default remains SQLite. PostgreSQL-only checks skip explicitly without the test variable.
- First full real PostgreSQL 17.11 run: **66 passed in 35.25s**. Added real concurrent admission/claim checks and migration/metadata drift checks; second run: **68 passed in 35.51s**, no skips. Both temporary containers were removed after testing.
- Updated backend capability text and implementation/setup/security documentation: the implemented initial PostgreSQL schema and fixture runtime are verified; the full normative model, Redis/RQ/outbox/distributed fencing and hardened deployment remain incomplete. Browser isolation and deterministic benchmark claims are unchanged.
- Final regression now includes an explicit PostgreSQL CHECK-constraint rejection assertion; final SQLite/PostgreSQL reruns pending below.
- Final verification: PostgreSQL **68 passed in 41.46s**, zero skips; SQLite **64 passed, 4 PostgreSQL-only skips in 35.13s**. Ruff lint/format and git whitespace checks passed. The PostgreSQL container was removed after testing. Image/version/commands/results/source hashes are recorded in docs/verification/2026-11-09-postgresql.json.
- This closes the “PostgreSQL adapter unverified” gap for the implemented initial schema. It does not close the full database model or Redis/RQ/outbox/distributed-fencing milestones. No live provider call, browser-policy expansion or deployment occurred.

## 2026-11-09 — Transactional Redis/RQ delivery

- Added migration 0002 and OutboxEvent. Admission commits run/job/outbox/idempotency together; existing queued jobs are backfilled. Queued cancellation suppresses delivery. Local mode remains explicit and unchanged by default.
- Added RQ 3.0.0 / redis-py 8.1.0, updated the complete 37-package Python lock. The producer uses RQ JSON serialization; the restricted consumer bounds compressed/plain JSON, validates one fixed marker and exact job/generation, and never calls Job.fetch/perform, pickle or queue-selected callbacks/imports.
- Dispatch reconciles lost acknowledgments and missing Redis data, retries with bounded backoff clamped to the original queue deadline, rejects old generations, and never replays active/terminal work. Worker liveness/cleanup failure now stops the loop. Redis configuration requires authentication and rejects URL timeout overrides.
- Extended the pinned rootless test harness with authenticated Redis 7.4.12 and owned-process/container cleanup; browser network isolation is unchanged. Added rollback/backfill, outage, lost ack/data, hostile payload, foreground worker, actual Redis restart, and cleanup failure regressions.
- Executed intermediate combined suites: 80 passed in 41.79s; then 82 passed in 52.29s (including foreground worker and actual Redis restart); then 84 passed in 62.61s. Default SQLite regression at that stage: 73 passed, 11 service-only tests skipped in 42.23s. Final cleanup/configuration regressions added afterward; final results pending below.
- This implements single-host delivery, not distributed RQ worker supervision or the full lease/epoch/signed-capability protocol. Exactly-once browser side effects are not claimed. No live provider call, public deployment or existing .env change occurred.
- Final combined PostgreSQL/Redis suite: **90 passed in 62.20s**, zero skips. Default SQLite/local suite: **79 passed, 11 service-only skips in 42.87s**. TypeScript type generation/check, frontend ESLint/status test, Python Ruff lint/format and whitespace checks passed. Verification commands, service/image versions, counters and source hashes are preserved in docs/verification/2026-11-09-rq-outbox.json. Both temporary services were removed by the runner.
- Next boundary: distributed leases/epochs and signed supervisor capabilities, full schema ownership constraints, cgroup/complete isolation release matrix and a configured bounded live provider adapter. The existing deterministic evaluation remains historical and unchanged; this stage adds delivery reliability evidence, not LLM accuracy claims.
