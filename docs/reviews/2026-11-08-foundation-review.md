# TestPilot AI: foundational review and Day 1 plan

> Historical review: the [v0.2 technical baseline](../README.md) and [resolution report](2026-11-08-architecture-resolution.md) supersede the proposals and path references below. All 14 sources now live in `docs/foundations/`; originals are preserved in `docs/archive/v0.1/`. This review retains the original inspection findings and pending implementation checklist.

Date: 2026-11-08. Status: documentation review complete; proposed architecture, not an approved specification or implemented system.

No application code was written. No application, browser, security, or evaluation tests were run. Checked boxes below record document inspection only; implementation tasks remain unchecked.

## 1. Material actually inspected

- [x] Root `AGENTS.md` and the additional `Agents.md`.
- [x] All fourteen numbered foundational Markdown documents in `Docs/`.
- [x] The Product & Engineering Hub in `Docs/`.
- [x] Repository file inventory, Git status, and selected development-tool availability.

The requested lowercase `docs/` was empty at inspection. The foundational files exist in uppercase `Docs/`; none of the fourteen numbered documents is missing there. This review creates `docs/reviews/`, but does not move or modify the foundational files. Their export-ID filenames are preserved. References such as D03 below identify the numbered files in `Docs/`.

| Ref | Document read | Principal requirements |
| --- | --- | --- |
| D01 | Project Charter & Statement of Work | Local-first portfolio prototype, seven days, controlled targets, 3–5 cases, gates and unknown budget |
| D02 | Product Requirements Document | Authorization, bounded planning, evidence, review, controlled evaluation; P0/P1 priorities |
| D03 | Software Requirements Specification | FR01–FR12, finite actions, cancellation, privacy, deadlines, classification and traceability |
| D04 | Wireframes & User Journey Prototypes | Project/run/review screens, progress states, accessible errors and human review |
| D05 | Data Strategy & Sourcing Plan | Synthetic sources, authorization records, redaction, proposed metadata/artifact TTLs |
| D06 | Datasheet for Golden Fixture Dataset | Five good/broken pairs, independently authored oracles, hidden labels and repeatability |
| D07 | AI Architecture & Model Design | One hosted planner, Pydantic validation, deterministic executor, separate verifier, optional reporter |
| D08 | Prompt & Guardrail Specification | Trust envelope, JSON example, bounded repair, safe actions and approval rules |
| D09 | System Architecture Document | Next.js/FastAPI/Postgres/Redis-RQ/Playwright, network zones, recovery and observability |
| D10 | Technical Design Document & API Contracts | Six primary entities, run state machine, API routes, local access, integrity and idempotency |
| D11 | Security & Threat Model Blueprint | SSRF, injection, egress, resource limits, artifact controls and release tests |
| D12 | AI Evaluation & Golden Dataset Plan | Thirty proposed trials, quality metrics, frozen versions, adversarial gates and limitations |
| D13 | AI Risk & Compliance Assessment | Synthetic-only MVP, provider due diligence, separate external-launch assessment |
| D14 | Risk Management & Cost Estimation Plan | Token/cost/storage budgets, hard caps, failure contingencies and unknown commitments |

All source documents are drafts. Numeric targets are acceptance proposals, not measured results. No document supplies a production-ready schema, deployed security boundary, provider selection, actual budget, or completed benchmark.

## 2. Audit: contradictions and unresolved contracts

“Blocker” means resolve before implementing the affected subsystem, not that all repository scaffolding must stop. Proposed resolutions below require incorporation into the relevant specification/ADR; they are not silently adopted requirements.

