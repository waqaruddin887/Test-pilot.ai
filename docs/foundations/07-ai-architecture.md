# 07 — AI Architecture & Model Design

**Technical baseline v0.2 — 8 November 2026. Design selected. See [current implementation and test evidence](../implementation-status.md); the full hardened design is not yet complete. Commercial charter/legal approval is not implied.**

## Core decision

One hosted LLM produces finite structured candidate test plans. Python Pydantic validates schema, authorization and action policy; a deterministic Playwright engine executes permitted actions. Deterministic reporting is initial scope; an optional later reporting model may summarize supplied evidence but cannot confirm defects or operate a browser.

## Data flow

Approved URL → isolated browser discovery → redacted page outline → LLM planner → strict JSON/Pydantic validation → safety action validator → Playwright executor → assertion and independent oracle checker → reproduction → evidence report → human review.

## Plan schema

The sole format is [test-plan 1.0.0](../contracts/test-plan-v1.md): schema_version, objective, cases; case id/title/intent/steps; ordered steps discriminated by action. Exact role/name or text targets; assertion-level versioned oracle_ref (explicit null only for exploratory cases). Required timeout_ms, strict types and forbidden extra properties. No parallel actions/assertions arrays, generic selectors, rationale/code fields or model-authored expected-behavior authority.

## Model selection and monitoring

Use one configurable model/provider initially. Pin model identifier and prompt version; log sanitized request category, token count, latency, cost estimate and schema validity. Never embed API keys or credentials in prompts. One bounded correction attempt for invalid structured output; hard stop when spend or token caps are exceeded.

## Fallback

If planner fails, mark planning failed/unavailable. Deterministic smoke is available only as an explicit newly requested smoke-mode run. Do not fabricate results. Preserve error type for debugging.

## No RAG justification

No approved external requirements corpus yet, no retrieval quality bottleneck, and no evidence that embeddings would improve reliable assertions. The golden fixture specification itself acts as oracle in the benchmark. Revisit retrieval only if future use cases supply large versioned, permissioned specifications.

## Guardrails

Page content is untrusted input and may contain prompt injection; it never changes instruction hierarchy or browser permissions. Schema validation and network allowlisting occur outside the LLM. Reporter cannot mutate tests, browser state or labels.

## Experiment plan

Test schema failures, prompt injections in page text, ambiguous locators, different model temperatures and repeated fixture runs. Compare plan stability, execution reliability and reported defect precision.

## References

[Playwright tracing](https://playwright.dev/python/docs/api/class-tracing) · [OWASP prompt injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html).

## v0.2 technical baseline

Planner runs in trusted orchestration; isolated Playwright runs in a fixture-only namespace under a narrow [supervisor protocol](../architecture/runner-protocol.md). Neither schema output nor a generated assertion grants network/action/oracle authority. Structural repair is bounded to one request; policy/oracle violations are rejected without repair. Machine verified and human accepted are separate.

Normative details: [baseline](../architecture/baseline.md), [ADRs](../README.md#architecture-decisions), and [implementation readiness](../implementation-readiness.md). Original v0.1 content is preserved in `../archive/v0.1/`; historical targets are not measurements.
