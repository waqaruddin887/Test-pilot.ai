# ADR-012: Offline synthetic fixture development mode

Date: 2026-11-08. Accepted for local implementation only.

The documentation baseline is already reconciled (ADR-001–011). It selects a
networked fixture namespace and PostgreSQL/RQ. On this host Podman cannot initialize
(`/run/user/1000/libpod` is read-only), and no PostgreSQL/Redis executable exists.
User authorization explicitly permits a lightweight development adapter and a
restricted fixture fallback. Do not claim PostgreSQL/Redis integration from SQLite tests.

Implement a development-only SQLAlchemy SQLite durable queue with one foreground
worker. PostgreSQL remains the intended store; Alembic migrations use portable
schema types. RQ, outbox dispatch and production lease fencing remain deferred.
Do not enable multiple workers; admission uses a singleton slot and live capability.
Crash recovery fails uncertain runs, never automatically replays fixture mutations.

The browser fallback serves repository-owned static synthetic fixture bytes with
Playwright request fulfillment under the neutral `http://fixture.test` origin.
It has **no network interface with connectivity**: unshare user/network namespace,
bubblewrap minimal read-only mounts, ephemeral HOME/tmp, clean environment, no
provider/database/API credentials, Chromium sandbox enabled. No `--no-sandbox`.
Only fixed fixture paths and known GET requests are fulfilled. Unknown requests,
redirects, popups, WebSockets, downloads and service workers are denied.
It cannot inspect a user-supplied website; project creation only selects fixtures.
Independent negative tests and successful sandboxed Chromium launch are required
before worker readiness. Missing prerequisites yield 503, never weaker execution.

The canonical plan remains 1.0.0 and retains five action types. Bounded assertions
provide waiting; diagnostics are trusted executor behavior, not extra model actions.
Smoke runs must be explicitly selected; planned/live mode remains unavailable until
a provider and spending policy are configured and tested. This implementation makes
no live-LLM or external-site capability claim.

Acceptance: strict parser/policy negatives; namespace socket denials; browser launch
with sandbox enabled; no secret mounts/environment; control passes and seeded
violations reproduce; artifact integrity/expiry and review gates; cancellation and
uncertain-crash handling tests. Unmet criteria are recorded, not waived.
