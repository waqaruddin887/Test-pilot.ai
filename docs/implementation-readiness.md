# Implementation readiness — v0.2

Date: 2026-11-08. Design contradictions are resolved as below. No application implementation, dependency installation, system configuration or browser/security/evaluation run was performed in this documentation change. “Selected” is not “verified working.”

## Resolved decisions

| Original audit | Resolution / authority |
| --- | --- |
| A01 paths/instructions | Lowercase docs/foundations, single root AGENTS.md, original files archived and checksummed; [ADR-011](adr/011-documentation-baseline.md) |
| A02 plan format | Strict Pydantic v2 plan schema 1.0.0 with ordered steps, exact targets, explicit intent, assertion oracle refs; [contract](contracts/test-plan-v1.md) |
| A03 mutation approval | Preapproved synthetic fixture operation manifests only; non-fixture submissions always denied; [policy](architecture/safety-policy.md) |
| A04 verification vs review | Machine verified separate from accepted/dismissed review; current confirmation requires both plus available evidence; [states](architecture/findings-and-evaluation.md) |
| A05 oracle input leakage | Public requirements allowed; hidden variant/defect/reference answers excluded; [protocol](architecture/findings-and-evaluation.md) |
| A06 browser privileges | Trusted supervisor/control plane and fixture-only Playwright namespace with bounded pipes; [runner](architecture/runner-protocol.md) |
| A07 capture/retention | Reviewed synthetic capture, quarantine unexpected sensitive content, 24-hour bytes/seven-day metadata; [data](architecture/data-model.md) |
| A08 missing APIs | Project/history/authorization/oracle/review resources selected; [HTTP](contracts/http-api-v1.md) |
| A09 entities | Versioned authorization/oracles, job/slot/capability/command-intent/attempt/results, manifests/reviews/usage/outbox; [data](architecture/data-model.md) |
| A10 recovery | Transactional outbox, idempotency, epochs/receipts, conservative uncertain-outcome failure; [jobs](architecture/job-lifecycle.md) |
| A11 budgets | 1–5 cases/default 3, 12 steps including assertions, 120s queue/300s active/5s cleanup; [limits](architecture/baseline.md) |
| A12 local access | Local operator session, CSRF, exact Origin/Host, loopback publication and ownership checks; [policy](architecture/safety-policy.md) |
| A13 metrics | Trial/unique rates, initial/repair validity, machine/human metrics and fixed miss denominators; [evaluation](architecture/findings-and-evaluation.md) |
| A14 fixture scope | Synthetic login rejection and cart arithmetic without real auth/payments; [scope](architecture/baseline.md) |
| A15 staged delivery | Honest 503 until capable execution exists; original run-creation acceptance remains pending, no simulated results; [baseline](architecture/baseline.md) |

## Ready for a later foundation coding pass

- [x] Canonical architecture, scope/limits, safety policy and state models selected.
- [x] All fourteen active foundations updated and original bytes preserved.
- [x] ADR-001–011 record context, decision, alternatives and consequences.
- [x] Canonical documentation-only Pydantic model, JSON Schema and matching planner example supplied.

These checkboxes record supplied design artifacts. See the change report for checks actually executed. The earlier Day 1 review remains a historical proposal; this baseline supersedes conflicting unchecked design tasks there. Application implementation requires a subsequent coding task, not automatic continuation from this documentation-only request.

## Remaining blockers by phase

| Gate | Owner | Required action/evidence | Blocks |
| --- | --- | --- | --- |
| R01 compatible toolchain | Developer | Select/pin supported Node/Python/pnpm/Pydantic/Playwright/DB-driver versions, verify browser image/package match; produce locks | Reproducible application setup, not documentation design |
| R02 Docker/host support | Developer | Docker missing on prior PATH inspection; explain installation need before changes, verify supported Linux sandbox/user namespaces/seccomp/capabilities or equivalent tested host | Compose and isolated browser runtime |
| R03 actual operator/ownership | Project lead | Configure local operator, repository/IP and fixture ownership/license; no invented attestation | Authorization provisioning and publishable assets |
| R04 fixture manifests | Developer | Choose exact service name/port/path/operation rules, reset protocol/version and expiry; create synthetic neutral-route fixtures | Any browser discovery/mutation |
| R05 sandbox implementation proof | Developer | Implement selected supervisor/namespace/pipe boundary, fixed reset control; prove denied connections including supervisor/provider/host and teardown on lease loss | Any browser execution |
| R06 provider/model and money | Project lead | Choose actual provider/model, verify structured-output support/token accounting/pricing/rate limits/terms, set positive explicit monetary caps | First live model request; fake adapters can be used offline |
| R07 oracle/fixture verification | Developer/reviewer | Author independent OracleVersions and reference tests; review and run on each control/broken variant; record disagreements | Verified findings and benchmark ground truth |
| R08 persistence/job correctness | Developer | Implement migrations/constraints, atomic outbox/budget reservation, singleton slot/capability/command-intent persistence, leases/fencing/cancel, unchanged deadlines on recovery, crash/restart/duplicate delivery tests | Reliable accepted run execution |
| R09 privacy and evidence | Developer | Implement ownership/expiry/quota/hash/manifest/deletion, fake-secret capture tests; demonstrate no credentials/cookies persisted | Evidence capture and acceptance |
| R10 API/UI checks | Developer | Implement DTO/client generation, operator session/CSRF/Host/Origin, ownership tests, accessible UI and honest unavailable states | Usable local foundation |
| R11 evaluation execution | Developer/reviewer | Freeze/shuffle protocol and development/final split, run 30 trials plus adversarial checks, report machine and human counters with denominators | Quality/accuracy and release claims |
| R12 external launch | Project lead | Separate permission/legal/vendor/security/procurement review and nonlocal egress design | External/customer/public deployment only; outside MVP |

The monetary amount, provider, runtime compatibility and actual fixture approvals cannot be inferred from documents. They remain explicit inputs, not architecture contradictions. The implementation of namespace isolation/reset and its feasibility on the chosen host is the largest technical risk; if infeasible, keep browser execution disabled and revisit ADR-005 with measured evidence.

## Implementation checkpoints (all pending)

- [ ] Scaffold the [monorepo](architecture/baseline.md), dependencies and lint/type/build commands after the user authorizes coding.
- [ ] Add Postgres migrations and real DB/Redis integration tests; no SQLite substitute for relational correctness.
- [ ] Implement minimum project/API/UI path and clearly return 503 for unavailable execution. Do not mark the original Day 1 full run path delivered prematurely.
- [ ] Port documented Pydantic contract into a backend module, pin dependency, wire schema/client drift and contextual parser/policy tests into CI.
- [ ] Implement and prove runner safety, authorization, cancellation and cleanup before visiting even fixture pages through the autonomous path.
- [ ] Implement bounded discovery/planning/execution and deterministic verification using independent oracles.
- [ ] Implement private evidence lifecycle and append-only review; only eligible findings can be accepted.
- [ ] Run the fixture and adversarial benchmark before claiming any security/accuracy gate passed.
- [ ] Record exact commands, outcomes, deferred work and risks for every milestone.

No further clarification is required to finish this documentation task. Operational inputs should be supplied when their affected implementation phase begins; no package installation or system change is implied by this checklist.

## Follow-up revalidation

The [follow-up report](reviews/2026-11-08-baseline-revalidation.md) records explicit execution-slot/capability/command-intent entities, nonrenewable recovery deadlines, one-time oracle/manifest sealing, and aligned privacy/backup/reporter wording. These refinements add no passed runtime gate; R01–R12 remain pending.
