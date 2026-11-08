# Architecture and requirements resolution — exact change report

> Historical initial resolution report. The [follow-up revalidation](2026-11-08-baseline-revalidation.md) records subsequent clarifications and its own exact change set. The path counts below describe the original resolution pass.

Date: 2026-11-08. Technical baseline v0.2 selected under the user's architecture-resolution request. No application code, dependency installation, service startup or system-level configuration change was made. Pydantic declarations are documentation specifications; their generated JSON Schema is a documentation artifact.

## Finalized technical decisions

- One strict Pydantic v2 plan contract 1.0.0: ordered action-discriminated steps, exact target variants, explicit requirement/exploratory intent, assertion-level versioned oracle refs and bounded required fields. Generated schema is derived, not an alternative format.
- One synthetic-fixture authorization policy: expiring operator-approved origins/paths/operations, live revocation, no approval override for non-fixture actions, runtime URL/action/connection enforcement.
- Separate machine pass/suspected/verified/test_error/inconclusive from human unreviewed/accepted/dismissed. Current confirmed claims require verified + accepted + available complete evidence.
- PostgreSQL entities, ownership constraints and evidence lifecycle finalized logically: versioned authorization/oracles, execution jobs/attempts/results, artifacts/manifests, append-only reviews, outbox/idempotency and token/cost reservations.
- Trusted orchestration/planning separated from supervised Playwright in a fixture-only namespace, connected through bounded command/result pipes with no provider/DB/queue secrets in the runner.
- At-least-once queue delivery with transactional outbox, deterministic IDs, DB leases/epochs, command receipts and fail-closed uncertain-outcome recovery. No blind side-effect replay or exactly-once guarantee.
- Fixed starting limits and explicit deadlines/cancellation grace, artifact TTL/quota and seven-day metadata lifetime.
- Public independent expected behavior allowed in prompts; private defect/variant/reference answers withheld. Machine and human evaluation metrics are reported separately with fixed denominators.
- Monorepo and minimum HTTP resources selected; original Day 1 full run-creation criterion remains incomplete until a capable real execution path exists. No fake completion.
- Lowercase documentation hierarchy, canonical root AGENTS.md, immutable original archive and eleven accepted ADRs.

See the [documentation index](../README.md) for authoritative specifications and all ADRs. Accepted technical design does not imply a signed charter, external/legal approval, implemented controls or passed runtime gates.

## Exactly which paths changed

The repository had no tracked files at inspection, so these changes are compared against a pre-edit content/hash inventory rather than a misleading Git diff. There are **2 modified existing paths**, **16 relocated source paths**, and **56 added current paths** (including relocation destinations and preserved archive files). The sets below are exhaustive; relocation destinations and archive copies also appear in added paths. Empty obsolete export directories were removed only after their files were relocated. No source file was discarded.

### Existing paths modified in place

- [AGENTS.md](../../AGENTS.md)
- [docs/reviews/2026-11-08-foundation-review.md](../../docs/reviews/2026-11-08-foundation-review.md)

### Relocated sources and preserved original bytes

All fifteen original foundational/hub documents were copied byte-for-byte into the archive before revision at their canonical active paths. The duplicate Agents.md itself was moved unchanged to the archive. Original SHA-256 values and exact machine-readable path sets are in [change-manifest.json](../change-manifest.json).

