# Measured deterministic fixture evaluation

Recorded 2026-11-09. This is a **development deterministic smoke baseline**, not a
live-LLM evaluation, held-out benchmark, human validation or general accuracy claim.

Raw final measurement: [latest.json](../evaluation/results/latest.json).
Frozen manifest: [smoke-v1.json](../evaluation/manifests/smoke-v1.json).
Measured backend: `cbd2a9f8fc8ed6c76866760b0e5e8a59c8b36724`; exact source-file,
fixture, requirement and manifest hashes are recorded in the raw result. Subsequent
local cancellation compare-and-swap hardening changed API/domain/worker lifecycle
code only; browser, planner, policy, fixture bytes and scoring remained unchanged.
Those final lifecycle changes were independently covered by the 64-test regression
suite. Do not describe this timing as a fresh measurement of a later full stack.

Ten independent handwritten browser reference checks ran first: all five controls
conformed and all five seeded variants violated their requirement. Thirty shuffled
trials followed (10 variants × 3 repeats, seed 20261108), each with discovery and a
fresh isolated initial browser. Every candidate had one additional fresh-process/
context static-fixture reproduction. Hidden variant/defect/reference labels were
not supplied to the planner; public requirements were. All five fixtures are
synthetic development examples; there is no independent held-out split.

| Measurement | Observed numerator / denominator |
| --- | --- |
| Schema-valid initial plans | 30 / 30 |
| Contextually accepted plans | 30 / 30 |
| Safe executor step completion | 153 / 153, including 51 reproduction steps |
| Trial execution errors | 0 / 30 |
| Unique seeded families with reproduced candidates | 5 / 5 |
| Candidate precision against scripted ground truth | 5 / 5 unique candidate claims |
| Control trials falsely flagged | 0 / 15 |
| Unique control variants falsely flagged | 0 / 5 |
| Successful reproductions | 15 / 15 attempted |
| Candidates with both screenshot/trace pairs captured and hashed | 15 / 15 |
| Machine verified claims | 0 (independent human oracle review pending) |
| Machine verified recall | 0 / 5 |
| Machine verified precision | N/A, zero verified claims |
| Human confirmed claims | 0 |
| Human confirmed precision | N/A, zero confirmed claims |
| Live model/provider calls | 0 |
| LLM tokens / estimated API cost | N/A, no model invoked |
| Median trial latency | 5.261 seconds |
| Whole evaluation including reference checks | 187.437 seconds |

No repairs were requested by the deterministic planner; repair validity is N/A.
There were no excluded or unexecuted trials in the completed final measurement.
Assertion failures attributable to seeded application behavior count as completed
executor steps, not infrastructure errors. Captures were hashed at execution;
benchmark byte payloads were discarded rather than retained as indefinitely
reviewable evidence. The application workflow/evidence tests separately exercised
actual persisted screenshots/traces, integrity/expiry, oracle review and acceptance.

Policy negatives are a separate suite: five direct socket destinations were denied
inside the actual network namespace; three fixed off-origin browser navigations
were rejected with zero successful unauthorized navigations. Invalid schemas,
invented oracles, unsafe paths/values and injected instruction text were tested
outside a live model. This does not measure live-LLM prompt-injection resistance
or the full networked-target bypass matrix.

The first completed development run is preserved in
[initial-baseline.json](../evaluation/results/initial-baseline.json) (same detection
counts; median 5.318s). A subsequent attempt aborted during reference checks because
an exiting child raced a /proc watchdog read. Its failure and unknown partial
reference count are retained in
[interrupted-evaluation.json](../evaluation/results/interrupted-evaluation.json).
The watchdog was fixed, a focused regression added, and the benchmark rerun to
produce latest.json. The aborted attempt had no scored trial outputs; it was not
silently relabeled successful or used to remove a difficult scenario.

These perfect candidate counts only demonstrate the tiny deterministic controlled
set. Independent human oracle review, live-provider trials, broader applications,
held-out variants, real PostgreSQL/queue behavior and hardened deployment are still
required before expanding any product-quality claim.
