# ADR-008: Independent machine assessment and human review

Status: Accepted technical baseline, 2026-11-08. Implementation pending.

## Context

A failed AI assertion is not an authoritative defect; original documents mixed verification and confirmation.

## Decision

Machine assessment is pass/suspected/verified/test_error/inconclusive. Human review is unreviewed/accepted/dismissed. Only complete oracle-backed initial plus reproduced evidence and acceptance yields a current confirmed claim. Append reviews; never edit raw outcomes.

## Alternatives considered

One overloaded finding status and human override of missing oracle/evidence are rejected.

## Consequences and verification

Expired evidence disables new acceptance and qualifies historical reviews; metrics expose machine false positives separately. See the [normative specification](../architecture/findings-and-evaluation.md) and [readiness gates](../implementation-readiness.md) for implementation requirements and evidence still needed.

This decision supersedes conflicting v0.1 wording; it does not claim controls have been implemented or tested.
