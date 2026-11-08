# ADR-006: One versioned strict Pydantic plan contract

Status: Accepted technical baseline, 2026-11-08. Implementation pending.

## Context

D07 and D08 used incompatible field names, assertion placement and required metadata.

## Decision

Choose schema_version 1.0.0, ordered steps discriminated by action, exact target variants, explicit intent and assertion-level versioned oracle refs. Pydantic v2 strict/extra-forbid models own schema; generate JSON Schema and frontend transport types.

## Alternatives considered

Separate hand-maintained model schemas and permissive free-form dictionaries are rejected.

## Consequences and verification

Runtime authorization/oracle checks remain independent; documentation models are specifications until implemented and tested in the application. See the [normative specification](../contracts/test-plan-v1.md) and [readiness gates](../implementation-readiness.md) for implementation requirements and evidence still needed.

This decision supersedes conflicting v0.1 wording; it does not claim controls have been implemented or tested.
