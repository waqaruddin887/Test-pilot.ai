# Planner and isolated browser runner

Accepted 2026-11-08. [ADR-005](../adr/005-browser-isolation.md). Logical separation is finalized; the concrete sandbox implementation and its negative tests remain a pre-browser gate.

## Privileges and topology

FastAPI serves the single operator and talks to Postgres. A trusted RQ orchestrator loads run policy, invokes the provider adapter, validates a finite plan, coordinates runner attempts and persists results. The planner has no tool interface and cannot contact or operate a browser. The optional reporter is deferred; deterministic reports consume sanitized evidence only.

Use a trusted runner supervisor with a narrow authenticated control endpoint reachable only by the orchestrator. It spawns one unprivileged Playwright runner process in a distinct network/process/mount namespace inside the runner service. The browser and Playwright process share only the fixture namespace, never the supervisor's control network. Commands/results cross bounded anonymous pipes inherited from the supervisor; browser cannot open those as network endpoints. The supervisor owns watchdog/teardown and performs no rendering of page content. No raw CDP/debug port or generic shell/evaluate command exists.

The fixture namespace has a pinned address/port allowlist with all other outbound traffic denied, no general DNS, and no route back to supervisor/worker/API/Postgres/Redis/provider/host. Fixture runs under its own unprivileged identity with no secrets. Browser runner has ephemeral storage, no host mounts, no provider/DB/queue keys, no benchmark labels and no reference scripts. Supervisor service has no DB/provider keys or Docker socket either. Provision required namespaces/rules only in an explicitly reviewed sandbox setup; avoid granting broad privilege to the web/API/worker. If the host cannot enforce the namespace separation, browser startup fails closed. No ordinary shared Compose bridge is claimed to satisfy directed isolation.

Provider egress is restricted to the configured provider endpoint from the trusted planner path. Use service-specific credentials and outbound destination rules. API/web need no Internet access at runtime. This design can initially run on a supported Linux Docker host after capability/seccomp verification; other platforms require equivalent tests. No system changes are performed by these documents.

## Protocol v1

Authenticated orchestrator→supervisor requests carry protocol_version=`1`, run_id, job_id, lease_epoch, attempt_id where applicable, command_id, policy_sha256, capability and deadline. Capability is a signed, short-lived envelope issued by the trusted orchestrator containing only that run/attempt/epoch, pinned destination, operation-manifest hash and allowed commands. Supervisor validates signature, payload bounds, deadline and epoch; runner validates policy again. Keys stay in trusted orchestrator/supervisor, never page state. Renew the lease/capability every five seconds; capability lasts at most 15 seconds and cannot outlive run deadline. Lost renewal stops the runner. Revocation/cancellation is pushed immediately and expires automatically if channel fails.

| Command | Permitted body and result |
| --- | --- |
| prepare | Fixed fixture lease/reset version/seed and isolation policy; supervisor establishes clean fixture sandbox; returns reset receipt/hash, not arbitrary shell output |
| discover | Canonical target_path and outline limits; returns bounded selected accessibility metadata and safe diagnostic status |
| execute_case | Fully validated canonical case, immutable policy and trusted resolved oracle assertions; returns step observations, typed errors, artifact descriptors and sequence acknowledgments |
| collect_artifact | Server-issued descriptor ID for the active attempt; bounded streamed bytes only, no arbitrary path read |
| cancel | Run/job/epoch, no arbitrary process ID; terminates only that supervised run |
| status | Active job/epoch, heartbeat and safe execution receipt; no unrestricted process inspection |

Fixed fixture reset operations are owned by the supervisor, invoked through a protected fixture-control channel before browser context creation; fixture pages cannot reach that channel. The exact control implementation must be proved by tests before fixture mutations. Protocol JSON is capped at 256 KiB, recursively bounded, with extra properties rejected. Artifact streams have per-file and per-run quotas; received bytes cannot select filenames or executable processing. Error envelopes expose code, safe message, command/step ID and partial results, never secrets or stack traces to the UI.

## Fencing and uncertain execution

Supervisor retains `(job_id, lease_epoch, command_id, payload_sha256)` receipts for the attempt lifetime. Duplicate identical commands return existing status/results and never re-execute; changed payload with the same ID conflicts. Reject old epochs. Orchestrator queries status after a dropped reply; it must not resend under a new command ID to repeat actions. If supervisor loses its receipts or cannot establish the old runner is stopped, terminate the run as failed/interrupted, quarantine pending outputs and require explicit new run. No exactly-once browser side-effect guarantee is claimed.

Every persisted result is checked against the current DB job epoch and attempt. Ingestion from an old worker/epoch is rejected even if bytes look valid. Closing one browser context is not sufficient cleanup: stop the process group, release namespace/fixture lease, discard storage and record teardown before another active run is admitted.

## Required proof before enablement

Test malicious page/network traffic from the actual browser namespace: host gateway, loopback, metadata, internal services, provider and supervisor must be unreachable while fixture access works. Test redirect/subresource/popup/WebSocket/service-worker bypasses, injected tool/code output, protocol size/auth/replay errors, lease expiry, lost command replies, supervisor restart and forced termination. Verify non-root browser sandbox, seccomp, dropped capabilities, read-only root, tmpfs/CPU/RAM/PID limits and lack of host mounts. Design acceptance is not passing these tests.
