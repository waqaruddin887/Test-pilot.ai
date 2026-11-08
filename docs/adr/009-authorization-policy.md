# ADR-009: Versioned fixture authorization and fail-closed operations

Status: Accepted technical baseline, 2026-11-08. Implementation pending.

## Context

Project creation, approval exceptions and domain checks previously lacked a single authority.

## Decision

Preconfigure operator-approved fixture origins/paths/operations and expiring immutable authorization revisions. Run snapshots cannot expand scope; revocation remains live. External forms are forbidden, synthetic mutations require preapproved manifests, every connection/action is checked.

## Alternatives considered

Self-authorizing URLs, string-prefix host checks, blanket private-IP exceptions and approval-to-bypass-safety are rejected.

## Consequences and verification

Single local operator needs session/CSRF/Host/Origin controls; nonlocal DNS support is deliberately deferred. See the [normative specification](../architecture/safety-policy.md) and [readiness gates](../implementation-readiness.md) for implementation requirements and evidence still needed.

This decision supersedes conflicting v0.1 wording; it does not claim controls have been implemented or tested.
