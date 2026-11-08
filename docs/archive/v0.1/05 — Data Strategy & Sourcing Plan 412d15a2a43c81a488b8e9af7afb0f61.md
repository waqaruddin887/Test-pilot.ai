# 05 — Data Strategy & Sourcing Plan

**Draft v0.1. No live data collection is authorized by this page.**

## Approved initial sources

Synthetic pages controlled by developer (known-good and deliberately broken variants), their written requirements, Playwright-generated test observations, and anonymized local execution logs. Real candidate interviews, customer production data, third-party site crawls and private datasets excluded.

## Data groups

| Kind | Examples | Handling |
| --- | --- | --- |
| Synthetic/public | Demo form labels, seeded cases | Suitable for planner context |
| Internal | Run IDs, step timing, test goals | Local, access controlled |
| Confidential | Screenshots, browser traces, sensitive paths | Restricted, do not send to LLM by default |
| Personal/secret | Cookies, emails, credentials, tokens | Do not collect or store in MVP |

## Authorization

Before nonlocal target testing record site owner, permission evidence, approved host/path, operation scope and expiration. A publicly accessible website is not automatically approved for automated testing.

## Processing lifecycle

Allowlist URL → bounded browser inspection → select relevant fields → redact secrets → structured planner context → validated plan → local execution → evidence capture → retention/deletion. Avoid trusting regex alone: prefer synthetic inputs and selected metadata only.

## Storage and retention (proposal)

Synthetic fixtures tracked in Git. Sanitized result metadata retained locally for a configurable period (suggested 7 days). Screenshots/traces default to deletion after 24 hours unless consciously exported. No cookies, auth headers, session tokens or secrets persisted. Provider retention and residency require vendor/account-specific verification before use.

## Quality and compliance gates

Confirm each fixture's copyright ownership and license. Test redaction with seeded fake secrets. Check artifact deletion, URL authorization log and absent secret values from telemetry. Use access controls and run-specific identifiers to prevent cross-run leakage.

## Decisions pending

- [ ]  Choose actual provider and inspect DPA/retention terms.
- [ ]  Confirm domain ownership or written permission.
- [ ]  Approve retention windows and public demo data policy.