| ID | Priority / source | Finding | Proposed resolution |
| --- | --- | --- | --- |
| A01 | Foundation / AGENTS, hub | Instructions refer to `docs/`; sources live in `Docs/`. Two differently cased agent files can drift. Hub links point into a nonexistent nested export directory. | Standardize on `docs/`, preserve document contents/history, repair hub links, and consolidate instructions into `AGENTS.md` in a separate reviewed documentation change. |
| A02 | Blocker: planner / D07, D08 | D07 uses top-level objective, case IDs, actions with `type`, separate assertions; D08 uses `steps` with `action`, case-level oracle_ref and omits required-looking fields. D08 also lacks an explicit exploratory flag despite describing one. | Freeze one discriminated, versioned Pydantic contract and generate its JSON Schema. Prefer ordered `steps` with `action`; assertion steps carry oracle refs, and cases explicitly identify exploratory intent. Rewrite both examples to match. |
| A03 | Blocker: safety / D08, D11, D01 | D08 permits human-approved non-fixture submissions; D11 prohibits external-site forms and calls for approving mutations. The fixture exemption and definition of mutation are unclear. | For MVP, refuse all non-fixture submissions even with an approval click. Preauthorize only explicitly named synthetic fixture mutations. A generic click cannot establish safety; define permitted controls and state changes per fixture. |
| A04 | Blocker: classification / D02–04, D07, D10–12, hub | Some passages imply verification/reproduction establishes confirmation; D04 requires a human to inspect evidence before confirming. Missing-oracle observations are described as both suspected and inconclusive. | Track machine assessment separately from human review. Only an independent oracle violation with complete evidence and successful clean reproduction becomes a confirmation candidate; human acceptance establishes `confirmed`. Missing oracle remains inconclusive. |
| A05 | Blocker: evaluation / D06–08, D12 | D06 forbids expected output in prompts, but D08 supplies expected requirements/oracles to enable assertions. This is ambiguous between legitimate requirements and hidden benchmark answers. | Allow independently authored public requirements and expected application behavior. Keep defect labels, variant labels, reference-script results, defect IDs and expected-detection answers exclusively in the evaluation harness. Clarify D06 wording. |
| A06 | Blocker: isolation / D09–11 | The worker needs queue/database/artifact and LLM access while the browser must not reach those services. Containerization alone does not define a boundary between these privileges. | Separate trusted orchestration/planning from an isolated browser runner. Use a narrow, bounded command protocol; browser runner gets no provider, DB, or Redis credentials. Define directed network rules before Day 2. |
| A07 | Blocker: privacy / D03, D05, D10–11 | Traces, screenshots and raw observations can retain data that the specifications prohibit persisting. DOM-to-LLM redaction does not sanitize a trace. | Use reviewed synthetic fixtures only; configure capture minimization and a tested retention policy. Block evidence capture or quarantine/delete artifacts when safe handling cannot be guaranteed. Do not claim arbitrary trace sanitization is solved. |
| A08 | Before API / D03, D04, D10 | “Separate resources” and UI actions exceed the listed API: no project list/detail, run history list, approvals management, review/dismiss, oracle lookup, or settings contracts. | Publish the minimum Day 1 project list/create and run create/detail API; specify later run/case/finding/artifact/review APIs before those screens. Add pagination and stable errors. |
| A09 | Before persistence / D05, D09–10 | Schema omits authorization scope/expiry, oracle versions, linked reruns, run policy/budget snapshots, review history, queue lease/events and idempotency storage. | Expand the logical model as described below, then translate it into migrations and constraints. JSON plans do not replace relational ownership and lifecycle constraints. |
| A10 | Before worker / D03, D09–10, D14 | Queue/DB durability is asserted but enqueue transaction boundaries, retryable errors, crash recovery, cancellation races and retry budgets are undefined. | Postgres is authoritative; transactional outbox, idempotent dispatch, run leases and reconciliation handle delivery gaps. Never automatically repeat potentially mutating steps after an unknown outcome. |
| A11 | Before execution / D01, D03, D14 | 3–5 cases versus maximum five; twelve “actions” versus twelve “steps”; five-minute budget versus 60 possible steps, reproduction and planner retry. | Recommend 1–5 cases; count assertions as steps, max 12 per case. Use one absolute execution deadline including planning, repair and reproduction; bound discovery/cleanup separately and define queue-wait expiry. Stop with partial results when exhausted. Confirm these semantics in D03. |
| A12 | Before local API / D10–11 | Binding localhost is the proposed local access model, yet ownership checks lack a user/principal definition. A browser-origin attack against local services remains possible. | Define one local operator, exact trusted UI origin, API session/bootstrap credential and server-side run/artifact checks; enforce Origin/Host and mutation CSRF protections as appropriate. Do not expose services publicly. |
| A13 | Before benchmark / D06, D12 | Run-level versus unique-variant false positives, aggregate deduplication over repeats, schema validity before/after repair, and “attempted” step denominator are underspecified. | Freeze a scoring protocol with raw counters, initial/repaired validity, per-trial and aggregate metrics, policy rejections separate from executor errors, and N/A for zero denominator. |
| A14 | Before fixture work / D01, D06 | Invalid-login and cart fixtures appear alongside exclusions on production authentication/payments. This is compatible only if simulated scope is explicit. | Use synthetic login rejection without real credentials/sessions and a read-only cart arithmetic demo without checkout/payment. Document reset behavior and permitted submissions. |
| A15 | Scheduling / D01–02, hub | Day 1 creates a run, but discovery/planning/execution arrive later; history is both core run-history scope and P1 comparison/replay. | Day 1 may persist/queue runs but must explicitly show execution unavailable when no capable worker exists. Retain basic run records; defer comparison/export/replay. Do not simulate completed testing. |

