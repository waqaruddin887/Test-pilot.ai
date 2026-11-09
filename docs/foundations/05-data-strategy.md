# 05 — Data Strategy & Sourcing Plan

**Technical baseline v0.2 — 8 November 2026. Design selected. See [current implementation and test evidence](../implementation-status.md); the full hardened design is not yet complete. Commercial charter/legal approval is not implied.**

## Approved initial sources

Synthetic pages controlled by developer (known-good and deliberately broken variants), their written requirements, Playwright-generated test observations, and anonymized local execution logs. Real candidate interviews, customer production data, third-party site crawls and private datasets excluded.

## Data groups

| Kind | Examples | Handling |
| --- | --- | --- |
| Synthetic/public | Demo form labels, seeded cases | Suitable for planner context |
| Internal | Run IDs, step timing, test goals | Local, access controlled |
| Confidential | Screenshots, browser traces, sensitive paths | Restricted; never send raw screenshot/trace bytes to LLM in MVP |
| Personal/secret | Captured target cookies, real email addresses, credentials, tokens | Do not collect or store in MVP |

## Authorization

For every local fixture record owner, permission evidence, exact origin/path/operation scope, policy version and explicit expiration (maximum seven days). Nonlocal targets remain outside MVP; any future authorization requires a separate scope/security review. Public accessibility is never permission.

## Processing lifecycle

Allowlist URL → bounded browser inspection → select relevant fields → redact secrets → structured planner context → validated plan → local execution → evidence capture → retention/deletion. Avoid trusting regex alone: prefer synthetic inputs and selected metadata only.

## Storage and retention (selected MVP defaults)

Synthetic fixtures tracked in Git. Sanitized run metadata, reviews and logs expire seven days after run acceptance. Screenshot/trace bytes expire 24 hours after capture; no automatic export or backup. Operators may shorten windows; extension needs a documented policy change. No captured target cookies, auth headers, session tokens or secrets are persisted. The operator control plane separately stores session-token hashes, never plaintext tokens; this does not permit target-session capture. Synthetic email-like values are allowed only under the approved fixture manifest. Provider retention and residency require vendor/account-specific verification before use.

## Quality and compliance gates

Confirm each fixture's copyright ownership and license. Test redaction with seeded fake secrets. Check artifact deletion, URL authorization log and absent secret values from telemetry. Use access controls and run-specific identifiers to prevent cross-run leakage.

## Decisions pending

- [ ]  Choose actual provider and inspect DPA/retention terms.
- [ ]  Confirm domain ownership or written permission.
- [ ]  Implement/test selected retention windows and define any explicitly sanitized public demo export policy.

## v0.2 technical baseline

Capture is restricted to reviewed synthetic fixtures. Trace sanitization is not assumed: unexpected cookies/authentication/real secrets stop capture and quarantine or discard temporary evidence. Redacting planner input is independent of artifact safety. [Data model](../architecture/data-model.md) defines immediate expiry enforcement, minute cleanup, ownership checks and deletion order.

Normative details: [baseline](../architecture/baseline.md), [ADRs](../README.md#architecture-decisions), and [implementation readiness](../implementation-readiness.md). Original v0.1 content is preserved in `../archive/v0.1/`; historical targets are not measurements.
