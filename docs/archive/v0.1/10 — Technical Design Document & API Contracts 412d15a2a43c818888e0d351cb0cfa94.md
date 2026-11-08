# 10 — Technical Design Document & API Contracts

**Draft v0.1. API shapes and SQL structures are proposed, not implemented.**

## Primary entities

Project(id UUID, name, approved_origin, created_at); Run(id UUID, project_id FK, target_path, objective, state, model_version, prompt_version, created_at, started_at, ended_at); Case(id UUID, run_id FK, title, plan_json, state); Step(id UUID, case_id FK, sequence, action_json, actual_json, status, duration_ms); Finding(id UUID, run_id FK, case_id FK, oracle_ref nullable, status, severity, evidence_summary, reproduced_count); Artifact(id UUID, run_id FK, step_id nullable, kind, storage_key, sha256, expires_at). Add migrations, foreign keys, indexes on project_id/run_id and event timestamps. Restrict artifact access to its owning run.

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
{"project_id":"uuid","target_path":"/form","objective":"Check required email validation","max_cases":5}
```

```json
{"run_id":"uuid","state":"queued","created_at":"2026-11-08T00:00:00Z"}
```

Errors follow a stable shape: code, message, run_id optional, safe_details. Use HTTP 422 for schema issues, 403 for unauthorized target, 409 for invalid transitions, 429 for budgets, 503 for unavailable planner/worker. Avoid exposing stack traces.

## Authentication and access

For local-only single-user MVP, bind services to [localhost](http://localhost) and protect developer configuration; do not claim enterprise authentication. Before deployment: OIDC or session auth, role-separated projects, CSRF defenses for cookie sessions, authorization on every run/artifact, request rate limiting and audit records.

## Runtime interfaces

Planner returns versioned typed cases, not code. Executor accepts only validated steps and an immutable policy object. OracleVerifier consumes independent requirement data. Reporter consumes sanitized evidence and cannot edit raw outcomes.

## Integrity and validation

Idempotency key on POST /runs; bounded payload length; reject unsupported URLs, path traversal and arbitrary action types; encrypt/limit secret configuration; checksum traces and screenshots; signed or server-controlled artifact download. Define migration rollback and retry behavior.

## Tests to author

API schema tests, unauthorized cross-project request, state-transition tests, malformed action refusal, cancellation, rerun idempotency, artifact expiry, allowed-origin redirect rejection.