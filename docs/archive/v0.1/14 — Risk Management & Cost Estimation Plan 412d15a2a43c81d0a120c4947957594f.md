# 14 — Risk Management & Cost Estimation Plan

**Draft v0.1. Cost assumptions are examples; no provider pricing or allocated budget was supplied.**

## Cost model

Let P = input tokens per run, Q = output tokens per run, I = vendor price per million input tokens, O = price per million output tokens, R = runs per month. Estimated LLM spend in provider billing currency:
**Monthly LLM cost = R × (P × I + Q × O) / 1,000,000**, plus retries and optional reporter calls.

Example **illustrative only**: P=8,000 tokens, Q=2,000 tokens, I=$1/million, O=$4/million → $0.016 per run; 1,000 runs cost about $16 before additional LLM passes. These are arbitrary teaching rates, not quoted vendor prices.

## Other costs

CPU/RAM for Playwright browser worker, Postgres/Redis service, storage of screenshots/traces, logs/monitoring, CI compute and bandwidth. Local prototype may run without monthly cloud infrastructure fees, but hardware/time costs remain.

## Budget controls

Max 5 cases per run, 12 steps per case, max one planner repair call, configurable per-run and daily token budgets, concurrency 1 initially, total run timeout (proposed 5 min), screenshot cap and TTL. Record actual provider token counts per request. Stop planned execution before hitting hard budget ceiling.

## Risks

| Risk | Probability (draft) | Impact | Mitigation |
| --- | --- | --- | --- |
| LLM unavailable or rate-limited | Medium | Medium | Smoke-only fallback, clear status |
| False-positive defect claims | High | High | Oracle validation, rerun, review |
| Playwright locator flakiness | Medium | Medium | Accessible locator rules and ambiguity errors |
| Prompt injection | Medium | High | Untrusted-page boundary, policy sandbox |
| Browser host/network access | Medium | Critical | Network isolation and deny-by-default egress |
| Token cost spikes | Medium | Medium | Per-run and daily hard caps |
| Storage leakage | Medium | High | Restricted directory, expiry, redaction |
| Scope creep | High | Medium | P0-only gate, design change log |
| Alignerr eligibility mismatch | Unknown | High for goal | Verify terms before significant work |

## Risk scoring

Initial qualitative labels are subjective. At every milestone update probability, impact, owner, status and remaining exposure. Critical security risks block external launch regardless of demo polish.

## Operational contingency

LLM outage → no model-dependent plan; execute only deterministic smoke check if permitted. Browser crash → stop run and retain safe diagnostic metadata. Provider cost breach → suspend new runs. Data-exposure suspicion → halt execution and revoke impacted credentials as appropriate.

## Open commitments

- [ ]  Pick model/provider and retrieve current price and rate limits.
- [ ]  Set actual spending ceiling and storage quota.
- [ ]  Benchmark CPU and elapsed time per full run.
- [ ]  Identify external deployment location only after security gate.