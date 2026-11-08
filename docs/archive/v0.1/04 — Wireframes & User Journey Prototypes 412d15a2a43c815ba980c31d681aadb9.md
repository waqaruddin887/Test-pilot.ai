# 04 — Wireframes & User Journey Prototypes

**Draft v0.1. Text-only conceptual wireframes; visual prototypes and usability testing pending.**

## Navigation

Projects → Create Run → Run Progress → Run Summary → Finding Details → Evidence Viewer. Settings contains approved origins, model selection and retention.

## Screen 1: Project list

Header: TestPilot AI / Projects / Runs / Settings. Content: New Project, approved domain, latest run, run health and a prominent New Run action. Empty state explains authorized testing and sample fixture.

## Screen 2: Start a run

Fields: project, approved URL path, testing objective, case-count cap, safe-action scope. Show warning that only controlled test sites are allowed. Buttons: Start and Cancel. Invalid origin shows explanatory error before enabling execution.

## Screen 3: Execution

Statuses: queued, discovering, planning, executing, verifying, completed, failed, cancelled. Step list shows case name, action, locator and elapsed time. Cancel remains usable. Planner errors appear as errors, not mysterious loading screens.

## Screen 4: Summary

Counts: passed, suspected defects, confirmed defects, test errors, inconclusive. Each finding card shows expected behavior, observed behavior, oracle source, evidence coverage and rerun status. Do not display an unqualified "100% bug-free" badge.

## Screen 5: Finding review

Tabs: Steps, Screenshot, Browser Trace, Console, Oracle. Actions: Mark reviewed, Dismiss finding, Rerun fixture. Human reviewer must see the evidence before confirming a finding.

## User journey

Select approved fixture → define goal → start run → inspect generated test cases → track execution → open failure → verify oracle and evidence → rerun → accept/dismiss. No automatic creation of external tickets in MVP.

## Edge and accessibility states

No projects; blocked URL; provider outage; invalid plan; timeout; browser crash; missing evidence; zero defects; ambiguous locator. Each has distinct copy and retry rules. Buttons keyboard reachable; focus managed after errors; status is not represented by color alone.

## Validation

- [ ]  Sketch mobile/desktop layout and error states.
- [ ]  Ask independent reviewer to find a screenshot and repro steps unaided.
- [ ]  Check that missing oracle never looks like confirmed bug.