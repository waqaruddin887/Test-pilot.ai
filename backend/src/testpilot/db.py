"""Portable initial relational schema; SQLite and PostgreSQL integration-tested."""

import os
import time
import uuid
from pathlib import Path

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def uid():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(120))
    fixture: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[float] = mapped_column(Float, default=time.time)


class Authorization(Base):
    __tablename__ = "authorizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), unique=True)
    origin: Mapped[str] = mapped_column(String(100), default="http://fixture.test")
    version: Mapped[str] = mapped_column(String(20), default="offline-1")
    expires_at: Mapped[float] = mapped_column(Float)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    manifest: Mapped[dict] = mapped_column(JSON)


class OracleVersion(Base):
    __tablename__ = "oracle_versions"
    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    specification: Mapped[dict] = mapped_column(JSON)
    source_sha256: Mapped[str] = mapped_column(String(64))
    reviewed_at: Mapped[float | None] = mapped_column(Float)


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = (
        CheckConstraint("max_cases BETWEEN 1 AND 5"),
        CheckConstraint(
            "state IN ('queued','discovering','planning','executing','verifying','completed','failed','cancelled')"
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("runs.id", ondelete="SET NULL"))
    target_path: Mapped[str] = mapped_column(String(100))
    objective: Mapped[str] = mapped_column(String(1000))
    max_cases: Mapped[int] = mapped_column(Integer)
    mode: Mapped[str] = mapped_column(String(20))
    state: Mapped[str] = mapped_column(String(20), default="queued", index=True)
    active_slot: Mapped[int | None] = mapped_column(Integer, unique=True, default=1)
    created_at: Mapped[float] = mapped_column(Float, default=time.time)
    started_at: Mapped[float | None] = mapped_column(Float)
    ended_at: Mapped[float | None] = mapped_column(Float)
    cancel_requested: Mapped[bool] = mapped_column(Boolean, default=False)
    reason: Mapped[str | None] = mapped_column(String(200))
    plan: Mapped[dict | None] = mapped_column(JSON)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
    policy: Mapped[dict] = mapped_column(JSON)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), unique=True)
    state: Mapped[str] = mapped_column(String(20), default="pending")
    intent: Mapped[str | None] = mapped_column(String(64))


class Slot(Base):
    __tablename__ = "execution_slot"
    __table_args__ = (CheckConstraint("id = 1"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    heartbeat: Mapped[float] = mapped_column(Float, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    active_run: Mapped[str | None] = mapped_column(String(36))
    proof: Mapped[dict] = mapped_column(JSON, default=dict)


class CaseRecord(Base):
    __tablename__ = "cases"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), unique=True)
    definition: Mapped[dict] = mapped_column(JSON)
    assessment: Mapped[str | None] = mapped_column(String(20))


class PlanStep(Base):
    __tablename__ = "plan_steps"
    __table_args__ = (UniqueConstraint("case_id", "sequence"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    sequence: Mapped[int] = mapped_column(Integer)
    definition: Mapped[dict] = mapped_column(JSON)


class Attempt(Base):
    __tablename__ = "attempts"
    __table_args__ = (UniqueConstraint("case_id", "kind"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(20))
    assessment: Mapped[str | None] = mapped_column(String(20))
    receipt: Mapped[dict] = mapped_column(JSON, default=dict)


class StepResult(Base):
    __tablename__ = "step_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    attempt_id: Mapped[str] = mapped_column(
        ForeignKey("attempts.id", ondelete="CASCADE"), index=True
    )
    observation: Mapped[dict] = mapped_column(JSON)


class Artifact(Base):
    __tablename__ = "artifacts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    attempt_id: Mapped[str] = mapped_column(ForeignKey("attempts.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(20))
    sha256: Mapped[str] = mapped_column(String(64))
    size: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[float] = mapped_column(Float)


class Finding(Base):
    __tablename__ = "findings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    case_id: Mapped[str] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), unique=True)
    oracle_ref: Mapped[str] = mapped_column(ForeignKey("oracle_versions.id"))
    machine_state: Mapped[str] = mapped_column(String(20))
    reproduced: Mapped[bool] = mapped_column(Boolean)
    reason: Mapped[str] = mapped_column(String(256))
    manifest: Mapped[dict] = mapped_column(JSON)
    manifest_sha256: Mapped[str] = mapped_column(String(64))


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("finding_id", "sequence"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    finding_id: Mapped[str] = mapped_column(ForeignKey("findings.id", ondelete="CASCADE"))
    sequence: Mapped[int] = mapped_column(Integer)
    decision: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str] = mapped_column(String(1000))
    manifest_sha256: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[float] = mapped_column(Float, default=time.time)


class RunEvent(Base):
    __tablename__ = "run_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    state: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[float] = mapped_column(Float, default=time.time)


class Idempotency(Base):
    __tablename__ = "idempotency"
    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    request_hash: Mapped[str] = mapped_column(String(64))
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"))
    expires_at: Mapped[float] = mapped_column(Float)


class OperatorSession(Base):
    __tablename__ = "operator_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    csrf_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[float] = mapped_column(Float)


def database(url: str | None = None):
    target = url or os.environ.get("TESTPILOT_DATABASE_URL", "sqlite:///.runtime/testpilot.db")
    Path(os.environ.get("TESTPILOT_DATA_DIR", ".runtime")).mkdir(
        mode=0o700, parents=True, exist_ok=True
    )
    engine = create_engine(
        target,
        connect_args={"check_same_thread": False, "timeout": 15}
        if target.startswith("sqlite")
        else {},
    )
    if target.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def configure(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA journal_mode=WAL")

    return engine, sessionmaker(engine, expire_on_commit=False)
