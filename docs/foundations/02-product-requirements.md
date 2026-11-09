# 02 — Product Requirements Document (PRD)

**Technical baseline v0.2 — 8 November 2026. Design selected. See [current implementation and test evidence](../implementation-status.md); the full hardened design is not yet complete. Commercial charter/legal approval is not implied.**

## Problem and users

Independent web developers and QA engineers spend time authoring UI test scenarios and diagnosing failures. TestPilot AI proposes scenarios, executes restricted browser steps, and surfaces reproducible evidence. Primary MVP user: developer testing an owned isolated synthetic fixture (authorized staging is future scope); secondary: QA engineer on an authorized environment.

## Core value and product boundaries

Reduce setup time while maintaining transparent evidence. Never market "AI detected a bug" merely because a generated assertion failed. Valid bug claims need a separate fixture specification or approved expected result.

## User experience

User registers an approved project origin → enters testing goal → starts run → watches discovery/planning/execution → inspects pass/test error/inconclusive/suspected finding → checks expected-vs-observed evidence → manually reviews or reruns.

## P0 backlog

| Feature | Acceptance |
| --- | --- |
| Project origin validation | Reject unauthorized destination and redirect |
| DOM/accessibility inspection | Extract buttons, links, labeled fields and title |
| Test plan generation | Strict finite JSON plan accepted or rejected |
| Playwright executor | Safe actions, typed errors and timeouts |
| Evidence | Screenshots/trace linked to failed steps |
| Finding review | Oracle provenance and rerun status shown |
| Controlled evaluation | Known-good and seeded-broken results compared |

## P1

History comparison, replay, export report, richer progress UI. Later: scheduling, cross-browser suites, CI/GitHub integration.

## Success criteria — proposed

On initial fixture set, demonstrate at least one seeded bug reproduced, zero false defect claims on its paired control in the walkthrough, 90% or more executor step completion without infrastructure errors, and evidence for all reported confirmed failures. These are thresholds to test, not claims of real performance.

## Risks and questions

Most likely failure: wrong oracle interpreted as product bug. Also browser isolation, prompt injection, flaky pages, changing LLM costs. Selected: five paired fixture families; deterministic reporting initially; no per-plan approval for a plan within the preapproved synthetic operation manifest. Unknown operations and all non-fixture submissions are refused.

## v0.2 technical baseline

Use [separate machine and review states](../architecture/findings-and-evaluation.md). Automated `verified` means an independently specified oracle violation reproduced with complete evidence; only human `accepted` yields a current confirmed defect. Basic persisted run history is P0; comparison/replay/export remain P1. Project creation references operator-approved authorization, never self-approves arbitrary origins.

Normative details: [baseline](../architecture/baseline.md), [ADRs](../README.md#architecture-decisions), and [implementation readiness](../implementation-readiness.md). Original v0.1 content is preserved in `../archive/v0.1/`; historical targets are not measurements.