### Missing requirements to close

Before implementation of the foundation:

- Identify the local operator, repository/IP ownership and fixture ownership; project eligibility is a separate administrative issue, not an invented engineering requirement.
- Define canonical schemas, state names and minimal API acceptance examples; specify config validation and which fields operators versus models may supply.
- Choose supported runtime versions after a compatibility check, not from installed version alone; define lockfile/image update policy and supported host platform.
- Define the Day 1 worker-unavailable behavior, local access boundary and trusted fixture origin configuration. Project creation must not let arbitrary submitted origins self-authorize.

Before browser/LLM use:

- Define URL canonicalization: exact scheme/host/port, path segments, query restrictions, credentials, encoded traversal, fragments, IDNA, IPv4/IPv6 and redirects. Never use a string-prefix origin check.
- Enumerate navigation, fetch, subresource, iframe, popup, WebSocket, service-worker, download, DNS and non-HTTP handling. Specify whether each is denied or supported; close bypass routes outside Playwright as well.
- Specify deterministic role/name/text matching, locator uniqueness, allowed fill values and lengths, supported URL/visible assertions, assertion polling, dialogs and unsupported-page errors. No model CSS/XPath/JavaScript execution escape hatch.
- Bound discovery depth, pages, DOM nodes, text bytes, response sizes, screenshot count, artifact bytes, CPU/RAM/processes and disk usage. Define total retry and cancellation grace periods.
- Select provider/model, verified pricing/rate limits, actual daily/per-run spend and token caps, timeouts and retention terms before live calls. Treat cost estimates as estimates until provider usage is known.
- Approve TTLs (D05 proposes seven days metadata, 24 hours artifacts), deletion/backups/log policy, storage quota and cleanup failure behavior. Specify evidence handling after TTL expiry.

Before findings/evaluation:

- Define oracle authoring, versioning, authority and permitted assertion types. Navigation or infrastructure errors alone do not establish product defects.
- Define confirmation, dismissal, review actor/time, severity rubric, reproduction attempts and immutable evidence linkage. Distinguish a replay of the same action sequence from an independently written reference oracle check.
- Define good/broken fixture reset and isolation. Hide variant identity in URLs/titles/context where feasible; do not give planner harness paths or golden scripts. Document any remaining benchmark leakage.
- Fix benchmark development/held-out separation, shuffled trial seeds, environment manifest, deduplication and missed-detection accounting. Five pairs justify a controlled demo, not general accuracy claims.
- Define migration backup/rollback, retention referential behavior, health/readiness, stale-job handling and incident ownership. Reverify legal/provider requirements before any external launch; this review makes no legal-compliance determination.

## 3. Proposed complete monorepo architecture

Retain the prescribed stack. Start with a modular Python backend and one web app; use deployment separation for the browser trust boundary rather than creating many business microservices.

