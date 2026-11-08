"""Loopback single-operator API. Never accepts a destination URL or executable plan."""

import hashlib
import hmac
import os
import secrets
import time
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from testpilot.contracts import StrictModel
from testpilot.db import (
    Artifact,
    Attempt,
    Authorization,
    CaseRecord,
    Finding,
    Idempotency,
    Job,
    OperatorSession,
    OracleVersion,
    Project,
    Review,
    Run,
    RunEvent,
    Slot,
    StepResult,
    database,
)
from testpilot.domain import TERMINAL, digest, evidence_available, finding_view, transition
from testpilot.fixtures import ORACLES, PATHS, SOURCE_HASH
from testpilot.policy import path_allowed
from testpilot.responses import (
    FindingList,
    FindingResponse,
    ProjectList,
    ProjectResponse,
    RunList,
    RunResponse,
)


class ProjectInput(StrictModel):
    name: str = Field(min_length=1, max_length=120, pattern=r"\S")
    fixture_authorization_ref: Literal["synthetic-control-v1", "synthetic-seeded-v1"]


class RunInput(StrictModel):
    project_id: str = Field(min_length=36, max_length=36)
    target_path: str = Field(max_length=100)
    objective: str = Field(min_length=1, max_length=1000, pattern=r"\S")
    max_cases: int = Field(default=1, ge=1, le=5)
    mode: Literal["smoke", "planned"] = "planned"


class ReviewInput(StrictModel):
    decision: Literal["accepted", "dismissed", "unreviewed"]
    expected_review_sequence: int = Field(ge=0)
    reason: str = Field(min_length=1, max_length=1000, pattern=r"\S")
    inspected_manifest_sha256: str | None


class SessionInput(StrictModel):
    secret: str = Field(min_length=32, max_length=200)


class OracleReviewInput(StrictModel):
    inspected_source_sha256: str


class EmptyInput(StrictModel):
    pass


class APIError(Exception):
    def __init__(self, status, code, message):
        self.status, self.code, self.message = status, code, message


def error(status, code, message):
    return JSONResponse(
        status_code=status,
        content={"code": code, "message": message, "run_id": None, "safe_details": {}},
    )


def token_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def run_view(run):
    return {column.name: getattr(run, column.name) for column in Run.__table__.columns}


