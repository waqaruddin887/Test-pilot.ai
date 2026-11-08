# 09 — System Architecture Document (SAD)

**Technical baseline v0.2 — 8 November 2026. Design selected; implementation and test evidence pending. Commercial charter/legal approval is not implied.**

## Logical components

- Next.js/TypeScript UI: project configuration, run progress and evidence review.
- FastAPI Python API: request validation, origin authorization, run lifecycle and typed results.
- Redis/RQ worker queue: isolates queued execution from HTTP handler; single worker is enough initially.
- Browser runner: isolated non-root Playwright/Chromium namespace with fixture-only egress, supervised through bounded pipes by a separate trusted control process; no provider/DB/Redis keys.
- LLM planner adapter: provider-independent JSON structured requests with timeout and spend cap.
- PostgreSQL: project configuration, test plans, results, findings and artifact metadata.
- Artifact store: local restricted directory during MVP; optional object storage later.

## Dataflow

Browser UI → API → Postgres/queue → worker policy engine → Playwright discovery → sanitized observation → LLM planner → Pydantic validation → executor → oracle verifier → evidence/artifacts → database → UI polling.

## Security zones

UI/API network; database/queue private network; isolated browser worker outbound allowlist; LLM API egress only from planner adapter. Browser should not reach cloud instance metadata, internal services, local admin endpoints or arbitrary RFC1918/loopback IPs. For local test fixtures, explicitly configure an isolated fixture network and allow its service hostname only; never globally permit loopback or private ranges. For MVP, pin the fixture service/address/port in a static run manifest with no general runner DNS; redirects and subresources still require enforcement. Nonlocal DNS resolution/connection-time rebinding defenses remain a separate prerequisite before expanding scope.

## Availability and capacity

Local MVP: one concurrent test worker, capped browser contexts, no SLA. Jobs durable through queue and database state reconciliation. Kill orphaned browser sessions after cancellation or timeout. No horizontal scaling, Kubernetes, GPU, CDN or cloud API gateway required. Runtime versions pinned in lockfiles and Docker images.

## Observability

Per-run structured logs include trace/run ID, stage transition, action ID, provider latency/token counts, browser failures and evidence hashes. Never log cookies, form secrets or full unrestricted HTML. Use health endpoint and run metrics. Separate user-facing explanation from diagnostic error.

## Deployment

Docker Compose for API, worker, Redis, PostgreSQL, web UI, and controlled demo fixture. CI: lint, type checks, Python tests, browser E2E fixtures, dependency scanning, image checks. Apply migrations before startup. Before schema changes, either create an explicitly requested private backup with a defined TTL, or explicitly establish that local development data is disposable; no automatic backup/export is enabled. Follow the data-model recovery policy.

## Recovery

LLM outage → explicit planning failure; smoke is a separate user-selected run mode. Browser crash → mark executor failure and collect partial trace. Queue failure → transactional Postgres outbox retains accepted work; retry dispatch only within queue deadline. Never automatically replay uncertain browser side effects. Disk full → stop artifact capture and report degraded result, never silently declare confirmed defect.

## Architectural decisions

ADR-001: deterministic engine over model-generated code. ADR-002: local-first controlled fixtures. ADR-003: hosted model with no RAG/fine-tune. ADR-004: queue/worker split to manage timeouts. Revisit only based on measured bottlenecks.

## v0.2 technical baseline

The [monorepo baseline](../architecture/baseline.md) retains the stack. [Runner design](../architecture/runner-protocol.md) selects supervised namespace isolation; ordinary Compose bridging is insufficient. Static per-run fixture address/port mapping removes general browser DNS; public DNS/nonlocal support is deferred. [Job lifecycle](../architecture/job-lifecycle.md) specifies outbox, fencing, command receipts, cancellation and recovery. ADR-001–011 record the selected engineering baseline; no control is deployed yet.

Normative details: [baseline](../architecture/baseline.md), [ADRs](../README.md#architecture-decisions), and [implementation readiness](../implementation-readiness.md). Original v0.1 content is preserved in `../archive/v0.1/`; historical targets are not measurements.