```text
testpilot/
  AGENTS.md
  README.md
  .env.example                   # names/placeholders only
  .gitignore
  package.json                   # pnpm workspace orchestration
  pnpm-workspace.yaml
  pnpm-lock.yaml
  pyproject.toml                 # one Python project, src layout
  uv.lock                        # proposed Python manager; choose compatibility first
  apps/
    web/                         # Next.js, TS, Tailwind; operator UI only
      app/                       # projects, runs, findings, evidence views
      components/
      lib/                       # API client, accessible status presentation
  packages/
    api-client/                  # generated TS client/types from backend OpenAPI
    contracts/                   # exported OpenAPI/plan schemas; no hand-copied types
  backend/
    src/testpilot/
      api/                       # FastAPI routes, dependencies, stable errors
      domain/                    # state machines, entities, classification, budgets
      contracts/                 # strict Pydantic DTOs and versioned plan schema
      application/               # project/run/review use cases; orchestration ports
      policy/                    # authorization, URLs, action rules, redaction
      persistence/               # ORM mappings, repositories, transactions/outbox
      jobs/                      # RQ dispatch, worker entry, leases/reconciliation
      planner/                   # provider adapter, prompt versions, metering
      runner/                    # bounded runner protocol/client; no model tools
      browser/                   # isolated Playwright server, discovery/executor
      verification/              # deterministic oracle evaluation and reproduction
      artifacts/                 # storage, manifests, hashes, expiry and safe serving
      reporting/                 # evidence-derived reports; optional LLM deferred
      observability/             # safe logs, correlation, metrics
    migrations/                  # Alembic revisions
    tests/                       # unit, API/DB/queue integrations, policy tests
  fixtures/
    site/                        # controlled local fixture app, good/broken variants
    requirements/                # public versioned product requirements/oracles
    reference-tests/             # authored Playwright checks; never planner input
  evaluation/
    manifests/                   # pinned fixture/model/prompt/browser protocol
    private-labels/              # harness-only labels; excluded from agent context
    scoring/                     # reproducible counters and classification analysis
    tests/
  tests/
    e2e/                         # dashboard-to-API and full fixture workflow
    security/                    # isolated negative tests, fake secrets, egress sinks
  infra/
    compose.yaml
    docker/                      # API/worker/web/runner/fixture Dockerfiles
    network/                     # explicit rules, denied destinations, security profile
  scripts/                       # setup, schema generation, migration/check commands
  docs/
    foundations/                 # proposed destination for the existing 14 + hub
    reviews/
    adr/
    runbooks/
  .github/workflows/             # CI only; no automatic issue/PR publishing agent
```

These are planned paths, not files already created. Use one shared Python distribution initially, with service-specific install/dependency groups and images. The runner image must not contain provider secrets, benchmark labels or reference-test outputs. A package boundary alone is not isolation. Avoid a generic plugin system or model-executable test scripts.

### Runtime topology and directed privileges

| Component | Responsibility | Access |
| --- | --- | --- |
| Web | Project configuration, run progress and evidence review | API only; no DB/provider credentials |
| API | Validate requests, authorize projects, persist state, retrieve evidence | Postgres, private artifacts, queue/outbox dispatcher as needed |
| RQ orchestrator | Claim one run, call planner and runner, verify, persist lifecycle | Postgres/Redis/artifacts; restricted provider egress; runner command endpoint |
| Planner adapter | Sanitize context, issue bounded model request, meter output | Logical module in trusted worker initially; provider key unavailable to runner |
| Browser runner | Discover and execute only policy-validated finite steps | Isolated fixture destination, temporary per-run files; no DB/Redis/provider/host access |
| Fixture | Serve synthetic UI and known state | Internal fixture network; no infrastructure credentials or outbound Internet |
| Postgres / Redis | Durable domain state / job transport | Private service networks; no published ports by default |
| Maintenance task | Reconcile jobs and delete expired artifacts | Trusted data/artifact access, no browser privilege |

Expose web and, if needed for development, API on loopback only. Prefer same-origin `/api` routing to FastAPI; Next.js must not duplicate backend policy/business logic. Container listeners can bind internally as required while host port publication binds loopback.

The runner protocol is initiated by the trusted worker and accepts a capability scoped to one run, policy version, allowed destination and deadline. Use fixed commands such as discover, execute validated steps, and cancel; bound request/response bytes and authenticate the caller. Do not expose a raw remote browser/debug port or arbitrary URL-fetch/evaluate RPC.

Network placement must permit worker-to-runner commands while preventing browser-initiated traffic to worker/API/DB/Redis. A shared Docker network does not provide this directed property by itself. Specify and test host-enforced firewall/namespace rules or an equivalent restricted transport; control-channel destinations are not target destinations. Do not mount the Docker socket in an application container. Allow only the isolated fixture service/address and required port; internal/private IP denial has this narrow explicit exception. Before introducing nonlocal targets, build and test connection-time DNS/IP enforcement and controlled egress; do not rely on request hooks alone.

