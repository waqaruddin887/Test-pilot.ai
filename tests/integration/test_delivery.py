import asyncio
import json
import os
import uuid
import zlib

import pytest
from conftest import create_project, create_run
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from rq import Queue
from rq.serializers import JSONSerializer
from sqlalchemy import select
from testpilot.db import Job, OutboxEvent, Run
from testpilot.delivery import FUNCTION, decode_notification, delivery_id, dispatch, receive
from testpilot.worker import execute_run


@pytest.fixture
def queue():
    url = os.environ.get("TESTPILOT_TEST_REDIS_URL")
    if not url:
        pytest.skip("Explicit temporary Redis URL required")
    connection = Redis.from_url(url, socket_timeout=1)
    q = Queue("tp-test-" + uuid.uuid4().hex, connection=connection, serializer=JSONSerializer)
    yield q
    # Only this fixture's named queue, never flush a shared Redis database.
    connection.delete(q.key)
    connection.srem("rq:queues", q.key)
    connection.close()


def event_for(sessions):
    with sessions() as db:
        event = db.scalar(select(OutboxEvent))
        return event.id, event.job_id, event.generation


def due(sessions):
    with sessions.begin() as db:
        db.scalar(select(OutboxEvent)).next_attempt_at = 0


@pytest.mark.parametrize(
    "payload",
    [
        ["os.system", None, ["id"], {}],
        [FUNCTION, {}, ["x", 0], {}],
        [FUNCTION, None, ["not-uuid", 0], {}],
        [FUNCTION, None, [str(uuid.uuid4()), True], {}],
        [FUNCTION, None, [str(uuid.uuid4()), 0], {"code": "run me"}],
    ],
)
def test_notification_rejects_executable_or_invalid_payload(payload):
    with pytest.raises(ValueError):
        decode_notification(zlib.compress(json.dumps(payload).encode()))


def test_notification_rejects_pickle_and_compression_bomb():
    for payload in [b"\x80\x04pickle", zlib.compress(b"x" * 65537)]:
        with pytest.raises(ValueError):
            decode_notification(payload)


def test_admission_writes_outbox_and_cancel_suppresses_it(client, store):
    sessions, _ = store
    run_id = create_run(client, create_project(client)).json()["run_id"]
    assert event_for(sessions)[1]
    client.post("/api/runs/" + run_id + "/cancel", json={})
    with sessions() as db:
        assert db.scalar(select(OutboxEvent)).state == "suppressed"


def test_redis_outage_does_not_undo_run(client, store, queue, monkeypatch):
    sessions, _ = store
    run_id = create_run(client, create_project(client)).json()["run_id"]

    def offline(*args, **kwargs):
        raise RedisConnectionError("synthetic outage")

    with monkeypatch.context() as context:
        context.setattr(queue, "get_job_ids", offline)
        assert dispatch(sessions, queue)["unavailable"] == 1
    with sessions() as db:
        assert db.get(Run, run_id).state == "queued"
        event = db.scalar(select(OutboxEvent))
        assert event.state == "pending" and event.failures == 1
    due(sessions)
    assert dispatch(sessions, queue)["published"] == 1
    assert receive(sessions, queue) == run_id


def test_lost_ack_and_redis_data_loss_reconcile(client, store, queue):
    sessions, _ = store
    run_id = create_run(client, create_project(client)).json()["run_id"]
    dispatch(sessions, queue)
    event_id, job_id, generation = event_for(sessions)
    with sessions.begin() as db:
        event = db.get(OutboxEvent, event_id)
        event.state = "pending"
        event.next_attempt_at = 0  # Redis accepted, DB ack was lost.
    dispatch(sessions, queue)
    assert queue.count == 1
    old_data = queue.connection.hget("rq:job:" + delivery_id(job_id, generation), "data")
    queue.connection.delete(queue.key, "rq:job:" + delivery_id(job_id, generation))
    due(sessions)
    dispatch(sessions, queue)
    assert event_for(sessions)[2] == generation + 1
    old_id = delivery_id(job_id, generation)
    queue.connection.hset("rq:job:" + old_id, "data", old_data)
    queue.connection.lpush(queue.key, old_id)
    assert receive(sessions, queue) is None  # Old generation cannot execute.
    assert receive(sessions, queue) == run_id


def test_queued_cancel_and_timeout_never_deliver(client, store, queue):
    sessions, _ = store
    run_id = create_run(client, create_project(client)).json()["run_id"]
    dispatch(sessions, queue)
    client.post("/api/runs/" + run_id + "/cancel", json={})
    assert receive(sessions, queue) is None
    # Rerun retains the target but is a separate explicitly requested run.
    response = client.post(
        "/api/runs/" + run_id + "/rerun", json={}, headers={"Idempotency-Key": "expiry"}
    )
    assert response.status_code == 202
    with sessions.begin() as db:
        db.get(Run, response.json()["run_id"]).created_at -= 121
    dispatch(sessions, queue)
    with sessions() as db:
        assert db.get(Run, response.json()["run_id"]).reason == "queue_timeout"


