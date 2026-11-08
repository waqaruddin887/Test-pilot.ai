# Durable execution jobs and recovery

Accepted 2026-11-08. [ADR-004](../adr/004-queue-worker.md), [ADR-007](../adr/007-durable-jobs.md). Postgres controls lifecycle; Redis/RQ provides at-least-once delivery of one fixed function with job/run IDs, using JSON serialization. Redis is private and accepts writes only from trusted dispatcher/worker credentials.

## Admission and HTTP idempotency

POST /api/runs and POST /api/runs/{id}/rerun require an Idempotency-Key (1–128 printable ASCII characters). Scope uniqueness to operator, route operation and key. Hash the validated canonical request plus referenced source run for reruns; hold a unique-key transaction lock. Same key/payload returns original resource and original response, including terminal runs; different payload gives 409. Keep keys seven days, return expires_at and document that reuse after expiry may create a new run. A retry of an old key returns its historical run even if current admission is disabled; it never resumes it.

For a new key: check operator, authorization/revocation, limits/storage/budget and fresh capable-worker heartbeat (≤15 seconds old). Missing capability returns 503 without creating queued work; live planning without provider/caps is similarly unavailable. In one transaction reserve budget/quota, create Run(queued), ExecutionJob(pending), IdempotencyRecord and OutboxEvent. Return 202 only after commit. An explicit smoke-mode run uses its own worker capability and never silently replaces planned mode.

## Dispatch, claim and deadlines

Dispatcher sends deterministic RQ job ID `(job_id, dispatch_generation)`; publishing may duplicate after an uncertain response. Outbox is marked published after enqueue acknowledgment. Backoff 1, 2, 4, 8, 16 then 30 seconds (capped), stopping at the 120-second queue deadline. Redis failure never undoes an accepted Postgres run. Reconciler scans pending/published jobs every five seconds and safely redispatches work with no active lease. Duplicate queue delivery is expected, not interpreted as new execution.

Worker claims job and the singleton active-run lease transactionally. Increment lease_epoch; set heartbeat every five seconds, lease expiry 15 seconds, active run deadline started_at+300 seconds. Persist discovery/planning/execution stages with version checks and ordered events. Revalidate authorization on claim and per step. Keep the active global lease through teardown; expiration alone cannot allow another browser while the old process may still be alive. The supervisor must acknowledge old runner termination before a new active lease executes browser work.

ExecutionSlot is the singleton lease row; WorkerCapability supplies the compatible worker heartbeat. Claim and release lock the slot and ExecutionJob together. On the single permitted pre-side-effect recovered claim, retain the original Run.started_at, deadline_at, queue_expires_at and budget reservation; increment recovered_claims and lease_epoch only. Recovery never restarts the 300-second clock or grants additional planner calls. If the original active deadline has elapsed, fail and clean up rather than reclaim. The queue deadline governs jobs that never started; an already-started recovered job uses its original active deadline.

Run states: queued → discovering → planning → executing → verifying → completed; any nonterminal state may become failed or cancelled. Terminal states do not transition back. Smoke runs still traverse planning with an explicit `planner_kind=deterministic_smoke` event. A run can complete with suspected/inconclusive findings; human review happens afterward. Queue expiry fails with `queue_timeout`; active deadline fails with `run_timeout`, preserving partial results and scheduling cleanup. Cleanup has a separate five-second maximum; deadline exhaustion never creates extra execution budget.

## Retry rules

| Situation | Rule |
| --- | --- |
| Outbox enqueue/network uncertainty before claim | Safe redispatch of same job identity until queue expiry |
| Worker dies before any runner/provider side effect | Reconcile, bump epoch only after old worker/supervisor fencing; at most one recovered claim before expiry |
| Invalid model JSON/structural schema | One bounded repair request; preserve initial failure counter; no unbounded regeneration |
| Model emits unsafe action/unknown oracle | Reject plan; no repair that might disguise policy violation; fail planning with safe diagnostic |
| Provider outage/429/timeout/unknown response | No automatic transport retry or smoke substitution; fail planning, retain uncertain usage reservation |
| Locator/assertion/policy/step failure | No automatic step retry outside deterministic bounded assertion polling; record typed outcome |
| Candidate oracle failure | One explicit reproduction attempt in verifying stage, with clean context and reset fixture; not a transport retry |
| Worker/browser/supervisor crash after side effect may have begun | Stop/fence old runner, fail run interrupted, retain safe partial evidence; never resume/replay mutations automatically |

Unknown side effect includes a sent provider request, runner prepare/execute command, or absent execution receipt. Do not infer safety from missing DB results. The worker writes intended command/attempt record before sending. Run recovery from that point is conservative. Rerun always creates a new linked run with renewed authorization, quota and budgets and an explicit user request; it does not overwrite prior observations.

JobCommand persists command identity, payload hash, epoch and acknowledgment/uncertainty before supervisor transmission; PlannerRequest records provider intent before transmission. A prepared intent left by a crashed process is treated as potentially sent unless a trusted receipt establishes otherwise. Recovery compares persisted intent with supervisor receipts; absence of an acknowledgment never proves the operation did not happen. Do not dispatch a command until the intent commit succeeds.

## Cancellation and races

Cancel is idempotent. For queued jobs, transactionally set cancelled and suppress pending outbox dispatch; a late delivery exits without work. For active jobs, persist cancel_requested_at/event, revoke capability, notify supervisor and stop work at the next safe boundary. After five seconds the supervisor kills the run process group and releases fixture resources. Mark cancelled only after teardown acknowledgment; if termination cannot be established, mark failed `cleanup_unconfirmed`, disable admission and raise a safe operator error until reconciliation proves cleanup. The cancelled flag is not evidence of process termination by itself.

Cancel of a terminal run returns its unchanged state and `already_terminal=true`. Complete/fail/cancel writes lock the run/job and compare version/epoch. If cancel request commits before completion, completion cannot win; terminate and cancel. If completion committed first, cancel is a no-op. Delayed provider/runner results from a fenced epoch cannot mutate terminal data or refunds. Budget accounting may append a usage reconciliation record without changing terminal state.

## Reconciliation and crash recovery

Every five seconds: expire queue waits, check worker heartbeats/leases, query supervisor status, fence stale epochs, stop orphans, resolve staged artifact writes and update outbox records. A stale worker alone does not justify replay. Safe pre-side-effect recovery is limited to one new claim; any uncertain execution fails interrupted. Supervisor loss stops admission until all prior run processes/namespaces are proven terminated. Redis restart reconstructs eligible pending work from Postgres; it never replays terminal jobs. DB outage causes runner capability to expire, then teardown; no new work proceeds on stale authorization.

Expired/corrupt/missing evidence blocks verification. Disk full stops capture/execution with a typed error and private cleanup. Test commit/enqueue gaps, duplicate deliveries, lost replies, epoch fencing, cancel-versus-complete, provider usage uncertainty, orphan termination and Redis/DB/supervisor restarts before enabling browser runs. Neither RQ nor an idempotency key promises exactly-once external side effects.
