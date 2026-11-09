# ADR-014: Transactional outbox with restricted RQ JSON notifications

Date: 2026-11-09. Accepted for the single-host fixture runtime.

Keep PostgreSQL/SQLite authoritative. Admission writes Run, Job, OutboxEvent and
idempotency in one transaction. Migration 0002 backfills existing pending queued
jobs without changing runs; downgrade removes delivery metadata only. Local polling
remains the explicit default. Optional TESTPILOT_QUEUE_TRANSPORT=redis uses a private,
authenticated TESTPILOT_REDIS_URL, with bounded connection timeouts and no library
transport retries. Unknown transports and URL timeout overrides fail closed.

RQ 3.0.0 creates JSON notifications containing only a database job UUID and dispatch
generation. The foreground consumer deliberately does not use generic RQ workers,
Job.fetch, pickle, Job.perform, callbacks or dynamic imports from queue data. It
reads only RQ's compressed JSON data field with strict input/decompression bounds,
checks the fixed function marker, empty instance/kwargs and exact UUID/generation,
then calls the trusted executor directly. The marker function fails if accidentally
invoked through a generic rq worker. This is an intentionally restricted consumer
of the pinned RQ format; generic RQ CLI/dashboard execution semantics are not claimed.

Dispatch uses a stable job/generation identity and acknowledges only after enqueue.
Lost acknowledgments reconcile against existing queued IDs. Redis data loss or a
pop-before-DB-claim crash can create a new notification generation, but only while
the DB run remains queued. Old generations are rejected; claim is a SQL CAS, so
notifications cannot restart active/terminal work. Backoff is 1,2,4,8,16,30 seconds,
clamped to the original 120-second queue deadline. Expiry and queued cancellation
suppress dispatch. A degraded/restored event is visible in run history. No browser
step or uncertain active attempt is automatically retried.

The current outbox is one mutable delivery cursor per job, not the full baseline's
append-only generation/command receipt ledger. The existing foreground host lock,
one-run admission and CAS remain required. Do not start generic RQ workers, multiple
hosts, or workers with different data directories against this store. Distributed
leases/epoch fencing and signed supervisor capabilities remain future work. Adding
Redis does not grant browser network access or send DB/Redis/provider credentials
to the browser child. No exactly-once side-effect guarantee is claimed.

Acceptance covers database commit/enqueue gaps, failed admission rollback, lost ack,
real Redis restart, old generations, duplicates, cancellation/expiry, unsafe payload
and compression-bomb rejection, foreground worker execution, and migration backfill.
The reproducible test runner owns pinned, authenticated temporary PostgreSQL/Redis
containers and removes both even when cleanup of one fails. It does not prune
unrelated containers, modify existing .env or mount application data.
