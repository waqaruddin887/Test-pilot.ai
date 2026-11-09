# TestPilot AI documentation

**Current coding status:** [implemented/tested/partial/planned](implementation-status.md), [security limits](security-status.md), [actual evaluation](evaluation-results.md), and [offline development ADR-012](decisions/012-offline-fixture-development.md). Earlier documentation-only status statements are historical.
Technical baseline v0.2, selected 2026-11-08 under the architecture-resolution task. Application implementation is not included. Accepted ADRs are engineering decisions, not commercial signatures, compliance certification, installed controls or test results.

## Reading order and authority

1. [Fourteen foundations and hub](foundations/index.md) define product intent and summarize the selected baseline.
2. [Technical baseline / monorepo](architecture/baseline.md) defines scope, fixed limits and staged delivery.
3. [Plan contract](contracts/test-plan-v1.md), [generated JSON Schema](contracts/test-plan-v1.schema.json) and [HTTP API](contracts/http-api-v1.md) define wire structures and validation.
4. [Safety](architecture/safety-policy.md), [runner](architecture/runner-protocol.md), [jobs](architecture/job-lifecycle.md), [database](architecture/data-model.md) and [findings/evaluation](architecture/findings-and-evaluation.md) are normative subsystem specifications.
5. [Implementation readiness](implementation-readiness.md) distinguishes completed design decisions from actual remaining blockers.

Root AGENTS.md governs engineering behavior. Contracts and subsystem specifications supply detailed v0.2 constraints adopted by all foundations; no looser example overrides them. If an unresolved conflict is discovered, fail closed and create an ADR change updating all affected texts. History/archive is non-normative. Dependencies and runtime choices still require compatibility checks; do not infer authority to install or modify host configuration.

## Architecture decisions

- [ADR-001: Deterministic execution over generated code](adr/001-deterministic-execution.md)
- [ADR-002: Local-first controlled fixtures](adr/002-local-controlled-fixtures.md)
- [ADR-003: One bounded hosted planner without retrieval](adr/003-bounded-hosted-planner.md)
- [ADR-004: Separate HTTP handling from queued work](adr/004-queue-worker.md)
- [ADR-005: Separate browser privileges from planner and supervisor](adr/005-browser-isolation.md)
- [ADR-006: One versioned strict Pydantic plan contract](adr/006-canonical-contracts.md)
- [ADR-007: Idempotency, transactional outbox and fenced leases](adr/007-durable-jobs.md)
- [ADR-008: Independent machine assessment and human review](adr/008-verification-review.md)
- [ADR-009: Versioned fixture authorization and fail-closed operations](adr/009-authorization-policy.md)
- [ADR-010: Private expiring evidence and independent benchmark](adr/010-evidence-evaluation.md)
- [ADR-011: Canonical documentation and traceable baseline changes](adr/011-documentation-baseline.md)

## Review and provenance

- [Original foundation review](reviews/2026-11-08-foundation-review.md): historical audit, superseded where the v0.2 baseline selects a resolution.
- [Architecture resolution change report](reviews/2026-11-08-architecture-resolution.md): exact file changes, validation and outstanding issues.
- [Original source archive](archive/v0.1/README.md): byte-preserved v0.1 originals and path/hash mapping.
- [Baseline revalidation and clarifications](reviews/2026-11-08-baseline-revalidation.md): follow-up contradiction fixes and exact changes for the repeated review.
- [Machine-readable change manifest](change-manifest.json): exact moves, additions, modifications and original checksums.

The active source location is `docs/foundations/`. Uppercase `Docs/` and duplicate root `Agents.md` are retired; the latter is archived, while root `AGENTS.md` is authoritative. No files were discarded.
