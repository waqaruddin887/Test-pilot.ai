# ADR-007: Idempotency, transactional outbox and fenced leases

Status: Accepted technical baseline, 2026-11-08. Implementation pending.

## Context

Postgres commits and Redis enqueue are not one transaction; delivery/crash races can duplicate side effects.

## Decision

Commit run/job/idempotency/outbox together, use deterministic delivery IDs, DB leases with epochs and supervisor command receipts. Retry delivery before side effects; fail interrupted on uncertain execution. Cancel durably, enforce watchdog teardown, reconcile every five seconds.

Clarification, 2026-11-08: explicitly model ExecutionSlot, WorkerCapability and JobCommand for the global lease, compatible heartbeat and pre-send command intent. A recovered claim retains the original active deadline and budget/call limits; it cannot extend execution time. Persisted intent without a reply is uncertain, not proof that a side effect did not occur.

## Alternatives considered

Exactly-once external side-effect claims and blind mutation replay are rejected.

## Consequences and verification

Additional state and fault-injection tests are required; a user rerun creates linked new evidence and budget. See the [normative specification](../architecture/job-lifecycle.md) and [readiness gates](../implementation-readiness.md) for implementation requirements and evidence still needed.

This decision supersedes conflicting v0.1 wording; it does not claim controls have been implemented or tested.
