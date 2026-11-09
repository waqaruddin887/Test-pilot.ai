# 14 — Risk Management & Cost Estimation Plan

**Technical baseline v0.2 — 8 November 2026. Design selected. See [current implementation and test evidence](../implementation-status.md); the full hardened design is not yet complete. Commercial charter/legal approval is not implied.**

## Cost model

Let P = input tokens per run, Q = output tokens per run, I = vendor price per million input tokens, O = price per million output tokens, R = runs per month. Estimated LLM spend in provider billing currency:
**Monthly LLM cost = R × (P × I + Q × O) / 1,000,000**, plus retries and optional reporter calls.

Example **illustrative only**: P=8,000 tokens, Q=2,000 tokens, I=$1/million, O=$4/million → $0.016 per run; 1,000 runs cost about $16 before additional LLM passes. These are arbitrary teaching rates, not quoted vendor prices.

## Other costs

CPU/RAM for Playwright browser worker, Postgres/Redis service, storage of screenshots/traces, logs/monitoring, CI compute and bandwidth. Local prototype may run without monthly cloud infrastructure fees, but hardware/time costs remain.

## Budget controls

1–5 cases (default 3), max 12 steps including assertions, one structural planner repair, fixed token ceilings plus configured monetary per-run/daily caps, one active run, 120-second queue deadline and 300-second active deadline including reproduction. Baseline fixes screenshot/storage/TTL ceilings. Record actual provider token counts per request. Stop planned execution before hitting hard budget ceiling.

## Risks

| Risk | Probability (draft) | Impact | Mitigation |
| --- | --- | --- | --- |
| LLM unavailable or rate-limited | Medium | Medium | Explicit planning failure; separately requested smoke mode |
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

LLM outage → planning failure, no automatic substitution; deterministic smoke needs an explicit new smoke-mode run. Browser crash → stop run and retain safe diagnostic metadata. Provider cost breach → suspend new runs. Data-exposure suspicion → halt execution and revoke impacted credentials as appropriate.

## Open commitments

- [ ]  Pick model/provider and retrieve current price and rate limits.
- [ ]  Set actual monetary spending ceilings; implement selected 1 GiB store / 100 MiB run quota and verify adequacy.
- [ ]  Benchmark CPU and elapsed time per full run.
- [ ]  Identify external deployment location only after security gate.

## v0.2 technical baseline

See [limits](../architecture/baseline.md) and [atomic budget reservations](../architecture/job-lifecycle.md). Unknown provider usage retains its reservation. Illustrative pricing remains arbitrary teaching data, never a vendor quote. Accepted design decisions do not resolve ownership/funding/eligibility, installed runtime compatibility, provider terms/caps or measured CPU/latency.

Normative details: [baseline](../architecture/baseline.md), [ADRs](../README.md#architecture-decisions), and [implementation readiness](../implementation-readiness.md). Original v0.1 content is preserved in `../archive/v0.1/`; historical targets are not measurements.
