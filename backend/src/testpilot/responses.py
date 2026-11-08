"""API response contracts; generated TypeScript transport types come from OpenAPI."""

from pydantic import BaseModel, JsonValue

from testpilot.contracts import TestPlan


class ProjectResponse(BaseModel):
    id: str
    name: str
    fixture: str
    created_at: float | None = None


class ProjectList(BaseModel):
    items: list[ProjectResponse]
    next_cursor: str | None


class AttemptResponse(BaseModel):
    id: str
    kind: str
    assessment: str | None
    receipt: dict[str, JsonValue]
    steps: list[dict[str, JsonValue]]


class EventResponse(BaseModel):
    state: str
    created_at: float


class RunResponse(BaseModel):
    id: str
    project_id: str
    parent_id: str | None
    target_path: str
    objective: str
    max_cases: int
    mode: str
    state: str
    created_at: float
    started_at: float | None
    ended_at: float | None
    cancel_requested: bool
    reason: str | None
    plan: TestPlan | None
    provenance: dict[str, JsonValue]
    policy: dict[str, JsonValue]
    assessment: str | None = None
    attempts: list[AttemptResponse] = []
    events: list[EventResponse] = []


class RunList(BaseModel):
    items: list[RunResponse]
    next_cursor: str | None


class FindingResponse(BaseModel):
    id: str
    run_id: str
    case_id: str
    oracle_ref: str
    machine_state: str
    reproduced: bool
    reason: str
    review_state: str
    review_sequence: int
    confirmed: bool
    evidence_available: bool
    manifest: dict[str, JsonValue]
    manifest_sha256: str
    oracle: dict[str, JsonValue] | None = None
    reviews: list[dict[str, JsonValue]] = []


class FindingList(BaseModel):
    items: list[FindingResponse]
    next_cursor: str | None
