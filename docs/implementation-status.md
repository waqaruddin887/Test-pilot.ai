# Current implementation status

Updated: 2026-11-09. The supplied v0.2 documentation remains the intended hardened
architecture. [ADR-012](decisions/012-offline-fixture-development.md) defines a
narrower, local offline implementation. This page supersedes **implementation
status** statements in the earlier documentation-only reviews, not their design
requirements. The full hardened MVP is **incomplete**.

| Capability | State | Executed evidence |
| --- | --- | --- |
| Canonical plan 1.0.0 | Implemented/tested | strict Pydantic, parser/schema drift, negative contract/policy suite |
| Project authorization | Implemented for built-in fixtures | API rejects arbitrary origins, invalid paths, revoked/expired authorization |
| Persistence/migrations | Implemented/tested on SQLite | fresh upgrade, rollback, reapply, FK/unique constraints, durable job/run/idempotency |
| PostgreSQL | Implemented initial schema/runtime integration-tested | PostgreSQL 17.11 in pinned rootless temporary container; migrations, constraints, API/lifecycle and real browser/evidence suite |
| Redis/RQ/outbox | Implemented for one foreground host | fixed JSON notifications, transactional admission, backfill, outage/lost-ack/restart tests and real browser execution |
| Distributed leases/fencing | Planned | no claim of distributed delivery/execution safety |
| Discovery | Implemented/tested, one fixture page | title/path, bounded roles/names/visible text |
| Planner | Explicit deterministic smoke implemented/tested | 30 valid fixture plans; zero live-provider calls |
| Hosted provider adapter/quotas | Deferred | provider/model/terms/cost caps unresolved |
| Playwright executor | Implemented/tested in offline sandbox | navigate/click/fill/visible/URL; exact locators, schema/policy revalidation |
| Browser isolation | Restricted mode tested | network/socket denial, minimal mounts, Chromium sandbox, resource watchdog, cancellation |
| Full production resource/isolation matrix | Partial | cgroup hard limits, networked target firewall and complete bypass/fault matrix unfinished |
| Independent fixture expectations | Authored/reference-checked | five good/seeded pairs, ten handwritten browser checks |
| Reproduction/evidence | Implemented/tested | fresh context/process/static reset, both screenshots/traces, hash/TTL/manifest |
| Machine/human separation | Implemented/tested | pending oracle review → suspected; reviewed oracle + clean reproduction → verified; acceptance additionally needs current evidence |
| Actual human review | Pending | no human-confirmed benchmark claim |
| API/dashboard | Implemented/tested | projects, run creation/progress/history/results, finding/evidence/review, configuration |
| Frontend accessibility | Basic implementation + limited tests | labels, keyboard controls/focus/skip link, text status, 390px no-overflow check; no independent WCAG audit |
| Evaluation | Development deterministic baseline executed | frozen shuffled 30-trial set, raw counters/errors/source hashes; no held-out/general accuracy claim |

Implementation lives in `backend/src/testpilot/`, `apps/web/`, `fixtures/`, `scripts/`
and `tests/`. See [README](../README.md) for exact commands and [progress](progress.md)
for executed results/failures. The UI E2E test uses disposable credentials/data and
stops all processes; normal runtime is started explicitly by the reviewer.

Requirements traceability:

| SRS | Implementation / test | Coverage |
| --- | --- | --- |
| FR01–02 | api.py/policy.py; test_api.py/test_contracts.py/test_browser.py | built-in offline fixtures only |
| FR03 | browser.py discover; fixed benchmark / dashboard E2E | selected accessible outline, not general crawler |
| FR04–06 | contracts.py/planner.py/policy.py/browser.py; unit/security/evaluation | deterministic finite fixture plans |
| FR07 | worker.py/domain.py; test_browser_workflow.py | screenshots/traces/step observations; console metadata deferred |
| FR08–10 | domain.py/api.py; workflow test and finding UI E2E | separate provenance/reproduction/review/current evidence |
| FR11 | isolation.py/worker.py; lifecycle and browser cancellation tests | local one-worker process lifecycle; distributed fault matrix deferred |
| FR12 | minimal clean runner inputs and static fake fixture data | no live LLM request/redaction test or generic trace sanitation claim |

Next engineering milestone: retain this demo unchanged while implementing and
extending the initial PostgreSQL schema and implementing distributed fencing/supervisor capabilities and cgroup-bounded
supervision on an explicitly provisioned host. Independent human oracle review is
needed for non-provisional verified findings. Live provider work requires explicit
model/terms/token/monetary-cap decisions before any paid request. External targets
remain outside the MVP.

PostgreSQL verification details: [2026-11-09 evidence](verification/2026-11-09-postgresql.json).
Final real database run: 68 passed, no skips. Default SQLite run: 64 passed with
four explicitly skipped PostgreSQL-only checks. Both use the same application
contracts; PostgreSQL tests additionally exercise real constraints, migration
schema drift and concurrent admission/claim behavior.

Redis/RQ verification: [2026-11-09 outbox evidence](verification/2026-11-09-rq-outbox.json).
The final combined PostgreSQL/Redis run passed 90 tests with no skips. The default
run passed 79, explicitly skipping 11 external-service checks. This verifies only
the documented single-host restricted consumer, not generic/distributed RQ workers.
