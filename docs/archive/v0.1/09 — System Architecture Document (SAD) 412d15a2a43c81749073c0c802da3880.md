# 09 — System Architecture Document (SAD)

**Draft v0.1 — recommended logical deployment. No infrastructure deployed.**

## Logical components

- Next.js/TypeScript UI: project configuration, run progress and evidence review.
- FastAPI Python API: request validation, origin authorization, run lifecycle and typed results.
- Redis/RQ worker queue: isolates queued execution from HTTP handler; single worker is enough initially.
- Browser worker: containerized Playwright Chromium with non-root user, strict networking and resource limits.
- LLM planner adapter: provider-independent JSON structured requests with timeout and spend cap.
- PostgreSQL: project configuration, test plans, results, findings and artifact metadata.
- Artifact store: local restricted directory during MVP; optional object storage later.

## Dataflow

Browser UI → API → Postgres/queue → worker policy engine → Playwright discovery → sanitized observation → LLM planner → Pydantic validation → executor → oracle verifier → evidence/artifacts → database → UI polling.

## Security zones

UI/API network; database/queue private network; isolated browser worker outbound allowlist; LLM API egress only from planner adapter. Browser should not reach cloud instance metadata, internal services, local admin endpoints or arbitrary RFC1918/loopback IPs. For local test fixtures, explicitly configure an isolated fixture network and allow its service hostname only; never globally permit loopback or private ranges. DNS must be checked at resolution and connection time to mitigate rebinding; redirects and subresources need policy enforcement too.

## Availability and capacity

Local MVP: one concurrent test worker, capped browser contexts, no SLA. Jobs durable through queue and database state reconciliation. Kill orphaned browser sessions after cancellation or timeout. No horizontal scaling, Kubernetes, GPU, CDN or cloud API gateway required. Runtime versions pinned in lockfiles and Docker images.

## Observability

Per-run structured logs include trace/run ID, stage transition, action ID, provider latency/token counts, browser failures and evidence hashes. Never log cookies, form secrets or full unrestricted HTML. Use health endpoint and run metrics. Separate user-facing explanation from diagnostic error.

## Deployment

Docker Compose for API, worker, Redis, PostgreSQL, web UI, and controlled demo fixture. CI: lint, type checks, Python tests, browser E2E fixtures, dependency scanning, image checks. Apply migrations before startup and back up metadata before schema changes.

## Recovery

LLM outage → smoke-only or explicit unavailable state. Browser crash → mark executor failure and collect partial trace. Queue failure → mark run pending/retry with idempotency. Disk full → stop artifact capture and report degraded result, never silently declare confirmed defect.

## Architectural decisions

ADR-001: deterministic engine over model-generated code. ADR-002: local-first controlled fixtures. ADR-003: hosted model with no RAG/fine-tune. ADR-004: queue/worker split to manage timeouts. Revisit only based on measured bottlenecks.