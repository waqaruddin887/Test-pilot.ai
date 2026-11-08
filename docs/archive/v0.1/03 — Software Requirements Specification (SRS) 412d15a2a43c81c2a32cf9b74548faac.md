# 03 — Software Requirements Specification (SRS)

**Draft v0.1. Proposed requirements for MVP.**

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
| FR08 | Classify pass, suspected, confirmed, test error, inconclusive | Classifier tests |
| FR09 | Reproduce suspected failure in clean browser context | E2E rerun |
| FR10 | Display result/evidence with steps and provenance | UI test |
| FR11 | Cancel jobs and close browser worker | Worker integration |
| FR12 | Redact sensitive data before LLM/logging | Privacy tests |

## Nonfunctional requirements — starting values

Max 5 cases per run; max 12 actions per case; default total run deadline 5 minutes; browser navigation timeout 30 seconds; bounded retries; strict request and completion token caps. Planner timeout 30 seconds; one schema-correction retry. All values configurable and evaluated before release.

## Failure modes and fallback

LLM unavailable → deterministic smoke checks or clearly failed planning state, not fabricated findings. Invalid JSON → reject. Ambiguous locator → test error. Off-allowlist navigation → blocked. Browser crash → failed with partial evidence. Missing oracle → inconclusive observation rather than confirmed defect. Storage failure → no confirmed bug if required evidence absent.

## Data and privacy

No login credentials or customer PII in MVP. Isolate runs; access-controlled artifacts; no secrets in logs. Accessibility: keyboard controls and textual status labels.

## Interfaces

Projects, runs, cases, findings, artifacts and cancellation are separate typed API resources; exact contracts in document 10.

## Traceability

A requirement counts as done only when supported by a runnable test and linked implementation. Date and performance numbers are initial design targets.