# ADR-001: Deterministic execution over generated code

Status: Accepted technical baseline, 2026-11-08. Implementation pending.

## Context

Model output is untrusted and browser steps must be reproducible.

## Decision

Execute only the five canonical enum actions through developer-authored Python Playwright handlers; never run model scripts, selectors, shell, or arbitrary eval. The independent oracle checker owns assessment.

## Alternatives considered

Arbitrary generated test programs would be flexible but break bounded validation and evidence integrity.

## Consequences and verification

Supported behavior is intentionally narrow; unsupported pages/actions become typed errors. See the [normative specification](../contracts/test-plan-v1.md) and [readiness gates](../implementation-readiness.md) for implementation requirements and evidence still needed.

This decision supersedes conflicting v0.1 wording; it does not claim controls have been implemented or tested.
