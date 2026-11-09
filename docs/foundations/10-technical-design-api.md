# 10 — Technical Design Document & API Contracts

**Technical baseline v0.2 — 8 November 2026. Design selected. See [current implementation and test evidence](../implementation-status.md); the full hardened design is not yet complete. Commercial charter/legal approval is not implied.**

## Primary entities

The [final logical database model](../architecture/data-model.md) defines Operator/Session, Project, versioned Authorization/Paths/Operations, Oracle/OracleVersion, Run/Case/PlanStep, ExecutionJob/ExecutionSlot/WorkerCapability/JobCommand/Attempt/StepResult, Finding, Artifact/Manifest, Review, RunEvent, OutboxEvent, IdempotencyRecord and budget/provider usage. Separate step definitions from attempt outcomes and human decisions from machine assessment. Use UUIDs, UTC timestamps, relational ownership constraints, explicit state transitions and indexes. A restricted SQLite initial migration is implemented/tested; the full PostgreSQL schema remains pending (see current implementation status).

## State machine

queued → discovering → planning → executing → verifying → completed. Failed/cancelled terminal; no direct transition from completed to executing. A rerun creates a new linked run; do not overwrite original evidence.

## API

| Method | Route | Purpose |
| --- | --- | --- |
| POST | /api/projects | Create approved project after origin validation |
| POST | /api/runs | Start run for existing project |
| GET | /api/runs/{id} | State and summary |
| GET | /api/runs/{id}/cases | Cases and steps |
| GET | /api/runs/{id}/findings | Findings and oracle source |
| GET | /api/artifacts/{id} | Authorized artifact retrieval |
| POST | /api/runs/{id}/cancel | Cooperative cancel + worker stop |
| POST | /api/runs/{id}/rerun | New run with same approved goal |

## Request/response examples

```json
{"project_id":"11111111-1111-4111-8111-111111111111","target_path":"/form","objective":"Check required email validation","max_cases":3,"mode":"planned"}
```

```json
{"run_id":"22222222-2222-4222-8222-222222222222","state":"queued","created_at":"2026-11-08T00:00:00Z","idempotency_expires_at":"2026-11-15T00:00:00Z"}
```

Errors follow a stable shape: code, message, run_id required but nullable, safe_details. Use HTTP 422 for schema issues, 403 for unauthorized target, 409 for invalid transitions, 429 for budgets, 503 for unavailable planner/worker. Avoid exposing stack traces.

## Authentication and access

For local-only single-operator MVP, publish services on loopback and require the operator session/CSRF/exact Origin/Host controls in the unified safety policy. Project/run/artifact ownership is enforced server-side; no enterprise authentication is claimed. Before external deployment, add the separate identity/role/rate-limit assessment; local sessions, CSRF and ownership checks are already mandatory for MVP.

## Runtime interfaces

Planner returns versioned typed cases, not code. Executor accepts only validated steps and an immutable policy object. OracleVerifier consumes independent requirement data. Reporter consumes sanitized evidence and cannot edit raw outcomes.

## Integrity and validation

Idempotency key on POST /runs; bounded payload length; reject unsupported URLs, path traversal and arbitrary action types; encrypt/limit secret configuration; checksum traces and screenshots; signed or server-controlled artifact download. Migration and retention behavior is specified in the data model; retry and crash behavior in the job lifecycle. Implementation still requires integration tests.

## Tests to author

API schema tests, unauthorized cross-project request, state-transition tests, malformed action refusal, cancellation, rerun idempotency, artifact expiry, allowed-origin redirect rejection.

## v0.2 technical baseline

The table above is a summary, not the entire API. [HTTP API v1](../contracts/http-api-v1.md) includes project lists/detail, authorization references/revocation, run lists, oracle provenance and append-only review actions. Idempotency keys are scoped by operator/operation for seven days; accepted runs use transactional outbox. Reruns create linked new records, review does not modify evidence, and expired artifacts return 410.

Normative details: [baseline](../architecture/baseline.md), [ADRs](../README.md#architecture-decisions), and [implementation readiness](../implementation-readiness.md). Original v0.1 content is preserved in `../archive/v0.1/`; historical targets are not measurements.
