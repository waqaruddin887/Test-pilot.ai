# 07 — AI Architecture & Model Design

**Draft v0.1. RAG and fine-tuning are intentionally excluded.**

## Core decision

One hosted LLM produces finite structured candidate test plans. Python Pydantic validates schema, authorization and action policy; a deterministic Playwright engine executes permitted actions. A reporting model may summarize verified findings, but cannot confirm a defect or operate a browser.

## Data flow

Approved URL → isolated browser discovery → redacted page outline → LLM planner → strict JSON/Pydantic validation → safety action validator → Playwright executor → assertion and independent oracle checker → reproduction → evidence report → human review.

## Plan schema

Top-level: schema_version, objective, cases. Each case includes id, title, actions, assertions and optional rationale. Each action: type (navigate/click/fill/assert_visible/assert_url), target fields (role, name or text), optional value, timeout. Assertions include oracle_ref and matching expected behavior. Reject free-form code and arbitrary selectors that cannot be resolved safely. An invented exact text is not an authoritative oracle.

## Model selection and monitoring

Use one configurable model/provider initially. Pin model identifier and prompt version; log sanitized request category, token count, latency, cost estimate and schema validity. Never embed API keys or credentials in prompts. One bounded correction attempt for invalid structured output; hard stop when spend or token caps are exceeded.

## Fallback

If planner fails, offer deterministic smoke-only tests (page loads, selected role exists) or explicitly mark planning unavailable. Do not fabricate results. Preserve error type for debugging.

## No RAG justification

No approved external requirements corpus yet, no retrieval quality bottleneck, and no evidence that embeddings would improve reliable assertions. The golden fixture specification itself acts as oracle in the benchmark. Revisit retrieval only if future use cases supply large versioned, permissioned specifications.

## Guardrails

Page content is untrusted input and may contain prompt injection; it never changes instruction hierarchy or browser permissions. Schema validation and network allowlisting occur outside the LLM. Reporter cannot mutate tests, browser state or labels.

## Experiment plan

Test schema failures, prompt injections in page text, ambiguous locators, different model temperatures and repeated fixture runs. Compare plan stability, execution reliability and reported defect precision.

## References

[Playwright tracing](https://playwright.dev/python/docs/api/class-tracing) · [OWASP prompt injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html).