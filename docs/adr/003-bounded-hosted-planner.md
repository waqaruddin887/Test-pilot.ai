# ADR-003: One bounded hosted planner without retrieval

Status: Accepted technical baseline, 2026-11-08. Implementation pending.

## Context

Planning is useful; autonomous authority, RAG and model training have no demonstrated MVP need.

## Decision

One configurable hosted provider/model emits canonical plans from minimized outlines and public oracle requirements. Freeze model/prompt versions, cap tokens/time/spend, permit one schema repair only. Optional reporter is deferred. Explicit smoke mode is separate; no silent fallback.

## Alternatives considered

RAG, embeddings, fine-tuning, multi-agent browser tools and automatic provider retries are excluded.

## Consequences and verification

Provider/model, verified prices/terms and actual spending caps remain live-call gates; offline fake adapters support development. See the [normative specification](../architecture/baseline.md) and [readiness gates](../implementation-readiness.md) for implementation requirements and evidence still needed.

This decision supersedes conflicting v0.1 wording; it does not claim controls have been implemented or tested.
