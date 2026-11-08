# 12 — AI Evaluation & Golden Dataset Plan

**Draft v0.1. Evaluation design is ready; measurements do not yet exist.**

## Hypotheses

H1: planner produces executable schema-valid tests for fixtures. H2: independent-oracle verification catches seeded defects. H3: prompt injection and ambiguous requirements do not lead to invalid actions or fabricated confirmed bugs.

## Benchmark

Five paired fixture families (good and deliberately broken): form required field, email validation, login failure, navigation, cart total. Ten variants at one frozen commit, 3 repeats per variant = 30 proposed runs, plus adversarial test fixtures. Reference oracles must be scripted independently of the AI test planner.

## Primary metrics

- Defect recall = unique seeded defects correctly confirmed / unique detectable seeded defects.
- Finding precision = unique genuine defects confirmed / unique confirmed defect claims.
- False-positive rate = normal/control variants incorrectly called defective / total normal/control variants evaluated.
- Executor success rate = planned safe steps executed without infrastructure/locator errors / attempted safe steps.
- Reproduction rate = findings reproducing in a clean context / findings attempted.
- Schema validity rate = valid planner outputs / planner requests.
- Prompt-injection escape count = action-policy violations actually executed.
- Per-run token cost, latency and artifact completeness.
For zero-denominator metrics, show N/A instead of invented 100%.

## Proposed MVP gates

- Show at least one **independently verified** seeded defect detected and reproduced.
- No confirmed defect claim on the paired known-good demo variant.
- 90%+ successful executor step completion on the controlled fixture set.
- 100% of confirmed claims include oracle ID, raw observation, screenshot/trace and reproduction state.
- Zero executed unauthorized actions during adversarial policy tests.
These numbers are goals, not achieved scores. A 10-variant set is too small for broad statistical accuracy claims.

## Protocol

Freeze fixture source, oracle spec, planner prompt, model identifier, browser version, test objective and token caps. Run controls and broken variants in shuffled order; never reveal hidden defect labels to planner. Execute 3 independent fresh-browser trials per variant. Deduplicate by defect ID. Inspect all failed and suspicious tests manually. Save raw counters and disagreement log.

## Analysis

Break down errors into incorrect oracle, bad locator, execution timeout, application nondeterminism, reasoning mistake, infrastructure crash and unsupported user goal. Publish precision and recall with denominators, scenario-level failures and limitations. Do not optimize repeatedly on held-out cases without splitting development and final evaluation sets.

## Milestone gate

A demo is acceptable with limited measured functionality if evidence is honest. No marketing claim like "95% accurate" until a sufficiently representative benchmark supports it.