| Original path (now retired) | Current path | Byte-preserved original |
| --- | --- | --- |
| `Docs/01 — Project Charter & Statement of Work 412d15a2a43c810ca3c7d8b7283780a9.md` | [docs/foundations/01-project-charter.md](../../docs/foundations/01-project-charter.md) | [docs/archive/v0.1/01 — Project Charter & Statement of Work 412d15a2a43c810ca3c7d8b7283780a9.md](../../docs/archive/v0.1/01%20%E2%80%94%20Project%20Charter%20%26%20Statement%20of%20Work%20412d15a2a43c810ca3c7d8b7283780a9.md) |
| `Docs/02 — Product Requirements Document (PRD) 412d15a2a43c81e3a6c2d9e576dea5c6.md` | [docs/foundations/02-product-requirements.md](../../docs/foundations/02-product-requirements.md) | [docs/archive/v0.1/02 — Product Requirements Document (PRD) 412d15a2a43c81e3a6c2d9e576dea5c6.md](../../docs/archive/v0.1/02%20%E2%80%94%20Product%20Requirements%20Document%20%28PRD%29%20412d15a2a43c81e3a6c2d9e576dea5c6.md) |
| `Docs/03 — Software Requirements Specification (SRS) 412d15a2a43c81c2a32cf9b74548faac.md` | [docs/foundations/03-software-requirements.md](../../docs/foundations/03-software-requirements.md) | [docs/archive/v0.1/03 — Software Requirements Specification (SRS) 412d15a2a43c81c2a32cf9b74548faac.md](../../docs/archive/v0.1/03%20%E2%80%94%20Software%20Requirements%20Specification%20%28SRS%29%20412d15a2a43c81c2a32cf9b74548faac.md) |
| `Docs/04 — Wireframes & User Journey Prototypes 412d15a2a43c815ba980c31d681aadb9.md` | [docs/foundations/04-user-journeys.md](../../docs/foundations/04-user-journeys.md) | [docs/archive/v0.1/04 — Wireframes & User Journey Prototypes 412d15a2a43c815ba980c31d681aadb9.md](../../docs/archive/v0.1/04%20%E2%80%94%20Wireframes%20%26%20User%20Journey%20Prototypes%20412d15a2a43c815ba980c31d681aadb9.md) |
| `Docs/05 — Data Strategy & Sourcing Plan 412d15a2a43c81a488b8e9af7afb0f61.md` | [docs/foundations/05-data-strategy.md](../../docs/foundations/05-data-strategy.md) | [docs/archive/v0.1/05 — Data Strategy & Sourcing Plan 412d15a2a43c81a488b8e9af7afb0f61.md](../../docs/archive/v0.1/05%20%E2%80%94%20Data%20Strategy%20%26%20Sourcing%20Plan%20412d15a2a43c81a488b8e9af7afb0f61.md) |
| `Docs/06 — Datasheet for Golden Fixture Dataset 412d15a2a43c813ca27ce91c58aaf45e.md` | [docs/foundations/06-golden-fixture-datasheet.md](../../docs/foundations/06-golden-fixture-datasheet.md) | [docs/archive/v0.1/06 — Datasheet for Golden Fixture Dataset 412d15a2a43c813ca27ce91c58aaf45e.md](../../docs/archive/v0.1/06%20%E2%80%94%20Datasheet%20for%20Golden%20Fixture%20Dataset%20412d15a2a43c813ca27ce91c58aaf45e.md) |
| `Docs/07 — AI Architecture & Model Design 412d15a2a43c818f9bb4fc53d28d4071.md` | [docs/foundations/07-ai-architecture.md](../../docs/foundations/07-ai-architecture.md) | [docs/archive/v0.1/07 — AI Architecture & Model Design 412d15a2a43c818f9bb4fc53d28d4071.md](../../docs/archive/v0.1/07%20%E2%80%94%20AI%20Architecture%20%26%20Model%20Design%20412d15a2a43c818f9bb4fc53d28d4071.md) |
| `Docs/08 — Prompt & Guardrail Specification 412d15a2a43c81a9825bf3bd3023e8b1.md` | [docs/foundations/08-prompt-guardrails.md](../../docs/foundations/08-prompt-guardrails.md) | [docs/archive/v0.1/08 — Prompt & Guardrail Specification 412d15a2a43c81a9825bf3bd3023e8b1.md](../../docs/archive/v0.1/08%20%E2%80%94%20Prompt%20%26%20Guardrail%20Specification%20412d15a2a43c81a9825bf3bd3023e8b1.md) |
| `Docs/09 — System Architecture Document (SAD) 412d15a2a43c81749073c0c802da3880.md` | [docs/foundations/09-system-architecture.md](../../docs/foundations/09-system-architecture.md) | [docs/archive/v0.1/09 — System Architecture Document (SAD) 412d15a2a43c81749073c0c802da3880.md](../../docs/archive/v0.1/09%20%E2%80%94%20System%20Architecture%20Document%20%28SAD%29%20412d15a2a43c81749073c0c802da3880.md) |
| `Docs/10 — Technical Design Document & API Contracts 412d15a2a43c818888e0d351cb0cfa94.md` | [docs/foundations/10-technical-design-api.md](../../docs/foundations/10-technical-design-api.md) | [docs/archive/v0.1/10 — Technical Design Document & API Contracts 412d15a2a43c818888e0d351cb0cfa94.md](../../docs/archive/v0.1/10%20%E2%80%94%20Technical%20Design%20Document%20%26%20API%20Contracts%20412d15a2a43c818888e0d351cb0cfa94.md) |
| `Docs/11 — Security & Threat Model Blueprint 412d15a2a43c81779760f9a96ff56dec.md` | [docs/foundations/11-security-threat-model.md](../../docs/foundations/11-security-threat-model.md) | [docs/archive/v0.1/11 — Security & Threat Model Blueprint 412d15a2a43c81779760f9a96ff56dec.md](../../docs/archive/v0.1/11%20%E2%80%94%20Security%20%26%20Threat%20Model%20Blueprint%20412d15a2a43c81779760f9a96ff56dec.md) |
| `Docs/12 — AI Evaluation & Golden Dataset Plan 412d15a2a43c8123b921ec8fc5dd06f3.md` | [docs/foundations/12-evaluation-plan.md](../../docs/foundations/12-evaluation-plan.md) | [docs/archive/v0.1/12 — AI Evaluation & Golden Dataset Plan 412d15a2a43c8123b921ec8fc5dd06f3.md](../../docs/archive/v0.1/12%20%E2%80%94%20AI%20Evaluation%20%26%20Golden%20Dataset%20Plan%20412d15a2a43c8123b921ec8fc5dd06f3.md) |
| `Docs/13 — AI Risk & Compliance Assessment 412d15a2a43c81798349d44d53415e74.md` | [docs/foundations/13-ai-risk-compliance.md](../../docs/foundations/13-ai-risk-compliance.md) | [docs/archive/v0.1/13 — AI Risk & Compliance Assessment 412d15a2a43c81798349d44d53415e74.md](../../docs/archive/v0.1/13%20%E2%80%94%20AI%20Risk%20%26%20Compliance%20Assessment%20412d15a2a43c81798349d44d53415e74.md) |
| `Docs/14 — Risk Management & Cost Estimation Plan 412d15a2a43c81d0a120c4947957594f.md` | [docs/foundations/14-risk-cost-plan.md](../../docs/foundations/14-risk-cost-plan.md) | [docs/archive/v0.1/14 — Risk Management & Cost Estimation Plan 412d15a2a43c81d0a120c4947957594f.md](../../docs/archive/v0.1/14%20%E2%80%94%20Risk%20Management%20%26%20Cost%20Estimation%20Plan%20412d15a2a43c81d0a120c4947957594f.md) |
| `Docs/TestPilot AI — Product & Engineering Hub 412d15a2a43c81c3871ffbc29f7c825b.md` | [docs/foundations/index.md](../../docs/foundations/index.md) | [docs/archive/v0.1/TestPilot AI — Product & Engineering Hub 412d15a2a43c81c3871ffbc29f7c825b.md](../../docs/archive/v0.1/TestPilot%20AI%20%E2%80%94%20Product%20%26%20Engineering%20Hub%20412d15a2a43c81c3871ffbc29f7c825b.md) |
| `Agents.md` | [docs/archive/v0.1/Agents.md](../../docs/archive/v0.1/Agents.md) | [docs/archive/v0.1/Agents.md](../../docs/archive/v0.1/Agents.md) |

