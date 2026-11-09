"""Single-host transactional outbox and restricted RQ JSON notification consumer."""

import json
import logging
import os
import re
import time
import uuid
import zlib
from urllib.parse import urlsplit

from redis import Redis
from redis.backoff import NoBackoff
from redis.exceptions import RedisError
from redis.retry import Retry
from rq import Queue
from rq.serializers import JSONSerializer
from sqlalchemy import select

from testpilot.db import Job, OutboxEvent, Run, RunEvent
from testpilot.domain import atomic_transition

FUNCTION = "testpilot.delivery.notification"
ID_PATTERN = re.compile(r"^tp-[a-f0-9-]{36}-g[0-9]{1,9}$")


def notification(job_id: str, generation: int):
    raise RuntimeError("Use the restricted TestPilot consumer, never a generic rq worker")


def queue_from_env() -> Queue:
    url = os.environ["TESTPILOT_REDIS_URL"]
    parsed = urlsplit(url)
    if (
        parsed.scheme not in {"redis", "rediss"}
        or not parsed.hostname
        or not parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Authenticated Redis URL without query overrides required")
    client = Redis.from_url(
        url, socket_connect_timeout=1, socket_timeout=1, retry=Retry(NoBackoff(), 0)
    )
    return Queue("testpilot-browser-v1", connection=client, serializer=JSONSerializer)


def delivery_id(job_id: str, generation: int) -> str:
    return f"tp-{job_id}-g{generation}"


def decode_notification(data: bytes) -> tuple[str, int]:
    if len(data) > 65536:
        raise ValueError("notification too large")
    inflater = zlib.decompressobj()
    try:
        raw = inflater.decompress(data, 65537)
        if len(raw) > 65536 or not inflater.eof or inflater.unused_data:
            raise ValueError("invalid compressed notification")
    except zlib.error as exc:
        raise ValueError("RQ notification must be compressed JSON") from exc
    try:
        payload = json.loads(raw)
    except (ValueError, RecursionError) as exc:
        raise ValueError("invalid notification JSON") from exc
    if not isinstance(payload, list) or len(payload) != 4:
        raise ValueError("invalid notification envelope")
    function, instance, args, kwargs = payload
    if (
        function != FUNCTION
        or instance is not None
        or kwargs != {}
        or not isinstance(args, list)
        or len(args) != 2
    ):
        raise ValueError("unapproved queued operation")
    job_id, generation = args
    if (
        not isinstance(job_id, str)
        or str(uuid.UUID(job_id)) != job_id
        or type(generation) is not int
        or not 0 <= generation < 10**9
    ):
        raise ValueError("invalid notification identity")
    return job_id, generation


def dispatch(sessions, queue: Queue) -> dict:
    """Redis acknowledgments are advisory; DB run state governs all re-delivery."""
    counters = {"published": 0, "unavailable": 0}
    with sessions() as db:
        ids = list(
            db.scalars(
                select(OutboxEvent.id)
                .where(
                    OutboxEvent.state.in_(["pending", "published"]),
                    OutboxEvent.next_attempt_at <= time.time(),
                )
                .limit(100)
            )
        )
    for event_id in ids:
        with sessions.begin() as db:
            event = db.scalar(
                select(OutboxEvent).where(OutboxEvent.id == event_id).with_for_update()
            )
            if event is None or event.state not in {"pending", "published"}:
                continue
            job = db.get(Job, event.job_id)
            run = db.get(Run, job.run_id)
            if run.state != "queued" or run.cancel_requested:
                event.state = "suppressed"
                continue
            if run.created_at + 120 <= time.time():
                if atomic_transition(db, run.id, "queued", "failed"):
                    run.reason = "queue_timeout"
                    job.state = "failed"
                event.state = "expired"
                continue
            try:
                identity = delivery_id(job.id, event.generation)
                queued = queue.get_job_ids(offset=0, length=100)
                if identity not in queued:
                    if event.state == "published":
                        event.generation += 1
                        identity = delivery_id(job.id, event.generation)
                    queue.enqueue_call(
                        FUNCTION,
                        args=[job.id, event.generation],
                        kwargs={},
                        job_id=identity,
                        ttl=max(1, int(run.created_at + 120 - time.time())),
                        result_ttl=0,
                        failure_ttl=120,
                        unique=True,
                        description="TestPilot fixed run notification",
                    )
                if event.state == "pending" and event.failures:
                    db.add(RunEvent(run_id=run.id, state="delivery_restored"))
                event.state = "published"
                event.published_at = time.time()
                event.next_attempt_at = min(run.created_at + 120, time.time() + 5)
                counters["published"] += 1
            except RedisError:
                if event.failures == 0:
                    db.add(RunEvent(run_id=run.id, state="delivery_unavailable"))
                event.failures += 1
                event.next_attempt_at = min(
                    run.created_at + 120, time.time() + min(30, 2 ** min(event.failures - 1, 5))
                )
                counters["unavailable"] += 1
    return counters


def receive(sessions, queue: Queue) -> str | None:
    """Read only RQ's compressed JSON data field; never Job.fetch/perform/pickle."""
    identity = queue.connection.lpop(queue.key)
    if identity is None:
        return None
    try:
        text = identity.decode("ascii")
        if not ID_PATTERN.fullmatch(text):
            raise ValueError("unapproved queue identity")
        data = queue.connection.hget("rq:job:" + text, "data")
        if data is None:
            return None  # A later DB reconciliation restores a lost notification.
        job_id, generation = decode_notification(data)
        if text != delivery_id(job_id, generation):
            raise ValueError("mismatched notification identity")
        with sessions() as db:
            event = db.scalar(select(OutboxEvent).where(OutboxEvent.job_id == job_id))
            job = db.get(Job, job_id)
            if not event or not job or event.generation != generation or event.state != "published":
                return None
            run = db.get(Run, job.run_id)
            if run.state != "queued" or run.cancel_requested or job.state != "pending":
                return None
            return run.id
    except (ValueError, UnicodeError, TypeError):
        logging.getLogger("testpilot").warning("delivery_rejected:invalid_notification")
        return None
    finally:
        # Notification metadata is disposable; no queued callback/result is executed.
        if isinstance(identity, bytes) and len(identity) < 128:
            try:
                text = identity.decode("ascii")
                if ID_PATTERN.fullmatch(text):
                    queue.connection.delete("rq:job:" + text)
            except UnicodeError:
                pass