def test_hostile_rq_callback_is_not_imported(client, store, queue):
    sessions, _ = store
    create_run(client, create_project(client))
    _, job_id, generation = event_for(sessions)
    dispatch(sessions, queue)
    key = "rq:job:" + delivery_id(job_id, generation)
    queue.connection.hset(
        key,
        "data",
        zlib.compress(json.dumps(["os.system", None, ["touch /tmp/forbidden"], {}]).encode()),
    )
    assert receive(sessions, queue) is None
    with sessions() as db:
        assert db.scalar(select(Job)).state == "pending"


def test_real_queue_to_browser_and_duplicate_delivery(client, store, queue):
    sessions, directory = store
    run_id = create_run(client, create_project(client)).json()["run_id"]
    dispatch(sessions, queue)
    assert receive(sessions, queue) == run_id
    asyncio.run(execute_run(sessions, directory, run_id))
    due(sessions)
    dispatch(sessions, queue)
    assert queue.count == 0
    with sessions() as db:
        assert db.get(Run, run_id).state == "completed"
        assert db.scalar(select(OutboxEvent)).state == "suppressed"


def test_foreground_worker_consumes_real_rq_notification(client, store, queue):
    import signal
    import subprocess
    import time

    from testpilot.db import Slot

    sessions, directory = store
    with sessions.begin() as db:
        db.get(Slot, 1).enabled = False
    environment = {
        **os.environ,
        "TESTPILOT_DATABASE_URL": sessions.kw["bind"].url.render_as_string(hide_password=False),
        "TESTPILOT_DATA_DIR": str(directory),
        "TESTPILOT_QUEUE_TRANSPORT": "redis",
        "TESTPILOT_REDIS_URL": os.environ["TESTPILOT_TEST_REDIS_URL"],
    }
    with (directory / "queue-worker.log").open("w") as log:
        process = subprocess.Popen(
            [".venv/bin/python", "-m", "testpilot.worker"],
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            for _ in range(200):
                assert process.poll() is None, "queue worker exited; inspect private test log"
                if client.get("/api/ready").status_code == 200:
                    break
                time.sleep(0.1)
            else:
                pytest.fail("queue worker readiness timeout")
            run_id = create_run(client, create_project(client)).json()["run_id"]
            for _ in range(300):
                with sessions() as db:
                    run = db.get(Run, run_id)
                    job = db.scalar(select(Job).where(Job.run_id == run_id))
                    if run.state == "completed" and job.state == "succeeded":
                        break
                    assert run.state not in {"failed", "cancelled"}, run.reason
                time.sleep(0.1)
            else:
                pytest.fail("real queue execution deadline exceeded")
            with sessions() as db:
                assert db.get(Slot, 1).proof["delivery_transport"] == "redis"
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGINT)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)


def test_actual_redis_restart_rebuilds_only_unstarted_work(client, store, queue):
    import re
    import subprocess
    import time

    from redis.exceptions import RedisError

    name = os.environ.get("TESTPILOT_TEST_REDIS_CONTAINER", "")
    if not re.fullmatch(r"testpilot-redis-test-[a-f0-9]{12}", name):
        pytest.skip("Owned disposable Redis container required for restart test")
    sessions, _ = store
    run_id = create_run(client, create_project(client)).json()["run_id"]
    dispatch(sessions, queue)
    _, job_id, generation = event_for(sessions)
    subprocess.run(["podman", "restart", name], check=True, capture_output=True, timeout=30)
    for _ in range(100):
        try:
            queue.connection.ping()
            break
        except RedisError:
            time.sleep(0.1)
    else:
        pytest.fail("Redis did not recover")
    assert queue.count == 0  # This test Redis disables persistence deliberately.
    due(sessions)
    dispatch(sessions, queue)
    assert event_for(sessions)[2] == generation + 1
    assert receive(sessions, queue) == run_id


def test_failed_outbox_insert_rolls_back_admission(client, store):
    from sqlalchemy import event as sql_event
    from sqlalchemy.exc import OperationalError
    from testpilot.db import Idempotency

    sessions, _ = store
    project = create_project(client)
    engine = sessions.kw["bind"]

    def reject_outbox(connection, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("INSERT INTO OUTBOX_EVENTS"):
            raise OperationalError("synthetic outbox failure", None, None)

    sql_event.listen(engine, "before_cursor_execute", reject_outbox)
    try:
        response = create_run(client, project)
        assert response.status_code == 503
    finally:
        sql_event.remove(engine, "before_cursor_execute", reject_outbox)
    with sessions() as db:
        for model in [Run, Job, OutboxEvent, Idempotency]:
            assert list(db.scalars(select(model))) == []


@pytest.mark.parametrize(
    "url",
    [
        "redis://127.0.0.1:6379/0",
        "http://:fake@localhost/0",
        "redis://:fake@localhost/0?socket_timeout=999",
        "redis://:fake@localhost/0#override",
    ],
)
def test_queue_configuration_rejects_unauthenticated_or_unbounded_urls(monkeypatch, url):
    from testpilot.delivery import queue_from_env

    monkeypatch.setenv("TESTPILOT_REDIS_URL", url)
    with pytest.raises(ValueError):
        queue_from_env()