### Every added current path

- [docs/README.md](../../docs/README.md)
- [docs/adr/001-deterministic-execution.md](../../docs/adr/001-deterministic-execution.md)
- [docs/adr/002-local-controlled-fixtures.md](../../docs/adr/002-local-controlled-fixtures.md)
- [docs/adr/003-bounded-hosted-planner.md](../../docs/adr/003-bounded-hosted-planner.md)
- [docs/adr/004-queue-worker.md](../../docs/adr/004-queue-worker.md)
- [docs/adr/005-browser-isolation.md](../../docs/adr/005-browser-isolation.md)
- [docs/adr/006-canonical-contracts.md](../../docs/adr/006-canonical-contracts.md)
- [docs/adr/007-durable-jobs.md](../../docs/adr/007-durable-jobs.md)
- [docs/adr/008-verification-review.md](../../docs/adr/008-verification-review.md)
- [docs/adr/009-authorization-policy.md](../../docs/adr/009-authorization-policy.md)
- [docs/adr/010-evidence-evaluation.md](../../docs/adr/010-evidence-evaluation.md)
- [docs/adr/011-documentation-baseline.md](../../docs/adr/011-documentation-baseline.md)
- [docs/architecture/baseline.md](../../docs/architecture/baseline.md)
- [docs/architecture/data-model.md](../../docs/architecture/data-model.md)
- [docs/architecture/findings-and-evaluation.md](../../docs/architecture/findings-and-evaluation.md)
- [docs/architecture/job-lifecycle.md](../../docs/architecture/job-lifecycle.md)
- [docs/architecture/runner-protocol.md](../../docs/architecture/runner-protocol.md)
- [docs/architecture/safety-policy.md](../../docs/architecture/safety-policy.md)
- [docs/archive/v0.1/01 — Project Charter & Statement of Work 412d15a2a43c810ca3c7d8b7283780a9.md](../../docs/archive/v0.1/01%20%E2%80%94%20Project%20Charter%20%26%20Statement%20of%20Work%20412d15a2a43c810ca3c7d8b7283780a9.md)
- [docs/archive/v0.1/02 — Product Requirements Document (PRD) 412d15a2a43c81e3a6c2d9e576dea5c6.md](../../docs/archive/v0.1/02%20%E2%80%94%20Product%20Requirements%20Document%20%28PRD%29%20412d15a2a43c81e3a6c2d9e576dea5c6.md)
- [docs/archive/v0.1/03 — Software Requirements Specification (SRS) 412d15a2a43c81c2a32cf9b74548faac.md](../../docs/archive/v0.1/03%20%E2%80%94%20Software%20Requirements%20Specification%20%28SRS%29%20412d15a2a43c81c2a32cf9b74548faac.md)
- [docs/archive/v0.1/04 — Wireframes & User Journey Prototypes 412d15a2a43c815ba980c31d681aadb9.md](../../docs/archive/v0.1/04%20%E2%80%94%20Wireframes%20%26%20User%20Journey%20Prototypes%20412d15a2a43c815ba980c31d681aadb9.md)
- [docs/archive/v0.1/05 — Data Strategy & Sourcing Plan 412d15a2a43c81a488b8e9af7afb0f61.md](../../docs/archive/v0.1/05%20%E2%80%94%20Data%20Strategy%20%26%20Sourcing%20Plan%20412d15a2a43c81a488b8e9af7afb0f61.md)
- [docs/archive/v0.1/06 — Datasheet for Golden Fixture Dataset 412d15a2a43c813ca27ce91c58aaf45e.md](../../docs/archive/v0.1/06%20%E2%80%94%20Datasheet%20for%20Golden%20Fixture%20Dataset%20412d15a2a43c813ca27ce91c58aaf45e.md)
- [docs/archive/v0.1/07 — AI Architecture & Model Design 412d15a2a43c818f9bb4fc53d28d4071.md](../../docs/archive/v0.1/07%20%E2%80%94%20AI%20Architecture%20%26%20Model%20Design%20412d15a2a43c818f9bb4fc53d28d4071.md)
- [docs/archive/v0.1/08 — Prompt & Guardrail Specification 412d15a2a43c81a9825bf3bd3023e8b1.md](../../docs/archive/v0.1/08%20%E2%80%94%20Prompt%20%26%20Guardrail%20Specification%20412d15a2a43c81a9825bf3bd3023e8b1.md)
- [docs/archive/v0.1/09 — System Architecture Document (SAD) 412d15a2a43c81749073c0c802da3880.md](../../docs/archive/v0.1/09%20%E2%80%94%20System%20Architecture%20Document%20%28SAD%29%20412d15a2a43c81749073c0c802da3880.md)
- [docs/archive/v0.1/10 — Technical Design Document & API Contracts 412d15a2a43c818888e0d351cb0cfa94.md](../../docs/archive/v0.1/10%20%E2%80%94%20Technical%20Design%20Document%20%26%20API%20Contracts%20412d15a2a43c818888e0d351cb0cfa94.md)
- [docs/archive/v0.1/11 — Security & Threat Model Blueprint 412d15a2a43c81779760f9a96ff56dec.md](../../docs/archive/v0.1/11%20%E2%80%94%20Security%20%26%20Threat%20Model%20Blueprint%20412d15a2a43c81779760f9a96ff56dec.md)
- [docs/archive/v0.1/12 — AI Evaluation & Golden Dataset Plan 412d15a2a43c8123b921ec8fc5dd06f3.md](../../docs/archive/v0.1/12%20%E2%80%94%20AI%20Evaluation%20%26%20Golden%20Dataset%20Plan%20412d15a2a43c8123b921ec8fc5dd06f3.md)
- [docs/archive/v0.1/13 — AI Risk & Compliance Assessment 412d15a2a43c81798349d44d53415e74.md](../../docs/archive/v0.1/13%20%E2%80%94%20AI%20Risk%20%26%20Compliance%20Assessment%20412d15a2a43c81798349d44d53415e74.md)
- [docs/archive/v0.1/14 — Risk Management & Cost Estimation Plan 412d15a2a43c81d0a120c4947957594f.md](../../docs/archive/v0.1/14%20%E2%80%94%20Risk%20Management%20%26%20Cost%20Estimation%20Plan%20412d15a2a43c81d0a120c4947957594f.md)
- [docs/archive/v0.1/Agents.md](../../docs/archive/v0.1/Agents.md)
- [docs/archive/v0.1/README.md](../../docs/archive/v0.1/README.md)
- [docs/archive/v0.1/TestPilot AI — Product & Engineering Hub 412d15a2a43c81c3871ffbc29f7c825b.md](../../docs/archive/v0.1/TestPilot%20AI%20%E2%80%94%20Product%20%26%20Engineering%20Hub%20412d15a2a43c81c3871ffbc29f7c825b.md)
- [docs/change-manifest.json](../../docs/change-manifest.json)
- [docs/contracts/http-api-v1.md](../../docs/contracts/http-api-v1.md)
- [docs/contracts/test-plan-v1.md](../../docs/contracts/test-plan-v1.md)
- [docs/contracts/test-plan-v1.schema.json](../../docs/contracts/test-plan-v1.schema.json)
- [docs/foundations/01-project-charter.md](../../docs/foundations/01-project-charter.md)
- [docs/foundations/02-product-requirements.md](../../docs/foundations/02-product-requirements.md)
- [docs/foundations/03-software-requirements.md](../../docs/foundations/03-software-requirements.md)
- [docs/foundations/04-user-journeys.md](../../docs/foundations/04-user-journeys.md)
- [docs/foundations/05-data-strategy.md](../../docs/foundations/05-data-strategy.md)
- [docs/foundations/06-golden-fixture-datasheet.md](../../docs/foundations/06-golden-fixture-datasheet.md)
- [docs/foundations/07-ai-architecture.md](../../docs/foundations/07-ai-architecture.md)
- [docs/foundations/08-prompt-guardrails.md](../../docs/foundations/08-prompt-guardrails.md)
- [docs/foundations/09-system-architecture.md](../../docs/foundations/09-system-architecture.md)
- [docs/foundations/10-technical-design-api.md](../../docs/foundations/10-technical-design-api.md)
- [docs/foundations/11-security-threat-model.md](../../docs/foundations/11-security-threat-model.md)
- [docs/foundations/12-evaluation-plan.md](../../docs/foundations/12-evaluation-plan.md)
- [docs/foundations/13-ai-risk-compliance.md](../../docs/foundations/13-ai-risk-compliance.md)
- [docs/foundations/14-risk-cost-plan.md](../../docs/foundations/14-risk-cost-plan.md)
- [docs/foundations/index.md](../../docs/foundations/index.md)
- [docs/implementation-readiness.md](../../docs/implementation-readiness.md)
- [docs/reviews/2026-11-08-architecture-resolution.md](../../docs/reviews/2026-11-08-architecture-resolution.md)

