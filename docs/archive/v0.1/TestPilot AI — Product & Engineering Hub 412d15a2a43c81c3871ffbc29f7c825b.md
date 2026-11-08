# TestPilot AI — Product & Engineering Hub

**Stage:** Architecture and specification — draft v0.1 (8 November 2026)
**Project:** TestPilot AI (working name)
**Goal:** Build an AI-assisted autonomous web testing agent that discovers UI elements, plans meaningful tests, runs restricted Playwright actions, verifies outcomes against trustworthy oracles, and reports reproducible defects with evidence.
**Audience:** Solo developer preparing a demonstrable engineering project for possible Alignerr consideration; future users would be web developers and QA engineers.
**Status:** No implementation or evaluation evidence has been supplied yet. The following pages are proposed designs, not approved or completed work.

## Current decision

Build an authorized-domain, local-first MVP. Use an LLM only for structured test planning and optional explanation; a Python Playwright executor enforces allowed operations. A reported bug requires a requirement-backed oracle or baseline and an independent reproduction attempt.

## Seven-day proposed milestones

1. Foundation: monorepo, API, dashboard, approved origin configuration.
2. Browser discovery and evidence capture.
3. LLM test planner with validated schema.
4. Deterministic browser execution.
5. Reproduction and failure triage.
6. Evaluation against seeded good/broken fixtures.
7. Documentation, reliability checks, and demonstrable walkthrough.

## Critical build gates

- [ ]  Lock URL allowlist, browser isolation and safe-action policy before agent execution.
- [ ]  Create at least one known-good and one intentionally broken local test fixture before reporting accuracy.
- [ ]  Define assertion/oracle sources; never infer a product defect solely from model expectations.
- [ ]  Establish LLM prompt redaction and artifact retention policy before collecting real data.
- [ ]  Determine whether any third-party or production website testing is authorized.
- [ ]  Confirm Alignerr's project ownership, geography and application requirements separately; no selection probability is established.

## Documents

The fourteen child documents below are draft specifications grouped as Product & Strategy (1–4), Data & AI (5–8), Technical & Security (9–11), and Evaluation, Legal & Risk (12–14). Each includes implementation details and unresolved decisions. Treat numeric targets as **proposed acceptance criteria**, not observed product performance.

## Working agreement

Review and revise as design choices or legal obligations change. Never label untested behavior, model accuracy or legal compliance as verified. Future source code and demo assets should remain under an account that satisfies any employer ownership conditions.

[01 — Project Charter & Statement of Work](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/01%20%E2%80%94%20Project%20Charter%20&%20Statement%20of%20Work%20412d15a2a43c810ca3c7d8b7283780a9.md)

[02 — Product Requirements Document (PRD)](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/02%20%E2%80%94%20Product%20Requirements%20Document%20(PRD)%20412d15a2a43c81e3a6c2d9e576dea5c6.md)

[03 — Software Requirements Specification (SRS)](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/03%20%E2%80%94%20Software%20Requirements%20Specification%20(SRS)%20412d15a2a43c81c2a32cf9b74548faac.md)

[04 — Wireframes & User Journey Prototypes](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/04%20%E2%80%94%20Wireframes%20&%20User%20Journey%20Prototypes%20412d15a2a43c815ba980c31d681aadb9.md)

[05 — Data Strategy & Sourcing Plan](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/05%20%E2%80%94%20Data%20Strategy%20&%20Sourcing%20Plan%20412d15a2a43c81a488b8e9af7afb0f61.md)

[06 — Datasheet for Golden Fixture Dataset](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/06%20%E2%80%94%20Datasheet%20for%20Golden%20Fixture%20Dataset%20412d15a2a43c813ca27ce91c58aaf45e.md)

[07 — AI Architecture & Model Design](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/07%20%E2%80%94%20AI%20Architecture%20&%20Model%20Design%20412d15a2a43c818f9bb4fc53d28d4071.md)

[08 — Prompt & Guardrail Specification](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/08%20%E2%80%94%20Prompt%20&%20Guardrail%20Specification%20412d15a2a43c81a9825bf3bd3023e8b1.md)

[09 — System Architecture Document (SAD)](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/09%20%E2%80%94%20System%20Architecture%20Document%20(SAD)%20412d15a2a43c81749073c0c802da3880.md)

[10 — Technical Design Document & API Contracts](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/10%20%E2%80%94%20Technical%20Design%20Document%20&%20API%20Contracts%20412d15a2a43c818888e0d351cb0cfa94.md)

[11 — Security & Threat Model Blueprint](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/11%20%E2%80%94%20Security%20&%20Threat%20Model%20Blueprint%20412d15a2a43c81779760f9a96ff56dec.md)

[12 — AI Evaluation & Golden Dataset Plan](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/12%20%E2%80%94%20AI%20Evaluation%20&%20Golden%20Dataset%20Plan%20412d15a2a43c8123b921ec8fc5dd06f3.md)

[13 — AI Risk & Compliance Assessment](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/13%20%E2%80%94%20AI%20Risk%20&%20Compliance%20Assessment%20412d15a2a43c81798349d44d53415e74.md)

[14 — Risk Management & Cost Estimation Plan](TestPilot%20AI%20%E2%80%94%20Product%20&%20Engineering%20Hub/14%20%E2%80%94%20Risk%20Management%20&%20Cost%20Estimation%20Plan%20412d15a2a43c81d0a120c4947957594f.md)