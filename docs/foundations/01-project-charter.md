# 01 — Project Charter & Statement of Work

**Technical baseline v0.2 — 8 November 2026. Design selected; implementation and test evidence pending. Commercial charter/legal approval is not implied.**

## Purpose

Deliver a local-first AI-assisted browser-testing prototype for an engineering portfolio: authorized URL inspection, bounded LLM test planning, deterministic Playwright execution, evidence collection, reproducible findings and review dashboard. Selection or pay from Alignerr is not guaranteed.

## People and authority

Project lead: developer; repository ownership and collaborators not yet confirmed. No client, sponsor, compliance officer or external approver identified. Third-party dependencies: chosen hosted LLM API, Playwright browser runtime, local Postgres/containers.

## Seven-day proposed scope

| Day | Deliverable and acceptance |
| --- | --- |
| 1 | Monorepo, dashboard, API and persisted project configuration; honest 503 until capable run worker exists. Full run creation remains a pending acceptance gate. |
| 2 | Allowlisted browser discovers accessible UI elements |
| 3 | LLM produces strictly validated bounded test plan |
| 4 | Playwright runs one plan with step results |
| 5 | Oracle-backed automated verification, successful clean reproduction and separate human review |
| 6 | Good/broken fixture benchmark and quality metrics |
| 7 | Setup README, security checks and recorded walkthrough |

## In and out

In: 1–5 tests per run (default 3), supported actions, screenshots, traces, run history, controlled fixtures. Out: arbitrary public website testing, real user data, payments/purchases, security penetration tests, CAPTCHA bypass, production authentication, RAG, fine-tuning, GPU deployment, GitHub publishing automation.

## Budget and approval

Funding, monetary cap and development hours are **unknown**. Proposed policy: local development first; choose provider API cap before first live request; keep model and browser consumption metered.

## Definition of done

A reviewer can reproduce one passing control, one confirmed seeded defect with specified expected behavior, and inspect trace/evidence. Documentation must distinguish simulated data, implemented features and future work. Scope changes require a dated design decision.

## Open gates

- [ ]  Repository and intellectual-property ownership confirmed.
- [ ]  Fixture authorization/operation manifest populated and safety/redaction controls implemented and tested.
- [ ]  LLM provider and cost cap approved.
- [ ]  Alignerr location/project eligibility verified independently.

## v0.2 technical baseline

The product remains a local-first bounded portfolio prototype. Only preauthorized synthetic fixture operations run automatically; external forms are prohibited even with human approval. Day 1 must not fake a queued/completed testing run. The [scope and limits](../architecture/baseline.md) resolve the case-count/deadline and unavailable-worker semantics. Ownership, funding and eligibility are still unverified administrative facts.

Normative details: [baseline](../architecture/baseline.md), [ADRs](../README.md#architecture-decisions), and [implementation readiness](../implementation-readiness.md). Original v0.1 content is preserved in `../archive/v0.1/`; historical targets are not measurements.
