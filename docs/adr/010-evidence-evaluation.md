# ADR-010: Private expiring evidence and independent benchmark

Status: Accepted technical baseline, 2026-11-08. Implementation pending.

## Context

Traces can persist secrets and benchmark labels can leak into planning or inflate accuracy.

## Decision

Synthetic reviewed capture only; immutable manifests, hashes, private opaque artifact IDs, 24-hour byte TTL and seven-day metadata TTL. Keep hidden labels/reference results outside planner/runner. Report both machine and human metrics with fixed denominators and N/A.

## Alternatives considered

Regex-only trace sanitization, indefinite evidence retention and model-derived oracle authority are rejected.

## Consequences and verification

Retention/access/deletion and leakage tests are required; five pairs support only a limited controlled demo. See the [normative specification](../architecture/findings-and-evaluation.md) and [readiness gates](../implementation-readiness.md) for implementation requirements and evidence still needed.

This decision supersedes conflicting v0.1 wording; it does not claim controls have been implemented or tested.

## Clarification — 2026-11-08

Oracle content is immutable at creation, with a one-time review-and-seal before first use; any content change creates a new revision. Evidence-manifest content/hash and finding binding are sealed together when published. Reporter wording cannot override machine assessment or human review. The prohibition on captured target credentials is separate from storing operator session-token hashes in the control plane.
