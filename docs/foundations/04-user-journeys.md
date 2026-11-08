# 04 — Wireframes & User Journey Prototypes

**Technical baseline v0.2 — 8 November 2026. Design selected; implementation and test evidence pending. Commercial charter/legal approval is not implied.**

## Navigation

Projects → Create Run → Run Progress → Run Summary → Finding Details → Evidence Viewer. Settings displays operator-configured fixture authorization, fixed baseline retention, and planner availability. These controls cannot grant new target scope or raise safety ceilings during a run.

## Screen 1: Project list

Header: TestPilot AI / Projects / Runs / Settings. Content: New Project, approved domain, latest run, run health and a prominent New Run action. Empty state explains authorized testing and sample fixture.

## Screen 2: Start a run

Fields: project, approved URL path, testing objective, case-count cap and selected preauthorized fixture operation scope. Show warning that only controlled test sites are allowed. Buttons: Start and Cancel. Invalid origin shows explanatory error before enabling execution.

## Screen 3: Execution

Statuses: queued, discovering, planning, executing, verifying, completed, failed, cancelled. Step list shows case name, action, locator and elapsed time. Cancel remains usable. Planner errors appear as errors, not mysterious loading screens.

## Screen 4: Summary

Counts: passed cases, suspected findings, automatically verified findings awaiting review, current human-confirmed defects, test errors and inconclusive observations. Show machine assessment and review state separately. Each finding card shows expected behavior, observed behavior, oracle source, evidence coverage and rerun status. Do not display an unqualified "100% bug-free" badge.

## Screen 5: Finding review

Tabs: Steps, Screenshot, Browser Trace, Console, Oracle. Actions: Accept verified finding, Dismiss, Reopen review, Rerun fixture. Acceptance requires verified machine assessment, unexpired complete evidence, oracle provenance and explicit inspected-manifest acknowledgment. Review appends a record; rerun creates linked new evidence.

## User journey

Select approved fixture → define goal → start run → inspect generated test cases → track execution → open failure → verify oracle and evidence → rerun → accept/dismiss. No automatic creation of external tickets in MVP.

## Edge and accessibility states

No projects; blocked URL; provider outage; invalid plan; timeout; browser crash; missing evidence; zero defects; ambiguous locator. Each has distinct copy and retry rules. Buttons keyboard reachable; focus managed after errors; status is not represented by color alone.

## Validation

- [ ]  Sketch mobile/desktop layout and error states.
- [ ]  Ask independent reviewer to find a screenshot and repro steps unaided.
- [ ]  Check that missing oracle never looks like confirmed bug.

## v0.2 technical baseline

Display “historically accepted; evidence unavailable” after evidence expiry, not an unqualified current confirmation. No browser/model capability shows a clear unavailable error. Operator/session/CSRF checks apply to mutation controls. Textual status, keyboard access, focus/error management remain P0. See [HTTP resources](../contracts/http-api-v1.md).

Normative details: [baseline](../architecture/baseline.md), [ADRs](../README.md#architecture-decisions), and [implementation readiness](../implementation-readiness.md). Original v0.1 content is preserved in `../archive/v0.1/`; historical targets are not measurements.
