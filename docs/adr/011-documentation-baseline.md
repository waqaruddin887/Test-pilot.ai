# ADR-011: Canonical documentation and traceable baseline changes

Status: Accepted technical baseline, 2026-11-08. Implementation pending.

## Context

Case-sensitive Docs/docs and AGENTS/Agents duplication and broken export links caused competing sources.

## Decision

Use docs/foundations for all fourteen active source documents, docs/architecture and contracts for normative detail, and docs/adr for accepted decisions. Preserve original bytes in docs/archive/v0.1 and original audit as historical. Maintain path/hash manifest and exact change report.

## Alternatives considered

Deleting original requirements or leaving contradictory active duplicates is rejected.

## Consequences and verification

Accepted means engineering design selected under this task, not signed charter, legal approval, working controls or passed gates. Later changes update all affected contracts/summaries. See the [normative specification](../README.md) and [readiness gates](../implementation-readiness.md) for implementation requirements and evidence still needed.

This decision supersedes conflicting v0.1 wording; it does not claim controls have been implemented or tested.
