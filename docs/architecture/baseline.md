# Technical baseline v0.2

> Current local implementation uses the narrower [offline fixture development mode](../decisions/012-offline-fixture-development.md). See [implemented/tested/partial/planned status](../implementation-status.md); the full architecture and release gates below remain the intended hardened target.
Decision date: 2026-11-08. Accepted engineering design under the requested contradiction-resolution work; not a signed charter, deployed control, or completed implementation. [Readiness](../implementation-readiness.md) records unfulfilled gates.

## Product and scope

Preserve the local-first AI-assisted browser tester: discover UI, propose meaningful finite tests, execute deterministically, collect evidence, reproduce requirement-backed failures, and present them for human review. Next.js/TypeScript/Tailwind, Python/FastAPI/Pydantic, Python Playwright/Chromium, PostgreSQL, Redis/RQ and Docker Compose remain the stack. One operator and one active run initially. Basic run history is P0; comparison, export, scheduling and CI integration are deferred. No RAG, fine-tuning, arbitrary generated code, production authentication, real personal data, payments or third-party testing.

The MVP target is an explicitly authorized, developer-controlled container fixture, not arbitrary local/staging URLs. Synthetic login rejection and cart arithmetic are simulations without real credentials, session persistence, checkout or payment. Each fixture mutation is preauthorized in its operation manifest. Human approval cannot expand this scope at runtime.

## Normative specifications

- [Plan contract](../contracts/test-plan-v1.md): sole Pydantic/JSON format and contextual validation rules.
- [Safety and authorization](safety-policy.md): single policy across UI/API/planner/runner.
- [Findings and evaluation](findings-and-evaluation.md): observations, machine verification, human review and scoring.
- [Data model](data-model.md): entity fields, relationships and invariants.
- [Runner protocol](runner-protocol.md): topology, privileges and command boundary.
- [Jobs](job-lifecycle.md): acceptance, dispatch, fencing, retries, cancellation and recovery.

If a conflict remains, fail closed and record it; do not let a less restrictive example override a normative contract. Foundational documents summarize these specifications. ADR changes must update both contracts and affected summaries in the same change. Archives and the original review describe previous states only.

## Repository architecture

```text
apps/web/                         Next.js app and accessible operator UI
packages/api-client/              generated TypeScript API client
packages/contracts/               generated OpenAPI / plan-schema exports
backend/src/testpilot/
  api/ contracts/                 HTTP routes, DTOs and strict Pydantic plans
  domain/ application/            state machines, use cases, budgets and ports
  policy/                         URL/action authorization, minimization/redaction
  persistence/ jobs/              SQLAlchemy, outbox, RQ, leases/reconciliation
  planner/                        provider adapter and versioned prompt assembly
  runner/ browser/                trusted client / isolated Playwright process
  verification/ reporting/        independent oracle checker / deterministic report
  artifacts/ observability/       private evidence and safe logs/metrics
backend/migrations/ tests/         Alembic revisions and Python tests
fixtures/site/ requirements/      synthetic fixtures and public oracle specs
fixtures/reference-tests/         independent harness-only reference assertions
evaluation/manifests/ scoring/    frozen benchmark protocol and raw counters
evaluation/private-labels/        harness-only expected detection and defect IDs
tests/e2e/ security/              cross-component tests and negative controls
infra/docker/ network/            images and explicit isolation rules
infra/compose.yaml                local services and one-shot migrations
scripts/                          reproducible developer/check commands
docs/foundations/ architecture/ contracts/ adr/ reviews/ archive/
```

One Python distribution and dependency lock, with separate service install groups/images; one pnpm workspace and JS lock. No application directories/manifests are created by this documentation pass. SQLAlchemy/Alembic are selected persistence tools; compatible exact runtime/driver versions remain a setup gate. Pydantic owns API/plan definitions; generated OpenAPI supplies transport types, not domain or ORM models. A model-output schema is distinct from an authorized execution capability.

## Fixed initial limits

Limits can be reduced per run. Raising these ceilings requires a dated baseline change and regression checks; the planner never changes them.

| Resource | v0.2 ceiling/default |
| --- | --- |
| Cases / ordered steps | 1–5 cases, default 3; 1–12 steps per case including assertions |
| Queue wait | 120 seconds from acceptance; unavailable capable worker rejects admission |
| Active run | 300 seconds from lease claim, including discovery, planning, repair, execution and reproduction |
| Cleanup / cancel grace | 5 seconds, then supervisor terminates runner process group/container |
| Navigation / other step | 30 seconds / 10 seconds; step timeout 1–30,000 ms, clamped to remaining deadline and action ceiling |
| Planner | 30 seconds per request, at most 2 requests total (one schema repair); no automatic provider transport retries |
| Model token limits | At most 8,000 request tokens and 2,000 completion tokens per call; total reservation accounts for both calls |
| Reproduction | At most one clean reproduction per candidate case; reuse same sequence and oracle versions |
| Discovery | One page, no crawl; 500 outline nodes, 32 KiB UTF-8 text, 64 KiB sanitized input envelope |
| Protocol payloads | 256 KiB command/result JSON, artifact bytes streamed separately |
| Artifacts | At most 20 screenshots and 100 MiB total artifacts per run, one trace per attempt |
| Retention | Artifact bytes 24 hours; metadata/reviews/logs 7 days; no automatic export or backup |
| Initial runner | 1 CPU, 1 GiB RAM, 256 PIDs, 256 MiB tmpfs; verify adequacy before browser use |
| Local storage | 1 GiB artifact store; reserve run quota before starting, reject when unavailable |

Provider/model, provider-specific token counting, price schedule and monetary daily/per-run caps must be supplied before live calls; absent configuration disables live planning. Reserve the worst-case two-call cost atomically, then reconcile actual usage; unknown provider usage retains reservation rather than guessing zero. The model, prompt, schema, oracle, policy, fixture and browser/image versions/hashes are captured per run.

## Day 1 delivery semantics

API/UI may create a persisted run only if a matching capable worker is healthy and the fixture authorization is active. Until execution exists, run admission returns 503 `worker_unavailable`; the UI clearly explains this. No placeholder worker consumes runs or fabricates completion. Day 1's original full run-creation acceptance stays incomplete until this path exists. Project configuration, validation, persistence, health and honest error handling can be implemented first. A fixture-only deterministic smoke mode is an explicit operator-selected mode on a new run, not a silent fallback from a failed planner.

Security and evaluation checklists are gates requiring recorded tests. Accepting this design does not mark any gate passed or authorize system-level changes.
