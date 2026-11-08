# 01 — Project Charter & Statement of Work

**Draft v0.1 — 8 November 2026. Not approved or signed.**

## Purpose

Deliver a local-first AI-assisted browser-testing prototype for an engineering portfolio: authorized URL inspection, bounded LLM test planning, deterministic Playwright execution, evidence collection, reproducible findings and review dashboard. Selection or pay from Alignerr is not guaranteed.

## People and authority

Project lead: developer; repository ownership and collaborators not yet confirmed. No client, sponsor, compliance officer or external approver identified. Third-party dependencies: chosen hosted LLM API, Playwright browser runtime, local Postgres/containers.

## Seven-day proposed scope

| Day | Deliverable and acceptance |
| --- | --- |
| 1 | Monorepo, dashboard and API create a run |
| 2 | Allowlisted browser discovers accessible UI elements |
| 3 | LLM produces strictly validated bounded test plan |
| 4 | Playwright runs one plan with step results |
| 5 | Finding with oracle and successful reproduction |
| 6 | Good/broken fixture benchmark and quality metrics |
| 7 | Setup README, security checks and recorded walkthrough |

## In and out

In: 3–5 tests per session, supported actions, screenshots, traces, run history, controlled fixtures. Out: arbitrary public website testing, real user data, payments/purchases, security penetration tests, CAPTCHA bypass, production authentication, RAG, fine-tuning, GPU deployment, GitHub publishing automation.

## Budget and approval

Funding, monetary cap and development hours are **unknown**. Proposed policy: local development first; choose provider API cap before first live request; keep model and browser consumption metered.

## Definition of done

A reviewer can reproduce one passing control, one confirmed seeded defect with specified expected behavior, and inspect trace/evidence. Documentation must distinguish simulated data, implemented features and future work. Scope changes require a dated design decision.

## Open gates

- [ ]  Repository and intellectual-property ownership confirmed.
- [ ]  Approved test domain, safe actions and redaction policy defined.
- [ ]  LLM provider and cost cap approved.
- [ ]  Alignerr location/project eligibility verified independently.