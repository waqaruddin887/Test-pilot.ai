# HTTP API v1 baseline

Accepted 2026-11-08; routes use `/api` for the local v1 prototype. Future breaking HTTP revisions require explicit versioning, not silent field changes. All requests require the configured operator session/credential and all objects are scoped to that operator; unowned IDs return 404. Browser mutations require exact trusted Origin/Host and CSRF. Bodies are strict JSON with extra properties rejected, max 64 KiB. Lists use opaque cursor, default 20 and max 100 items; return `{items, next_cursor}` with stable `(created_at,id)` ordering.

## Resources

| Method / route | Body or query | Result |
| --- | --- | --- |
| GET /api/health | none | 200 liveness, no sensitive configuration |
| GET /api/ready | none | 200 ready or 503 with named unavailable capabilities, no secrets |
| POST /api/projects | name (1–120), fixture_authorization_ref | 201 project_id/name/fixture_id; bind only preconfigured authorization owned by operator |
| GET /api/projects | cursor, limit | project list with latest-run summary |
| GET /api/projects/{id} | none | project and active authorization summary |
| GET /api/projects/{id}/authorizations | cursor, limit | immutable revisions, paths, operations, expiry/revocation and evidence reference; no permission evidence bytes |
| POST /api/authorizations/{id}/revoke | reason (1–1000) | 200 revoked_at, active-run stop requested; idempotent, cannot expand scope |
| POST /api/runs | project_id UUID, target_path (max 2048), objective (1–1000), max_cases (1–5, default 3), mode planned/smoke (default planned) | 202 run_id/state=queued/created_at/idempotency_expires_at; requires Idempotency-Key |
| GET /api/runs | optional project_id, cursor, limit | run history, state and safe outcome counts |
| GET /api/runs/{id} | none | run/state/reason/provenance/summary/cancel_requested_at/event_sequence; counts separate machine assessment and review |
| GET /api/runs/{id}/events | after_sequence, limit | bounded ordered stage events for polling |
| GET /api/runs/{id}/cases | cursor, limit | cases, ordered plan steps, attempt summaries and per-step outcomes |
| GET /api/runs/{id}/findings | cursor, limit | machine assessment, latest review, derived current confirmation, oracle/evidence/reproduction availability |
| GET /api/oracle-versions/{id} | none | public versioned requirement, expected assertion, provenance/severity; never benchmark labels |
| GET /api/findings/{id}/reviews | cursor, limit | append-only decisions and evidence-manifest hashes |
| POST /api/findings/{id}/reviews | decision accepted/dismissed/unreviewed, expected_review_sequence, reason (1–1000), manifest_id nullable, inspected_manifest_sha256 nullable | 201 appended review; acceptance requires nonnull current manifest/hash and all verification/evidence gates; 409 on stale sequence |
| GET /api/artifacts/{id} | none | private safe download after ownership/expiry/integrity check; 410 expired/deleted, 409 quarantined, safe error on corruption |
| POST /api/runs/{id}/cancel | empty object | 202 cancel requested, or 200 unchanged terminal with already_terminal=true; idempotent |
| POST /api/runs/{id}/rerun | empty object | 202 new linked run from same goal/path/mode/count, current authorization and limits; requires Idempotency-Key; never modifies source |

Authorization creation/revision and provider configuration are local operator setup operations, not permissive web endpoints. The UI selects from existing authorization revisions; unknown refs return 403. Revocation through the UI can only reduce authority. Reviews do not trigger reproduction; reproduction is part of verifying stage, bounded to one per candidate. Rerun initiates new testing with a new budget and fresh fixture state.

Exact response DTOs must be generated from Pydantic when application development begins; required fields and behavior above are selected now. HTTP uses snake_case JSON fields, UUID strings, UTC RFC3339 timestamps and stable enums from normative contracts. Job deadlines, state transitions, admission availability and idempotency semantics are defined in [jobs](../architecture/job-lifecycle.md). No 202 response until run/outbox commit succeeds; missing capable worker returns 503 with no queued run. Basic run history is included; export/comparison/replay automation is deferred.

## Errors, sessions and evidence

Errors: `{code, message, run_id, safe_details}` where run_id is nullable, safe_details is a bounded typed object, and no stack trace/page HTML/secrets are returned. Use 401 missing/invalid session, 403 unauthorized target/operation/CSRF, 404 unknown/unowned resource, 409 stale review/invalid transition/idempotency conflict, 410 expired artifact, 422 structural/semantic request error, 429 spend/quota/rate limit and 503 absent worker/provider or unhealthy required infrastructure. Structural model plan failures are recorded as run errors after admission, not a retroactive HTTP admission error.

Bootstrap/session issuance is through trusted local setup; no public registration/login flow is introduced. Use session-token hashes and eight-hour expiry. Operator changes or revocation invalidate sessions; protect local secrets in untracked configuration. Same-origin web-to-API proxy avoids duplicate backend business logic; no wildcard CORS. No settings route may increase baseline safety caps or approve external targets.

Artifacts use server-controlled MIME and Content-Disposition=attachment, `nosniff`, private no-store cache policy, no arbitrary path parameters or inline active content. Recheck availability/expiry while opening the object. EvidenceViewer shows safe screenshots and textual provenance; trace access is a safe download or isolated viewer, not arbitrary archive execution. Acceptance checks oracle, manifest and availability transactionally, and later expiry changes the displayed availability without rewriting historical review.