## Checks actually executed

- Re-inventoried all fourteen numbered foundations plus hub; validated every relocated original against its pre-edit SHA-256, including archived Agents.md. All sixteen original source hashes match.
- Executed the documented model using already installed Pydantic 2.13.4; four positive checks accepted (requirement, exploratory, empty synthetic fill, matching D08 example).
- Rejected 25 invalid model cases: unsupported versions/actions/target kinds/roles, extras at each object level, timeout coercion/bounds, duplicate IDs, missing assertion/ref, wrong intent/ref combination, count limits, blank objective, invalid ref syntax, absolute navigation URL and non-role fill target.
- Generated companion JSON Schema and checked it against JSON Schema draft 2020-12; validated positive JSON examples and checked extra-properties prohibition on every model object. Confirmed D08 example equals the canonical contract example.
- Checked active documentation local links, Markdown code-fence balance and trailing whitespace; archived original text is deliberately exempt from link repair to preserve bytes. Final check passed: 39 active/index Markdown files, 282 existing local links, balanced code fences and no trailing whitespace; all 16 archived source hashes matched.

These checks do not exercise the production JSON parser's duplicate-key/depth handling, contextual oracle/authorization checks, API, database, job worker, sandbox, browser, privacy or benchmark. Those application/runtime tests were **not run** and no such gate is claimed passed.

## Issues still unresolved

No known A01–A15 design contradiction is intentionally left unresolved. Operational choices and implementation proof remain open in [readiness](../implementation-readiness.md): compatible pinned runtime/tool versions; Docker and host sandbox feasibility; actual operator/repository/fixture ownership; exact fixture service/port/path/operation/reset manifests; provider/model/terms/prices and monetary caps; independent oracle review; implementation and fault-injection tests; artifact privacy/deletion proof; API/operator access tests; and the frozen thirty-trial plus adversarial benchmark. External/customer deployment is outside MVP and requires separate assessment.

Application development has not begun. No packages were installed, provider calls made, browsers launched, or system configuration changed.
