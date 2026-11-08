# ADR-004: Separate HTTP handling from queued work

Status: Accepted technical baseline, 2026-11-08. Implementation pending.

## Context

Long browser operations must not own HTTP lifetimes.

## Decision

Keep FastAPI request handling separate from one trusted Redis/RQ orchestrator. Postgres is authoritative and a capable-worker heartbeat gates run admission. Worker does not run a browser in its privileged namespace.

## Alternatives considered

Inline HTTP execution and a fake worker marking runs successful are rejected.

## Consequences and verification

Day 1 can expose honest unavailability; original full run-creation acceptance remains incomplete until a real capable path exists. See the [normative specification](../architecture/job-lifecycle.md) and [readiness gates](../implementation-readiness.md) for implementation requirements and evidence still needed.

This decision supersedes conflicting v0.1 wording; it does not claim controls have been implemented or tested.
