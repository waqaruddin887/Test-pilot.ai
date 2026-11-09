# Security implementation status

Date: 2026-11-08. Scope: **offline, repository-owned synthetic fixtures only**.
This is a restricted development demo. It is not approved for arbitrary/customer
sites, public hosting or production secrets. Original threat-model release gates
are not all passed merely because this mode works.

| Control | Implementation / actual proof | Remaining limits |
| --- | --- | --- |
| Destination authority | API accepts fixed fixture references, exact paths; no submitted origin. Unexpired/unrevoked authorization required. Unknown methods/URLs/aliases/queries rejected by policy tests. | No networked or externally authorized targets supported. |
| Network isolation | New user/network namespace; no connected interface or general DNS; minimal mount/PID namespace. Direct socket attempts to loopback, metadata, private/public IPv4 and IPv6 denied in actual runner. Off-origin browser navigation rejected. | Full networked-fixture firewall/DNS/redirect/subresource/alternate-channel release matrix is unfinished. No arbitrary-site safety claim. |
| Privilege separation | Clean runner environment; normal runner mounts only browser/contracts/policy/public requirements and one neutral fixture tree. Private home, API/planner, DB, queue and provider secrets absent. Chromium sandbox enabled. | Dependency directories and /usr are read-only mounts. Not a custom hardened container image or escape-proof security certification. |
| Code and actions | Strict discriminated schema, bounded JSON parser, exact finite operations/values, no eval/model tools/CSS/XPath/shell. Injected text cannot expand policy. | Live-provider prompt injection has not been evaluated. |
| Resource bounds | 300s active deadline, 120s queue expiry, <=40s child commands, CPU/file/fd/core limits, 256 MiB tmpfs, bounded JSON/evidence, 1 GiB artifact store. RSS <=1 GiB and <=64 process watchdog, 100ms polling. | Polling can overshoot and is not a cgroup hard cap. Per-process CPU limits are not aggregate CPU accounting. Cgroup/seccomp/image hardening and stress/escape testing remain release gates. |
| Cancellation/recovery | Supervisor kills owned process group, waits for exit; PID namespace and die-with-parent protect child lifetime. Actual cancellation and fresh subsequent launch tested. Interrupted jobs fail without replay. Singleton host file lock + unique active DB slot. | No distributed fencing, signed capability renewal, RQ/outbox fault matrix or independently certified orphan recovery. Use one worker on one host/data directory only. |
| Local operator | Hashed eight-hour sessions, HttpOnly/SameSite=Strict cookie, exact Host/Origin, mutation CSRF, separate CLI bearer; tests executed. Bind loopback. | Single operator only. No public auth, role model, bootstrap rate limiter or multi-tenant ownership claim. Same-OS-user attackers are outside this development boundary. |
| Evidence | Synthetic screenshots/traces only; private UUID files, checksum/expiry/download checks, atomic publication, 24h byte TTL, 7d metadata TTL. Expired evidence blocks acceptance. Tests exercised review races/expiry/deletion. | No generic trace redaction/quarantine solution. Physical deletion requires running worker; no backup/export. Local privileged tampering cannot be ruled out by hashes. Some relational ownership is enforced in application code rather than composite database constraints. |
| Finding integrity | Public versioned independently authored oracles, separate initial/reproduction attempts, complete manifest, separate append-only human review. Unknown/mismatched oracles rejected. Human oracle review starts pending. | No independent human review performed in evaluation. Machine/human confirmation metrics therefore stay zero/N/A. Automated test review records are not human signoff. |

The synthetic page receives no real authentication state, form secrets, customer
personal information or provider content. Its permitted inputs are fixed fake
values. Raw traces/screenshots never enter planner input. New fixtures that add
cookies/authentication/sensitive data or external requests require review and tests;
this implementation is not a general sanitizer for hostile authenticated websites.

Provider adapter, pricing/terms, token/spend reservations, the full intended PostgreSQL model and Redis/RQ behavior, deployment/container scans and the complete v0.2
supervisor protocol are deferred. Do not expose the API publicly or expand URL
scope while any of those release boundaries are unproved.
