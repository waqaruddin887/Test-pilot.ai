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