def create_app(sessions=None, data_dir=None, ui_origin=None):
    app = FastAPI(title="TestPilot AI", version="0.1.0")
    if sessions is None:
        _, sessions = database()
    storage = Path(data_dir or os.environ.get("TESTPILOT_DATA_DIR", ".runtime"))
    origin = ui_origin or os.environ.get("TESTPILOT_UI_ORIGIN", "http://localhost:3000")
    from urllib.parse import urlsplit

    allowed_hosts = {"localhost:8000", "127.0.0.1:8000", urlsplit(origin).netloc}
    app.state.sessions = sessions

    @app.exception_handler(APIError)
    async def api_error(_, exc):
        return error(exc.status, exc.code, exc.message)

    @app.exception_handler(IntegrityError)
    async def integrity_error(_, exc):
        return error(
            409, "integrity_conflict", "Concurrent update or relational constraint conflict."
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(_, exc):
        return error(422, "validation_error", "Request does not match the strict schema.")

    @app.middleware("http")
    async def boundary(request: Request, call_next):
        if request.headers.get("host") not in allowed_hosts:
            return error(403, "untrusted_host", "Host is not permitted.")
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 65536:
                return error(413, "body_too_large", "Request body exceeds 64 KiB.")
        request._body = bytes(body)
        public = request.url.path in {
            "/api/health",
            "/openapi.json",
            "/docs",
            "/docs/oauth2-redirect",
        }
        cli_token = os.environ.get("TESTPILOT_CLI_TOKEN", "")
        cli = bool(
            len(cli_token) >= 32
            and hmac.compare_digest(request.headers.get("authorization", ""), "Bearer " + cli_token)
        )
        mutation = request.method not in {"GET", "HEAD", "OPTIONS"}
        if mutation and not cli and request.headers.get("origin") != origin:
            return error(403, "untrusted_origin", "Exact UI Origin required.")
        if not public and request.url.path != "/api/session/bootstrap" and not cli:
            with sessions() as db:
                session = db.get(OperatorSession, token_hash(request.cookies.get("tp_session", "")))
                if not session or session.expires_at <= time.time():
                    return error(401, "unauthenticated", "Local operator session required.")
                if mutation and not hmac.compare_digest(
                    token_hash(request.headers.get("x-csrf-token", "")), session.csrf_hash
                ):
                    return error(403, "csrf_failed", "Session CSRF token required.")
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.get("/api/health")
    def health():
        return {"status": "alive", "mode": "offline_synthetic_only"}

    @app.post("/api/session/bootstrap")
    def bootstrap(body: SessionInput):
        configured = os.environ.get("TESTPILOT_OPERATOR_SECRET", "")
        if len(configured) < 32:
            raise APIError(
                503,
                "operator_unconfigured",
                "Configure a local operator secret of at least 32 characters.",
            )
        if not hmac.compare_digest(body.secret, configured):
            raise APIError(401, "unauthenticated", "Invalid local operator secret.")
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        with sessions.begin() as db:
            db.add(
                OperatorSession(
                    token_hash=token_hash(token),
                    csrf_hash=token_hash(csrf),
                    expires_at=time.time() + 28800,
                )
            )
        response = JSONResponse({"authenticated": True})
        secure = origin.startswith("https://")
        response.set_cookie(
            "tp_session", token, httponly=True, secure=secure, samesite="strict", max_age=28800
        )
        response.set_cookie(
            "tp_csrf", csrf, httponly=False, secure=secure, samesite="strict", max_age=28800
        )
        return response

    @app.get("/api/settings")
    def settings():
        with sessions() as db:
            slot = db.get(Slot, 1)
            ready = bool(slot and slot.enabled and slot.heartbeat > time.time() - 15)
            return {
                "mode": "offline_synthetic_only",
                "worker_ready": ready,
                "planner": "deterministic_smoke",
                "live_llm_available": False,
                "storage": "SQLite development adapter"
                if db.bind.dialect.name == "sqlite"
                else "PostgreSQL adapter (unverified)",
                "artifact_ttl_hours": 24,
                "metadata_ttl_days": 7,
                "isolation_proof": slot.proof if slot else {},
                "limitations": [
                    "No external targets or live LLM",
                    "No Redis/RQ or distributed recovery",
                    "Memory/PID watchdog uses polling; cgroup hard limits and release hardening pending",
                    "Independent human oracle review required for verified findings",
                ],
            }

    @app.get("/api/ready")
    def ready():
        result = settings()
        if not result["worker_ready"]:
            raise APIError(
                503, "worker_unavailable", "Start the foreground isolated fixture worker."
            )
        return result

    @app.get("/api/projects", response_model=ProjectList)
    def projects():
        with sessions() as db:
            return {
                "items": [
                    {"id": p.id, "name": p.name, "fixture": p.fixture, "created_at": p.created_at}
                    for p in db.scalars(
                        select(Project).order_by(Project.created_at.desc()).limit(100)
                    )
                ],
                "next_cursor": None,
            }

    @app.post("/api/projects", status_code=201, response_model=ProjectResponse)
    def project_create(body: ProjectInput):
        with sessions.begin() as db:
            project = Project(name=body.name.strip(), fixture=body.fixture_authorization_ref)
            db.add(project)
            db.flush()
            db.add(
                Authorization(
                    project_id=project.id,
                    expires_at=time.time() + 604800,
                    manifest={
                        "version": "offline-1",
                        "fixture_version": "1.0.0",
                        "source": "repository-authored-synthetic-fixtures",
                        "paths": sorted(PATHS),
                        "operations": "testpilot.policy.FILLS/CLICKS",
                        "oracle_sha256": SOURCE_HASH,
                    },
                )
            )
            return {"id": project.id, "name": project.name, "fixture": project.fixture}

    @app.get("/api/projects/{project_id}")
    def project_detail(project_id: str):
        with sessions() as db:
            project = db.get(Project, project_id)
            if not project:
                raise APIError(404, "not_found", "Project not found.")
            auth = db.scalar(select(Authorization).where(Authorization.project_id == project_id))
            return {
                "id": project.id,
                "name": project.name,
                "fixture": project.fixture,
                "authorization": {
                    "id": auth.id,
                    "origin": auth.origin,
                    "expires_at": auth.expires_at,
                    "revoked": auth.revoked,
                    "manifest": auth.manifest,
                },
            }

    @app.post("/api/authorizations/{authorization_id}/revoke")
    def revoke(authorization_id: str, body: EmptyInput):
        with sessions.begin() as db:
            auth = db.get(Authorization, authorization_id)
            if not auth:
                raise APIError(404, "not_found", "Authorization not found.")
            auth.revoked = True
            for run in db.scalars(
                select(Run).where(Run.project_id == auth.project_id, Run.state.not_in(TERMINAL))
            ):
                run.cancel_requested = True
            return {"revoked": True}

    def admit(body: RunInput, key: str | None, parent_id=None):
        if not key or len(key) > 100:
            raise APIError(
                422, "idempotency_required", "Supply an Idempotency-Key of at most 100 characters."
            )
        try:
            path_allowed(body.target_path)
        except ValueError:
            raise APIError(403, "policy_blocked", "Target path is not authorized.") from None
        if body.target_path not in {o["path"] for o in ORACLES.values()}:
            raise APIError(422, "no_oracle", "Choose a supported scenario path.")
        fingerprint = digest({**body.model_dump(), "parent_id": parent_id})
        try:
            with sessions.begin() as db:
                existing = db.get(Idempotency, key)
                if existing and existing.expires_at > time.time():
                    if existing.request_hash != fingerprint:
                        raise APIError(
                            409, "idempotency_conflict", "This key was used with different input."
                        )
                    return {
                        "run_id": existing.run_id,
                        "state": db.get(Run, existing.run_id).state,
                        "idempotency_expires_at": existing.expires_at,
                    }
                project = db.get(Project, body.project_id)
                if not project:
                    raise APIError(404, "not_found", "Project not found.")
                auth = db.scalar(
                    select(Authorization).where(Authorization.project_id == project.id)
                )
                if not auth or auth.revoked or auth.expires_at <= time.time():
                    raise APIError(
                        403,
                        "authorization_expired",
                        "Fixture authorization expired or was revoked.",
                    )
                if auth.manifest.get("oracle_sha256") != SOURCE_HASH:
                    raise APIError(
                        409,
                        "source_changed",
                        "Fixture requirement source changed; create a new versioned authorization.",
                    )
                if body.mode != "smoke":
                    raise APIError(
                        503,
                        "planner_unavailable",
                        "Live planner unavailable. Explicitly choose smoke mode.",
                    )
                slot = db.get(Slot, 1)
                if not slot or not slot.enabled or slot.heartbeat <= time.time() - 15:
                    raise APIError(503, "worker_unavailable", "No current isolated fixture worker.")
                if db.scalar(select(Run.id).where(Run.state.not_in(TERMINAL)).limit(1)):
                    raise APIError(429, "run_limit", "One pending or active run is permitted.")
                run = Run(
                    **body.model_dump(),
                    parent_id=parent_id,
                    policy={
                        "authorization_id": auth.id,
                        "expires_at": auth.expires_at,
                        "manifest": auth.manifest,
                        "fixture": project.fixture,
                    },
                )
                db.add(run)
                db.flush()
                db.add(Job(run_id=run.id))
                db.add(RunEvent(run_id=run.id, state="queued"))
                expiry = time.time() + 604800
                if existing:
                    db.delete(existing)
                    db.flush()
                db.add(
                    Idempotency(key=key, request_hash=fingerprint, run_id=run.id, expires_at=expiry)
                )
                return {
                    "run_id": run.id,
                    "state": "queued",
                    "created_at": run.created_at,
                    "idempotency_expires_at": expiry,
                }
        except IntegrityError:
            raise APIError(
                409, "admission_conflict", "Concurrent admission conflicted; retry the same key."
            ) from None

    @app.post("/api/runs", status_code=202)
    def run_create(body: RunInput, request: Request):
        return admit(body, request.headers.get("idempotency-key"))

    @app.get("/api/runs", response_model=RunList)
    def runs():
        with sessions() as db:
            return {
                "items": [
                    run_view(r)
                    for r in db.scalars(select(Run).order_by(Run.created_at.desc()).limit(100))
                ],
                "next_cursor": None,
            }

    @app.get("/api/runs/{run_id}", response_model=RunResponse)
    def run_detail(run_id: str):
        with sessions() as db:
            run = db.get(Run, run_id)
            if not run:
                raise APIError(404, "not_found", "Run not found.")
            result = run_view(run)
            case = db.scalar(select(CaseRecord).where(CaseRecord.run_id == run_id))
            result["assessment"] = case.assessment if case else None
            result["attempts"] = []
            if case:
                for attempt in db.scalars(select(Attempt).where(Attempt.case_id == case.id)):
                    result["attempts"].append(
                        {
                            "id": attempt.id,
                            "kind": attempt.kind,
                            "assessment": attempt.assessment,
                            "receipt": attempt.receipt,
                            "steps": [
                                s.observation
                                for s in db.scalars(
                                    select(StepResult).where(StepResult.attempt_id == attempt.id)
                                )
                            ],
                        }
                    )
            result["events"] = [
                {"state": e.state, "created_at": e.created_at}
                for e in db.scalars(
                    select(RunEvent).where(RunEvent.run_id == run_id).order_by(RunEvent.created_at)
                )
            ]
            return result

    @app.get("/api/runs/{run_id}/findings", response_model=FindingList)
    def findings(run_id: str):
        with sessions() as db:
            if not db.get(Run, run_id):
                raise APIError(404, "not_found", "Run not found.")
            return {
                "items": [
                    finding_view(db, f, storage)
                    for f in db.scalars(select(Finding).where(Finding.run_id == run_id))
                ],
                "next_cursor": None,
            }

    @app.post("/api/runs/{run_id}/cancel")
    def cancel(run_id: str, body: EmptyInput):
        with sessions.begin() as db:
            run = db.get(Run, run_id)
            if not run:
                raise APIError(404, "not_found", "Run not found.")
            if run.state in TERMINAL:
                return {"state": run.state, "already_terminal": True}
            run.cancel_requested = True
            if run.state == "queued":
                transition(db, run, "cancelled")
                db.scalar(select(Job).where(Job.run_id == run.id)).state = "cancelled"
            return {"state": run.state, "cancel_requested": True}

    @app.post("/api/runs/{run_id}/rerun", status_code=202)
    def rerun(run_id: str, body: EmptyInput, request: Request):
        with sessions() as db:
            run = db.get(Run, run_id)
            if not run:
                raise APIError(404, "not_found", "Run not found.")
            input_ = RunInput(
                project_id=run.project_id,
                target_path=run.target_path,
                objective=run.objective,
                max_cases=run.max_cases,
                mode=run.mode,
            )
        return admit(input_, request.headers.get("idempotency-key"), run_id)

    @app.get("/api/oracles")
    def oracles():
        with sessions() as db:
            return {
                "items": [
                    {
                        "ref": o.id,
                        "specification": o.specification,
                        "source_sha256": o.source_sha256,
                        "reviewed_at": o.reviewed_at,
                    }
                    for o in db.scalars(select(OracleVersion))
                ]
            }

    @app.post("/api/oracles/{ref}/review")
    def oracle_review(ref: str, body: OracleReviewInput):
        with sessions.begin() as db:
            oracle = db.get(OracleVersion, ref)
            if not oracle:
                raise APIError(404, "not_found", "Oracle not found.")
            if body.inspected_source_sha256 != oracle.source_sha256:
                raise APIError(
                    409,
                    "source_mismatch",
                    "Inspect the current requirement source before sealing review.",
                )
            if oracle.reviewed_at is None:
                oracle.reviewed_at = time.time()
            return {"ref": ref, "reviewed_at": oracle.reviewed_at}

    @app.get("/api/findings/{finding_id}", response_model=FindingResponse)
    def finding_detail(finding_id: str):
        with sessions() as db:
            finding = db.get(Finding, finding_id)
            if not finding:
                raise APIError(404, "not_found", "Finding not found.")
            result = finding_view(db, finding, storage)
            result["oracle"] = db.get(OracleVersion, finding.oracle_ref).specification
            result["reviews"] = [
                {
                    "sequence": r.sequence,
                    "decision": r.decision,
                    "reason": r.reason,
                    "created_at": r.created_at,
                }
                for r in db.scalars(
                    select(Review).where(Review.finding_id == finding_id).order_by(Review.sequence)
                )
            ]
            return result

    @app.post("/api/findings/{finding_id}/reviews", status_code=201)
    def review(finding_id: str, body: ReviewInput):
        with sessions.begin() as db:
            finding = db.scalar(select(Finding).where(Finding.id == finding_id).with_for_update())
            if not finding:
                raise APIError(404, "not_found", "Finding not found.")
            latest = db.scalar(
                select(Review)
                .where(Review.finding_id == finding_id)
                .order_by(Review.sequence.desc())
            )
            sequence = latest.sequence if latest else 0
            if body.expected_review_sequence != sequence:
                raise APIError(409, "stale_review", "Review changed; reload before submitting.")
            if body.decision == "accepted" and (
                finding.machine_state != "verified"
                or not evidence_available(db, finding, storage)
                or body.inspected_manifest_sha256 != finding.manifest_sha256
            ):
                raise APIError(
                    409,
                    "evidence_required",
                    "Acceptance requires verified, complete current evidence and inspected manifest hash.",
                )
            db.add(
                Review(
                    finding_id=finding_id,
                    sequence=sequence + 1,
                    decision=body.decision,
                    reason=body.reason,
                    manifest_sha256=body.inspected_manifest_sha256,
                )
            )
            return {"sequence": sequence + 1, "decision": body.decision}

    @app.get("/api/artifacts/{artifact_id}")
    def artifact(artifact_id: str):
        with sessions() as db:
            item = db.get(Artifact, artifact_id)
            if not item:
                raise APIError(404, "not_found", "Artifact not found.")
            if item.expires_at <= time.time():
                raise APIError(410, "artifact_expired", "Evidence has expired.")
            path = storage / "artifacts" / item.id
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item.sha256:
                raise APIError(
                    409, "artifact_corrupt", "Evidence is missing or failed its integrity check."
                )
            return FileResponse(
                path,
                media_type="image/png" if item.kind == "screenshot" else "application/zip",
                filename=item.id + (".png" if item.kind == "screenshot" else ".zip"),
                headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"},
            )

    return app


app = create_app()
