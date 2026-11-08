# ADR-002: Local-first controlled fixtures

Status: Accepted technical baseline, 2026-11-08. Implementation pending.

## Context

Authorized local/staging product aspirations exceed the initial safety evidence and seven-day scope.

## Decision

MVP permits only operator-authorized isolated synthetic fixtures. One to five cases, default three. Simulated login/cart fixtures cannot use real authentication or checkout. Known good/broken pairs remain the benchmark.

## Alternatives considered

Arbitrary public targets and broad localhost/private-range permissions are rejected.

## Consequences and verification

External deployment and real applications require a separate scope/security/permission assessment; no runtime approval bypass. See the [normative specification](../architecture/safety-policy.md) and [readiness gates](../implementation-readiness.md) for implementation requirements and evidence still needed.

This decision supersedes conflicting v0.1 wording; it does not claim controls have been implemented or tested.
