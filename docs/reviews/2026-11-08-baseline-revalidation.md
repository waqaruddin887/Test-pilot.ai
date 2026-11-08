# Baseline revalidation and clarification report

Date: 2026-11-08. Follow-up to the repeated architecture-resolution request. Reread the historical foundation review and all fourteen current foundational documents, then checked their selected contracts and subsystem specifications. The original technical baseline and eleven accepted ADRs remain in place; no application code, dependencies, services or system configuration were introduced.

## Finalized clarifications

1. **Persistent control entities:** define ExecutionSlot (singleton global execution lease and teardown state), WorkerCapability (trusted compatible-worker liveness), and JobCommand (pre-send command identity/hash/epoch and receipt state). Previously these concepts were referenced but their rows were missing from the logical model. Constrain cross-job/attempt ownership and preserve live cleanup obligations. Specify ManifestArtifact as a composite-key join table rather than applying the primary-entity UUID rule to it.
2. **Recovery budget:** a recovered claim retains the original started_at, active deadline, queue deadline, reservation and planner-call cap. Queue expiry applies to work never started; recovered active work uses its original active deadline. Recovery cannot grant a fresh five minutes.
3. **Uncertain delivery:** persist command/provider intent before transmission. An intent with no acknowledgment is potentially sent and cannot justify replay; reconcile trusted receipts or fail interrupted.
4. **Sealed authority:** OracleVersion content is immutable; review fields are sealed once before use. A published evidence manifest seals content/hash and its finding binding together.
5. **Privacy consistency:** prohibit target credentials/session capture while permitting operator-session token hashes in the separate control plane. Synthetic approved email-like values are distinct from real personal data. Raw screenshots/traces never go to the MVP planner.
6. **Reporter and foundation alignment:** objective text cannot grant policy authority; future reporters preserve supplied assessments/reviews. Foundation backup guidance now matches explicit private backup or declared disposable development data. Static fixture mapping replaces the lingering dynamic-DNS MVP wording; API examples use valid UUIDs and include the required idempotency expiry.

The canonical plan schema remains **1.0.0**, with no wire-format change. The fixture-only safety boundary, machine-versus-human states, PostgreSQL authority, isolated browser runner and conservative crash recovery are unchanged. ADR-007 and ADR-010 document the refinements. No additional domain, mutation or network permission was granted.

## Exactly which files changed in this pass

Modified existing files:

- [docs/README.md](../../docs/README.md)
- [docs/adr/007-durable-jobs.md](../../docs/adr/007-durable-jobs.md)
- [docs/adr/010-evidence-evaluation.md](../../docs/adr/010-evidence-evaluation.md)
- [docs/architecture/data-model.md](../../docs/architecture/data-model.md)
- [docs/architecture/job-lifecycle.md](../../docs/architecture/job-lifecycle.md)
- [docs/change-manifest.json](../../docs/change-manifest.json)
- [docs/foundations/05-data-strategy.md](../../docs/foundations/05-data-strategy.md)
- [docs/foundations/08-prompt-guardrails.md](../../docs/foundations/08-prompt-guardrails.md)
- [docs/foundations/09-system-architecture.md](../../docs/foundations/09-system-architecture.md)
- [docs/foundations/10-technical-design-api.md](../../docs/foundations/10-technical-design-api.md)
- [docs/foundations/11-security-threat-model.md](../../docs/foundations/11-security-threat-model.md)
- [docs/implementation-readiness.md](../../docs/implementation-readiness.md)
- [docs/reviews/2026-11-08-architecture-resolution.md](../../docs/reviews/2026-11-08-architecture-resolution.md)

Added files:

- [docs/reviews/2026-11-08-baseline-revalidation.md](../../docs/reviews/2026-11-08-baseline-revalidation.md)

No files were removed or relocated in this pass; archival originals remain untouched. The [manifest](../change-manifest.json) retains the initial resolution's exact path sets and original checksums, and adds a separate followup_clarifications change set with prior content hashes. The [initial resolution report](2026-11-08-architecture-resolution.md) lists the preceding normalization, fourteen revised foundations, hub and eleven ADRs.

## Verification actually performed

- Documentation-only Pydantic validation with the already installed dependency: four positive checks accepted; 25 invalid cases rejected. The D08 example still matches the canonical example.
- Generated JSON Schema remains structurally valid and unchanged; no wire-version bump is needed.
- Rechecked active/index local links, code fences, whitespace and original archive hashes. Final validation passed: 40 active/index Markdown documents, 302 local links, balanced code fences, no trailing whitespace and all 16 archived-source hashes matched.
- Content-inventory comparison records the exact changes above; only Markdown and the documentation change manifest changed in this pass.

No API, database, queue, browser, sandbox, privacy or evaluation tests were run. Model checks do not prove the production parser or contextual authorization/oracle checks, which are not implemented.

## Remaining blockers

[Readiness R01–R12](../implementation-readiness.md) remains authoritative: pin a compatible runtime/toolchain; establish Docker/host sandbox capability; configure the actual operator and fixture ownership/permissions; specify exact fixture deployment/operation/reset manifests; choose provider/model and verified terms/pricing/monetary caps; independently author/review/reference-test fixture oracles; implement and test persistence/job fencing, isolation, cleanup, evidence lifecycle and local API access; and run the frozen thirty-trial plus adversarial benchmark. External/customer testing remains out of MVP scope.

No known design contradiction found in this pass is intentionally left open. Concrete implementation and host-sandbox feasibility remain unverified; design acceptance is not proof of readiness for browser execution. Application development has not begun.
