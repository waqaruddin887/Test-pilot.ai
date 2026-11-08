# 06 — Datasheet for Golden Fixture Dataset

**Technical baseline v0.2 — 8 November 2026. Design selected; implementation and test evidence pending. Commercial charter/legal approval is not implied.**

## Purpose

Evaluate whether the agent identifies reproducible, requirement-backed defects while avoiding false positives on known-good versions.

## Proposed fixtures

Five scenario pairs: required-field validation, invalid-login rejection, malformed email, broken navigation and incorrect cart arithmetic. Each pair has a control and defective variant created with synthetic inputs, served through neutral routes without variant-revealing labels. Login rejection is simulated without real sessions; cart arithmetic has no payment/checkout. Keep stable route, semantic fixture version, seed, commit hash and documented oracle.

## Schema

A record contains: case_id, fixture_version, route, variant, objective, steps, oracle_type, expected_behavior, observable_assertion, defect_id (hidden from agent), expected_detection, expected_severity, source_commit and privacy_class.

## Annotation rules

"Defect" means observed behavior violates independently written fixture requirements. "Non-defect" means conformant behavior. "Inconclusive" when no reliable assertion is possible. Executor/locator failures receive their own label. Severity reflects actual application impact, not AI confidence.

## Independent verification

Each fixture must have an authored reference Playwright assertion that does not use the AI planner. Confirm the defect exists by running the reference check on control and broken variant. Review every fixture on creation and after code changes.

## Evaluation hygiene

Supply public independent fixture requirements and their expected application behavior to the planner. Never supply hidden defect IDs, good/broken labels, expected agent outputs/detection/severity, reference scripts or reference results. Report both correct and incorrect defect classifications. De-duplicate findings by defect ID before scoring. Run each fixture multiple times (proposed 3) to measure flakiness; log versions, timestamps and seeds. Publish failures and exclusions, not only successes.

## Known limitations

Synthetic fixtures do not establish performance on production SPAs, payment flows, dynamic authentication, multiple browsers or multilingual apps. No general accuracy claim is justified from five fixtures.

## Ready gate

- [ ]  10 fixture variants implemented and behavior verified.
- [ ]  Reference oracles reviewed independently of LLM output.
- [ ]  Evaluation scripts freeze input versions and prompts.
- [ ]  Benchmark report includes false positives and uncertain outcomes.

## v0.2 technical baseline

The full dataset record is harness-only; construct a separate allowlisted planner projection. Public oracle IDs/versions and requirements are identical across paired variants. Expected severity and defect_id remain hidden labels. Reproduction is the agent sequence in clean/reset state; reference assertions are independent ground truth. [Scoring protocol](../architecture/findings-and-evaluation.md) separates machine verification and accepted claims, fixes denominators and records repeated trial consistency.

Normative details: [baseline](../architecture/baseline.md), [ADRs](../README.md#architecture-decisions), and [implementation readiness](../implementation-readiness.md). Original v0.1 content is preserved in `../archive/v0.1/`; historical targets are not measurements.
