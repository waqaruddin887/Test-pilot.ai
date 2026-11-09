# Implemented API reference

Production Pydantic request/response schemas are exported to
`packages/contracts/openapi.json`; generated TypeScript is `packages/contracts/api.d.ts`.
The strict plan is `testpilot.contracts.TestPlan`, schema version 1.0.0. Run
`scripts/export_contracts.py` and `pnpm contracts` after contract changes.

`docs/contracts/http-api-v1.md` remains the intended full baseline. The current
restricted implementation provides:

| Resource | Implemented routes |
| --- | --- |
| Health/capability | GET /api/health, /api/ready, /api/settings |
| Local session | POST /api/session/bootstrap |
| Projects | GET/POST /api/projects; GET /api/projects/{id} |
| Reduced authority | POST /api/authorizations/{id}/revoke with {} |
| Runs | GET/POST /api/runs; GET /api/runs/{id} |
| Control | POST /api/runs/{id}/cancel and /rerun with {} |
| Findings | GET /api/runs/{id}/findings; GET /api/findings/{id} |
| Human review | POST /api/findings/{id}/reviews |
| Independent oracles | GET /api/oracles; POST /api/oracles/{ref}/review |
| Evidence | GET /api/artifacts/{id}, safe authenticated attachment |

Use the OpenAPI reference for exact body fields. Project creation selects only
`synthetic-control-v1` or `synthetic-seeded-v1`, never a submitted URL. POST /runs
requires Idempotency-Key; same key/body returns the existing run, changed body
conflicts. Explicit `mode=smoke` is required; `planned` returns 503. Admission checks
current compatible worker heartbeat, unexpired/unrevoked authorization, source hash
and one-run capacity. Job and idempotency rows commit with the run.

Local operator browser access uses HttpOnly SameSite=Strict cookie, session-token
hashes, an eight-hour expiry, exact Origin/Host checks and CSRF header. CLI access
uses a separate configured bearer credential of at least 32 characters. There is
one operator, no multi-tenant identity or cross-operator security claim.

Errors use code/message/run_id/safe_details. Payloads are bounded to 64 KiB; input
DTOs reject extra fields. Untrusted origin/target is 403; no worker/planner is 503;
concurrency/idempotency/review conflict is 409; expired artifact is 410. Artifacts
are addressed by generated ID, never paths, and checked for expiry/hash before
serving with attachment/nosniff/private no-store headers.

Current deliberate differences from the full baseline: UTC epoch seconds rather
than RFC3339 transport timestamps, latest 100 rows rather than cursor pagination,
embedded cases/attempts/events in run detail, single-host delivery rather than distributed supervision,
no distributed lease/capability protocol, and no live planner usage/budget records.
Review responses and settings contain some dictionary fields; core project/run/
finding transport DTOs are generated. These are prototype interfaces, not a claim
that every normative v0.2 endpoint/entity has shipped.

Run admission now also commits an outbox row transactionally. The same API supports
explicit local polling or Redis/RQ JSON notification delivery; Redis outages do not
undo committed runs. Delivery degradation/restoration appear as additional textual
run events. No endpoint can configure arbitrary queued callbacks or executable code.