Docker documents that default container networking permits outbound connections; therefore default Compose bridges cannot establish the required allowlist ([Docker networking](https://docs.docker.com/engine/network/)). Playwright documents root/sandbox caveats and cautions against treating its development image as protection for untrusted sites ([Playwright Docker](https://playwright.dev/python/docs/docker)). Use a non-root sandboxed browser, drop capabilities, set no-new-privileges, apply seccomp and resource limits, use a read-only root plus bounded tmpfs, and verify the effective runtime settings. Do not copy privileged or host-network settings from examples.

Playwright request interception is defense in depth. Its network documentation describes service-worker visibility gaps; block service workers for the restricted MVP ([Playwright network](https://playwright.dev/python/docs/network)). Test redirects, frames, popups, external assets and alternate channels independently. Fixed developer-authored inspection logic is permissible; model/page text must never become executable code.

### End-to-end processing and lifecycle

1. Local operator chooses a preauthorized fixture project. API checks active authorization and allowed path, caps objective/count, and snapshots effective policy.
2. API atomically stores Run, idempotency record and outbox event. A repeated key with the same payload returns the existing run; changed payload conflicts.
3. Dispatcher enqueues a fixed worker function with run ID only. Worker claims a database lease; duplicate delivery cannot execute the same lease twice. Queue arguments cannot select arbitrary functions or code.
4. Discovery runs inside the isolated runner. Trusted orchestration minimizes and redacts the bounded outline before any planner call.
5. Planner emits strict schema-v1 data. Reject extras, unknown actions, invalid oracle IDs, unsafe/ambiguous targets and over-budget plans. One bounded schema-repair request is permitted. Save sanitized plan and version/hash provenance.
6. Execute under an immutable policy; recheck authorization, deadline and per-step destination/safety. Each case starts in clean state; reproduction resets fixture state as well as browser context. Artifacts carry per-step IDs, hashes and expiry.
7. Independent verifier compares observations to versioned requirements. Missing evidence or oracle prevents confirmation. Successful reproduction creates a confirmation candidate for human review.
8. Persist terminal run outcome and all partial error/results; UI polls persisted state. A completed run means processing ended, not that the target passed or is bug-free.

Keep D10's queued → discovering → planning → executing → verifying → completed sequence. failed/cancelled are terminal. Cancellation is requested durably, checked between steps, and escalated to runner process termination after a specified grace period. Cleanup runs on every exit. Terminal writes use a state/version check to prevent cancel/complete races. No capable worker means a clear unavailable error for new runs; an already accepted run must be reconciled to an explicit failure after a bounded wait. A rerun creates a new linked run with new authorization checks; preserve original evidence.

Use RQ as delivery machinery rather than the source of run truth. Its worker is sequential by default, consistent with concurrency one ([RQ workers](https://python-rq.org/docs/workers/)); run leases still protect against duplicate dispatch and additional accidental workers. Use JSON serialization for fixed job payloads, private Redis access, bounded TTL/retries and documented Redis persistence. After a crash, mark an uncertain mutating attempt as interrupted/test error; do not silently resume by repeating it.

### Database specification to finalize

Keep D10's six entities, adding these fields/relations before migration design:

| Entity | Required specification additions |
| --- | --- |
| Project + Authorization | Operator, normalized origin, allowed path rules, fixture identity, allowed operations, permission source, issued/expiry/revocation times and policy version |
| Run | Authorization/policy snapshot, max cases/steps, deadline/budget snapshot, queued/started/ended timestamps, terminal reason, cancel request, parent rerun ID, environment/model/prompt/schema versions |
| Case / Step | Stable sequence/IDs, validated plan, clean-context attempt ID, typed outcome, oracle binding, observed assertion result, error category; unique sequence per case |
| Oracle | Versioned trusted requirement reference, expected behavior and supported deterministic assertion spec; no model-authored authority |
| Finding / Review | Machine assessment separate from human status, observed/expected values, oracle version, evidence links, severity basis, review actor/time/reason and reproduction attempts |
| ExecutionAttempt | Initial/reproduction kind, fresh-state seed, timestamps, outcome and artifact manifest; avoid overwriting first observations |
| Artifact | Opaque server-owned storage key, run/step/attempt ownership, kind, MIME, bytes, hash, expiry/deletion state and sensitivity; no user-controlled filesystem paths |
| RunEvent / lease | Ordered stage events, safe errors, heartbeat/lease owner/expiry, stage version for concurrency checks |
| Outbox / idempotency | Transactional pending dispatch and unique operator/key/request hash with documented expiry |
| Usage | Actual request/attempt token counts, cost estimate and price-version provenance; atomic daily budget reservations and reconciliation |

Use UUID primary keys, timezone-aware timestamps, FK constraints, valid-state/check constraints, unique step ordering, indexes on FKs/state/times/expiry and bounded JSON payloads. Use JSONB for versioned structured plans/observations, not for authorization or relational ownership shortcuts. Ensure an artifact's step/attempt belongs to the same run, and a finding's case belongs to its run. Define delete/restrict behavior before retention jobs are written.

Postgres is authoritative. Redis is disposable transport only to the extent recovery can reconstruct work safely. Store artifact bytes outside the database; publish a completed artifact manifest only after a successful atomic write/hash. Hashes detect changes but do not establish authenticity against a privileged attacker. Expired artifacts must make findings display “evidence expired”; retain historical review provenance without pretending evidence remains inspectable. Missing required evidence prevents any new confirmation. Reruns and reviews append records rather than editing prior raw observations.

Suggested persistence tools are SQLAlchemy and Alembic, with one Postgres driver chosen after compatibility checks; Alembic provides SQLAlchemy migrations ([SQLAlchemy](https://docs.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/en/latest/)). Keep transaction boundaries explicit and avoid synchronous DB/network calls inside async handlers without an appropriate execution strategy.

### API and contract boundaries

Pydantic models own HTTP request/response and plan schemas; generated OpenAPI owns frontend transport types. Domain entities and ORM models remain separate. Version HTTP contracts independently from prompt and plan schema versions. Enforce strict bounds and reject extra properties for model output. UI validation supplements server policy.

Day 1 minimum: project create/list, run create/detail, health/readiness, stable error envelope and persisted authorization policy. Subsequent P0 contracts: case/step listing, findings, review/dismiss, oracle provenance, evidence retrieval, cancel and linked rerun. Scope project/origin management to the local trusted operator. Settings changes must not retroactively expand an existing run's policy; revocation must stop ongoing work.

Poll initially; defer SSE/WebSockets, scheduling, export/comparison, reporter model, cloud object storage, public authentication, CI integration, RAG, embeddings, fine-tuning, Kubernetes and multi-browser execution.

## 4. Development dependencies and environment

Observed on PATH, without installation or service startup:

| Tool | Observation |
| --- | --- |
| Git | 2.56.0 |
| Python | 3.14.8 |
| Node | v22.23.1 |
| pnpm | Executable found; version/compatibility not checked |
| corepack, uv | Not on PATH |
| Docker / Compose | Docker executable not on PATH; Compose not checked independently |
| psql, redis-server | Not on PATH; no database/Redis service availability inferred |

These are environment observations, not supported-version decisions. No Python/JS dependency manifests or application source existed at inspection. No packages were installed. Select versions together, verify official support and binary-wheel availability, and pin lockfiles/images before setup. Do not assume installed Python is compatible with the chosen Playwright, driver and worker stack. Docker installation/runtime access is an infrastructure prerequisite, not something this review has performed.

| Layer | Required by sources | Proposed additions / validation |
| --- | --- | --- |
| Web | Next.js, TypeScript, Tailwind | React peer dependencies, pnpm workspace; lint/typecheck, UI test tooling and generated OpenAPI client |
| API/domain | Python, FastAPI, Pydantic | ASGI server, settings loader, bounded HTTP client; pytest, API test client, Ruff and type checker |
| Data | PostgreSQL | SQLAlchemy, Alembic, one compatible driver; actual Postgres integration tests rather than SQLite substitutes |
| Jobs | Redis, RQ | Redis client, JSON serializer, outbox/reconciliation task; real Redis worker integration tests |
| Browser | Python Playwright, Chromium | Matching Python package/browser image, browser OS dependencies, sandbox/seccomp, pytest integration |
| Local infra | Docker Compose | Health checks, private volumes/networks, resource controls and one-shot migration service |
| Quality | Critical automated checks | Dependency/image/secret scanning, Python/TS checks, contract drift and fixture-reference checks |
| LLM | One configurable hosted provider | Choose SDK or bounded HTTP adapter only after provider/model/caps are decided; deterministic fake adapter for offline tests |

Use one Python dependency lock and one JavaScript workspace lock. Keep browser-only and development tools out of the API runtime image where practical. Store no API keys in `.env.example`, images, Git, prompts or artifacts. No paid provider dependency is required for Day 1. Candidate additions above are recommendations, not requirements found in the foundational documents.

## 5. Detailed Day 1 checklist

This is the implementation plan for a later coding pass. None of these unchecked items has been completed by this review.

### A. Freeze foundation decisions

- [ ] Normalize source paths and fix hub links without losing source content; retain a single authoritative AGENTS.md.
- [ ] Record the audit issues with source, owner, decision, due milestone and unresolved status.
- [ ] Reconcile D07/D08 schema, A03 action policy, A04 confirmation rules and A05 benchmark leakage wording.
- [ ] Write ADR-001–004 from D09 and proposed additional ADRs below; label accepted versus proposed explicitly.
- [ ] Define exact fixture hostname/port/path policy and operator boundary. Never authorize arbitrary URLs solely because project creation supplied them.
- [ ] Approve the Day 1 acceptance path and unavailable-worker behavior; defer live browser/model calls.

Acceptance: one consistent documented contract and policy; no unresolved contradiction is hidden by an implementation assumption.

### B. Establish reproducible repository/tooling

- [ ] Choose compatible Node/Python/package manager versions; pin tool declarations and dependency locks.
- [ ] Create workspace/source/test/config directories, root commands, ignore rules and placeholder-only environment template.
- [ ] Declare backend dependency groups and web dependencies; generate the API client from the authoritative schema.
- [ ] Configure formatting/lint/type checks, secret checks and dependency scanning; record any unavailable tool instead of claiming success.
- [ ] Document prerequisites and one setup command with explicit failure messages.

Acceptance: a clean checkout resolves locked dependencies and runs checks on the documented host; no credentials or generated browser data are tracked.

### C. Bring up minimum infrastructure

- [ ] Make Docker/Compose available through the normal installation process; verify runtime permission and version.
- [ ] Define web/API/Postgres/Redis services and a one-shot migration command; separate trusted service networks and loopback host bindings.
- [ ] Add health/readiness and service dependency checks, non-root images and bounded persistent volumes.
- [ ] Define worker/runner/fixture topology, credentials and deny-by-default networking; keep browser execution disabled until negative tests prove the boundary.
- [ ] Keep artifacts private and ignored; define storage quota/TTL configuration and startup validation.
- [ ] Document startup/shutdown and preserve-volume versus destructive-reset commands distinctly.

Acceptance: Compose configuration validates, required services become healthy and unintended host ports are absent. Runner isolation remains unverified until tested; configuration alone is not a passed gate.

### D. Implement a small persisted vertical slice

- [ ] Add the initial migration for projects, authorization, runs, idempotency/outbox and essential ownership/state constraints.
- [ ] Create/list projects against operator-approved fixture configuration; do not browse/fetch a URL during validation.
- [ ] Create/read a run with capped input, policy snapshot and stable typed response/error envelope.
- [ ] Persist `queued` only when a capable queued execution path exists. Otherwise return a clear 503 worker-unavailable error; test run creation through a declared test worker capability, without pretending a browser ran.
- [ ] If an infrastructure-only worker is included, process only explicitly named foundation jobs; do not consume browser runs and mark them successful.
- [ ] Build project and run-start UI with empty/loading/error states, keyboard controls and textual status.
- [ ] Show persisted run state through polling and state clearly that discovery/planning/execution are later milestones.

Acceptance: dashboard → API → Postgres path works; duplicate run submission is idempotent; no endpoint returns fabricated test results. If queue-capable run creation cannot fit safely, report that Day 1 charter criterion as incomplete rather than redefine it as a mock.

### E. Run checks with recorded evidence

- [ ] Formatting, Python lint/type checks, TypeScript checks and web build.
- [ ] API/DB tests: project authorization, invalid inputs, canonical URL/path cases, persisted run retrieval, idempotency conflict and valid state transitions.
- [ ] DB/outbox tests: simulated enqueue failure leaves dispatchable committed work, duplicate delivery cannot start duplicate execution, unavailable worker response is explicit.
- [ ] Local access tests: untrusted Origin/Host rejected, no secrets in responses/logs, artifact/path ownership contract enforced when introduced.
- [ ] One UI-to-API smoke test creates a project and exercises run creation or explicit unavailability; distinguish this from future browser-executor E2E tests.
- [ ] Migration upgrade on fresh Postgres, relevant constraint violations, and documented recovery/rollback procedure.
- [ ] Compose health/start/stop check and exposed-port inspection. Record deferred runner isolation tests as deferred.

Acceptance: record exact commands, exit results and blockers. Do not mark later Day 2–6 browser, security or evaluation gates as passed from Day 1 foundation checks.

### F. Close Day 1

- [ ] README: scope, setup, synthetic-only policy, implemented versus planned behavior, known limitations and cleanup.
- [ ] Requirements matrix: D03 FR IDs → contract/module → runnable test; mark partial and future items honestly.
- [ ] Save reviewable diffs and test evidence; update the risk/decision log with owners and dates.
- [ ] Day 2 handoff: authorized fixture pair and oracle spec, isolated runner protocol, discovery limits and required SSRF/egress/cancellation negative tests.

## 6. Security risk priorities and gates

| Risk | Priority | Required evidence before affected use |
| --- | --- | --- |
| Browser reaches host/metadata/DB/provider | Critical | Connection attempts denied from actual runner namespace, including alternate IP encodings, IPv6, redirects and subresources; fixture exception remains narrow |
| URL approval becomes self-authorization | Critical | Non-operator requests cannot add arbitrary origins or expand an active policy; revoked/expired authorization blocks work |
| Model/page injection triggers unsafe mutation/code | High | Strict schema/action refusal, fixture mutation policy, fake injection pages, no arbitrary eval or function dispatch |
| Trace/log/DOM leaks secrets | High | Seeded fake-secret checks on provider requests, logs and captures; artifact TTL/access/deletion tests |
| Retry/cancellation repeats mutation or leaks processes | High | Duplicate-delivery/crash/race tests, clean runner teardown, fixture reset, no automatic replay after unknown outcome |
| Unsupported confirmation or benchmark answer leakage | High | Independent versioned oracles, fresh successful reproduction, complete evidence, human review record; hidden labels absent from planner input |
| Overspend/resource exhaustion | High | Atomic reservations, bounded provider calls, total deadlines, runner CPU/RAM/PID limits and disk quota behavior |
| Local API abused by another origin | High | Trusted UI origin/session policy, CSRF/Host validation where applicable, loopback-only publication and ownership checks |
| Dependency/browser vulnerability | High | Compatible pinned package/browser images, scans and documented updates; no blanket claim that a container makes arbitrary sites safe |

External domains, production credentials, purchases, deletion, third-party forms and public hosting remain outside this MVP. This follows source scope; it is not a new external approval workflow. Provider, legal and domain-permission questions become gates only when the relevant live/external work is proposed. Keep Day 1 offline and synthetic.

## 7. Recommended architectural decisions

Retain D09's ADR-001 deterministic execution, ADR-002 controlled local fixtures, ADR-003 hosted planner without RAG/fine-tuning, and ADR-004 queue/worker separation. Add proposed decisions:

1. **ADR-005: split browser privileges from trusted orchestration.** A provider adapter in the same privileged browser worker does not enforce the intended trust boundary. A narrow runner protocol and directed network rules add necessary operational work before autonomous execution.
2. **ADR-006: canonical schemas and generated transport types.** One Pydantic plan/API authority prevents D07/D08 and frontend/backend drift; version prompts and benchmark manifests separately.
3. **ADR-007: durable lifecycle with outbox and leases.** Postgres/Redis are not one transaction. Explicit delivery recovery prevents lost runs and duplicate side effects; RQ remains intentionally simple.
4. **ADR-008: separate observations, verification and human review.** A failing model assertion, reproduced mismatch and human-confirmed finding are different records. This preserves evidence and supports honest metrics.
5. **ADR-009: versioned authorization and policy snapshots.** Exact destination and action scope must be fixed outside the model, with immediate revocation checks and audited changes.
6. **ADR-010: evidence lifecycle and independent evaluation.** Store artifacts privately with expiry and manifests; keep reference oracles/hidden labels in the harness and track expired evidence explicitly.

These preserve the requested technology stack and seven-day prototype intent. They increase foundation work where security or evidence integrity requires it. If time is constrained, reduce UI polish, defer the optional reporter and ship fewer demonstrated capabilities with clear limitations; never remove the network, action-policy or oracle gates to preserve a calendar promise.

## 8. Review outcome

Documentation review is complete for all fourteen actual foundational files and the hub. The design supports a bounded local synthetic prototype, with substantial subsystem contracts still to freeze. Day 1 scaffolding can proceed once foundation decisions are recorded; browser execution, live provider calls, confirmed findings and benchmark claims each remain behind their own documented prerequisites. No application implementation is included in this review.
