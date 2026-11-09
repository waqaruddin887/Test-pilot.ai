# 11 — Security & Threat Model Blueprint

**Technical baseline v0.2 — 8 November 2026. Design selected. See [current implementation and test evidence](../implementation-status.md); the full hardened design is not yet complete. Commercial charter/legal approval is not implied.**

## Assets and boundaries

Protect host machine/network, API credentials, LLM token budget, project authorization list, browser state, screenshots/traces, local test fixtures and integrity of bug reports. Trust boundaries: user → API; webpage → inspection; inspection → LLM; model → executor; worker → network/artifacts.

## Threat scenarios and mitigation

| Threat | Mitigation and verification |
| --- | --- |
| SSRF via target URL, redirects, DNS rebinding | Exact origin/path allowlist and pinned fixture address/port without general runner DNS, restricted network namespace, deny metadata/internal endpoints; integration tests. Public DNS/connection-time rebinding handling is a future expansion gate. |
| Prompt injection from webpage content | Treat DOM as data; separate system instructions; strict schema; sandbox policies outside LLM; injection fixture |
| Arbitrary generated code execution | Never eval model output; enum actions only; reject JS/shell/Python from plan |
| Cross-origin data exfiltration | Block all unauthorized egress, including subresources and redirects; test with local sink fixture |
| Destructive testing | Restrict to synthetic fixtures; operator preapproves exact versioned safe operations; refuse unknown/non-fixture submissions and all delete/purchase/external-send actions |
| Credential/PII leakage | Synthetic data only; cookies and auth headers excluded from prompts and logs; redaction tests |
| Container escape/resource exhaustion | Nonroot browser, read-only FS where feasible, no host mounts, CPU/RAM/time budgets, seccomp and patching |
| Artifact exposure | Run ownership checks, path indirection, expiring artifacts, private storage |
| Report tampering/fabricated findings | Independent oracle refs, immutable run evidence, reproduction hashes and human review |
| API abuse/token overspend | Auth before public access, rate limiting, model quotas, budgets and cancellation |

## Threat methodology

Use STRIDE for service-level threats (spoofing, tampering, repudiation, information disclosure, denial of service, privilege escalation), plus AI-specific prompt injection, model hallucination and tool-output manipulation. Prioritize controls by likelihood and impact, not severity labels alone.

## Hard prohibitions for MVP

No arbitrary public URL scanning, no production logins, no external site forms, no automated purchases, no browser extension or system monitoring, no privileged host mounts. Locally authorized fixtures run in explicit container network.

## Security release gates

- [ ]  Redirect/DNS/blocked-host tests pass.
- [ ]  Prompt-injection fixture never alters allowable actions.
- [ ]  Secrets absent from model requests and persisted logs.
- [ ]  Browser worker cannot access internal/metadata endpoints.
- [ ]  Cancellation and resource limits prevent orphaned jobs.
- [ ]  Artifact retrieval enforces access and expiry.
A "passed" gate requires a real recorded test, not this checkbox.

## Incident response

Stop execution, disable suspect origin, revoke provider keys if compromised, quarantine artifacts, preserve sanitized incident evidence, assess personal-data exposure and follow applicable notification requirements. A single developer is interim incident owner until a team is appointed.

## References

[OWASP LLM Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html), [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/).

## v0.2 technical baseline

The [unified safety policy](../architecture/safety-policy.md) is the sole target/action authority. Privilege isolation uses the [supervised runner namespace](../architecture/runner-protocol.md), with no fixture-network path to provider/DB/Redis/API/supervisor/host. Local operator session, Origin/Host and CSRF checks are required now, not postponed until public hosting. Nonlocal/public DNS handling is out of scope. All security release checkboxes remain unpassed until actual tests.

Normative details: [baseline](../architecture/baseline.md), [ADRs](../README.md#architecture-decisions), and [implementation readiness](../implementation-readiness.md). Original v0.1 content is preserved in `../archive/v0.1/`; historical targets are not measurements.
