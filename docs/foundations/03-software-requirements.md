# 03 — Software Requirements Specification (SRS)

**Technical baseline v0.2 — 8 November 2026. Design selected. See [current implementation and test evidence](../implementation-status.md); the full hardened design is not yet complete. Commercial charter/legal approval is not implied.**

## Functional requirements

| ID | Requirement | Test |
| --- | --- | --- |
| FR01 | Create project and approved origin | API integration |
| FR02 | Reject unsupported schemes/hosts/redirections | Security negative tests |
| FR03 | Extract page accessibility and DOM outline | Fixture snapshot |
| FR04 | Produce schema-valid finite test plans | JSON schema cases |
| FR05 | Block unsupported/unsafe/ambiguous actions | Policy tests |
| FR06 | Run navigate/click/fill/visible and URL assertions | Browser E2E |
| FR07 | Capture step result, screenshot, trace and errors | Artifact inspection |
| FR08 | Separate machine pass/suspected/verified/test_error/inconclusive from human unreviewed/accepted/dismissed | Classifier tests |
| FR09 | Reproduce suspected failure in clean browser context | E2E rerun |
| FR10 | Display result/evidence with steps and provenance | UI test |
| FR11 | Cancel jobs and close browser worker | Worker integration |
| FR12 | Redact sensitive data before LLM/logging | Privacy tests |

## Nonfunctional requirements — starting values

1–5 cases (default 3), 1–12 ordered steps per case including assertions. Queue deadline 120 seconds; active deadline 300 seconds from lease claim including discovery, planning, repair, execution and reproduction; separate cleanup grace 5 seconds. Navigation max 30 seconds, other steps max 10 seconds, always bounded by remaining deadline. Planner max 30 seconds per call, max 2 calls including one structural repair. No automatic provider/step retry. Use the complete ceilings in the baseline; operators can lower them. Raising ceilings requires a design change.

## Failure modes and fallback

LLM unavailable → clearly failed planning state; deterministic smoke is only an explicit separately requested run mode, not fabricated findings. Invalid JSON → reject. Ambiguous locator → test error. Off-allowlist navigation → blocked. Browser crash → failed with partial evidence. Missing oracle → inconclusive observation rather than confirmed defect. Storage failure → no confirmed bug if required evidence absent.

## Data and privacy

No login credentials or customer PII in MVP. Isolate runs; access-controlled artifacts; no secrets in logs. Accessibility: keyboard controls and textual status labels.

## Interfaces

Projects, runs, cases, findings, reviews, oracles, artifacts and cancellation are separate typed API resources; exact contracts in document 10 and the HTTP contract.

## Traceability

A requirement counts as done only when supported by a runnable test and linked implementation. Date and performance numbers are initial design targets.

## v0.2 technical baseline

FR04 uses [plan 1.0.0](../contracts/test-plan-v1.md); FR01/02/05 use the [single safety policy](../architecture/safety-policy.md); FR08–10 use the [verification/review contract](../architecture/findings-and-evaluation.md); FR11 uses the [job lifecycle](../architecture/job-lifecycle.md). Missing evidence prevents automated verification or new human acceptance. Each FR still needs linked implementation and runnable tests; none is complete from documentation alone.

Normative details: [baseline](../architecture/baseline.md), [ADRs](../README.md#architecture-decisions), and [implementation readiness](../implementation-readiness.md). Original v0.1 content is preserved in `../archive/v0.1/`; historical targets are not measurements.
