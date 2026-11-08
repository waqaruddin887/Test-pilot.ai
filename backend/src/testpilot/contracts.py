from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,31}$")]
Text = Annotated[str, Field(min_length=1, max_length=256, pattern=r"\S")]
Path = Annotated[str, Field(min_length=1, max_length=2048, pattern=r"^/")]
OracleRef = Annotated[
    str, Field(min_length=3, max_length=128, pattern=r"^[A-Z][A-Z0-9_-]*@[1-9][0-9]*$")
]
Timeout = Annotated[int, Field(ge=1, le=30000)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class RoleTarget(StrictModel):
    kind: Literal["role"]
    role: Literal[
        "button",
        "link",
        "textbox",
        "checkbox",
        "radio",
        "combobox",
        "option",
        "heading",
        "status",
        "alert",
    ]
    name: Text


class TextTarget(StrictModel):
    kind: Literal["text"]
    text: Text


Target = Annotated[RoleTarget | TextTarget, Field(discriminator="kind")]


class StepBase(StrictModel):
    id: Identifier
    timeout_ms: Timeout


class Navigate(StepBase):
    action: Literal["navigate"]
    path: Path


class Click(StepBase):
    action: Literal["click"]
    target: Target


class Fill(StepBase):
    action: Literal["fill"]
    target: RoleTarget
    value: Annotated[str, Field(max_length=256)]


class AssertVisible(StepBase):
    action: Literal["assert_visible"]
    target: Target
    oracle_ref: OracleRef | None


class AssertUrl(StepBase):
    action: Literal["assert_url"]
    path: Path
    oracle_ref: OracleRef | None


Step = Annotated[Navigate | Click | Fill | AssertVisible | AssertUrl, Field(discriminator="action")]


class Case(StrictModel):
    id: Identifier
    title: Text
    intent: Literal["requirement", "exploratory"]
    steps: Annotated[list[Step], Field(min_length=1, max_length=12)]

    @model_validator(mode="after")
    def validate_case(self) -> Self:
        if len({step.id for step in self.steps}) != len(self.steps):
            raise ValueError("duplicate step id")
        checks = [step for step in self.steps if isinstance(step, (AssertVisible, AssertUrl))]
        if not checks:
            raise ValueError("case requires an assertion")
        if self.intent == "requirement" and any(s.oracle_ref is None for s in checks):
            raise ValueError("requirement assertions need oracle_ref")
        if self.intent == "exploratory" and any(s.oracle_ref is not None for s in checks):
            raise ValueError("exploratory assertions must use null oracle_ref")
        return self


class TestPlan(StrictModel):
    schema_version: Literal["1.0.0"]
    objective: Annotated[str, Field(min_length=1, max_length=1000, pattern=r"\S")]
    cases: Annotated[list[Case], Field(min_length=1, max_length=5)]

    @model_validator(mode="after")
    def unique_cases(self) -> Self:
        if len({case.id for case in self.cases}) != len(self.cases):
            raise ValueError("duplicate case id")
        return self
