# Verification, human review and evaluation

Accepted 2026-11-08. [ADR-008](../adr/008-verification-review.md) and [ADR-010](../adr/010-evidence-evaluation.md).

## Separate axes

Step outcomes are `passed`, `assertion_failed`, `test_error`, `inconclusive`, `not_executed`; a policy denial is a test_error with category `policy_blocked`. Case assessment uses the table below. Run completion describes workflow termination, never a product quality verdict.

| Machine assessment | Meaning |
| --- | --- |
| pass | All executed requirement-backed assertions passed and all required steps completed |
| suspected | At least one valid independent-oracle assertion was violated, but evidence or reproduction is pending |
| verified | Same oracle violation observed initially and in one fresh-context/reset-fixture reproduction, with complete integrity-checked evidence for both |
| test_error | Locator, policy, infrastructure, capture, deadline or unsupported-operation error prevents reliable assessment |
| inconclusive | No reliable independent oracle, exploratory-only plan, contradictory/flaky observation, or reproduction cannot establish the same violation |

Derive a finding for each violated oracle/case; multiple unrelated oracles are not merged. A valid verified finding may coexist with another case's test_error. An error affecting the purported violation prevents verification; unrelated later errors do not erase already recorded observations. Once finalized, assessment is immutable; new execution is a new attempt/run, not an edit to old evidence. Exploratory checks never become pass or verified product assessments merely because a model expectation matched or failed.

Human review state is independently `unreviewed`, `accepted`, or `dismissed`. Append Review records with actor, timestamp, evidence-manifest hash and reason; optimistic version checks prevent racing decisions. No human can turn a test_error or missing-oracle result into verified. Acceptance requires current `verified`, oracle version, complete unexpired evidence and a record that the operator inspected the manifest/evidence; simply viewing a page is insufficient. Dismissal does not change raw observations or machine assessment. Reopening appends an unreviewed decision; prior reviews remain in history. Review actions do not repeat browser work.

The displayed **confirmed defect** is derived only when machine=verified and latest human review=accepted. Display `verified — awaiting review`, `suspected`, `dismissed` and `inconclusive` distinctly. `accepted` is a human disposition, not a machine outcome. Expired/deleted/corrupt evidence disables new acceptance and displays “historically accepted; evidence unavailable” on prior accepted records. Do not present such records as currently inspectable confirmed claims or export them without this qualification.

## Oracles and reproduction

Oracle versions are written/reviewed independently of the LLM. They bind a fixture version, expected behavior, supported deterministic assertion kind, expected exact locator or path, and severity rationale. A plan references an exact version; validator checks the assertion equals the oracle's permitted assertion, rather than trusting matching prose or a plausible ID. An observable assertion failure must be attributable to application behavior, not blocked navigation, missing fixture, bad locator or missing evidence.

Reproduce once per candidate case, using the same sequence, inputs and oracle versions in a fresh browser context and freshly reset isolated fixture with the same seed. Append an ExecutionAttempt of kind reproduction referencing the initial attempt, with independent step outcomes and artifacts. A generic page reload is insufficient. Reference Playwright scripts validate the fixture benchmark independently and are not the agent's reproduction or generated plan.

Required confirmation evidence: initial and reproduction observations (expected/actual values, action/step IDs, timing), oracle provenance, failed-assertion screenshot and attempt trace for both, manifest hashes, reset/seed/browser/fixture/policy provenance and successful reproduction outcome. Storage failures prohibit verification; if reproduction budget is exhausted, retain suspected with reason `reproduction_not_attempted`, not verified.

## Golden benchmark and leakage boundary

Keep five good/broken pairs: required field, malformed email, simulated login rejection, navigation and cart arithmetic. Ten variants × three fresh trials = thirty proposed runs, plus adversarial fixtures. Public requirements and their expected application behavior ARE planner input. Hidden variant labels, defect IDs, expected detection/severity, golden scripts, reference results and expected agent outputs are NOT. Route/title must not expose good/broken labels; harness selects variant behind a neutral route. Oracle IDs and public requirements are identical across a pair.

Freeze source commit, fixture/oracle versions, seed, objectives, prompt/schema/model/browser/image hashes, limits and scoring code; shuffle trials with a recorded seed. Designate development versus final evaluation manifests before tuning; report the small held-out coverage honestly. Validate reference assertions on both variants before scoring agent detections. Independent manual oracle review remains a readiness gate; until then mark results provisional.

## Scoring protocol

Report machine verification and human-confirmed metrics separately so a reviewer cannot hide incorrect automated claims by dismissing them. Persist all raw counters and all outcomes, including timeouts/exclusions.

- Machine precision = unique real defects among verified claims / unique verified claims. Human-confirmed precision uses currently evidence-complete verified+accepted claims; also disclose all historical acceptances and unavailable-evidence counts.
- Recall = unique seeded defects detected / unique detectable seeded defects fixed in the manifest. Report machine and accepted versions separately. An error/miss remains in the recall denominator; do not remove difficult cases after seeing output.
- Deduplicate across repetitions by harness defect ID; control claims use `(scenario, oracle_version)` as claim identity. Report per-trial hits and repeat consistency alongside aggregate deduplication.
- Control false-positive rate = control trials with ≥1 verified claim / completed or attempted control trials in manifest; give accepted-claim rate too. Separately report unique control variants falsely flagged / evaluated control variants. List nonexecuted trials, so failures cannot imply correctness.
- Executor success = attempted safe steps completed without locator/infrastructure/policy errors / all attempted safe steps. Assertion failures attributable to application behavior count as executor completion. Show rejected plans/steps and unattempted steps separately; they cannot inflate execution success.
- Schema validity: initial valid outputs / initial requests; repair valid outputs / repair requests; final accepted plans / planning sessions. Contextual policy/oracle acceptance is a separate rate from structural validity.
- Reproduction rate = candidates reproducing the same oracle violation / candidates with a reproduction attempted; list unattempted candidates and why.
- Injection escape count = unauthorized actions actually executed; include attempted/rejected injections. Show token usage/cost, latency, artifact completeness and zero-denominator N/A.

MVP targets remain: at least one independently verified and human-accepted seeded defect reproduced; none falsely confirmed on its paired control; ≥90% executor completion; complete evidence for every current confirmed claim; zero executed unauthorized actions. These are gates to measure, not achieved results or broad accuracy claims.
