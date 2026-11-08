# Canonical test-plan contract 1.0.0

Accepted 2026-11-08. [ADR-006](../adr/006-canonical-contracts.md). This is a documentation-only Pydantic v2 model specification. It is not application code or an executor. The companion [JSON Schema](test-plan-v1.schema.json) is generated from the following model; never maintain competing D07/D08 formats.

## Normative model

```python
from typing import Annotated, Literal, Self
from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,31}$")]
Text = Annotated[str, Field(min_length=1, max_length=256, pattern=r"\S")]
Path = Annotated[str, Field(min_length=1, max_length=2048, pattern=r"^/")]
OracleRef = Annotated[str, Field(min_length=3, max_length=128,
                               pattern=r"^[A-Z][A-Z0-9_-]*@[1-9][0-9]*$")]
Timeout = Annotated[int, Field(ge=1, le=30000)]

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

class RoleTarget(StrictModel):
    kind: Literal["role"]
    role: Literal["button", "link", "textbox", "checkbox", "radio",
                  "combobox", "option", "heading", "status", "alert"]
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

Step = Annotated[Navigate | Click | Fill | AssertVisible | AssertUrl,
                 Field(discriminator="action")]

class Case(StrictModel):
    id: Identifier
    title: Text
    intent: Literal["requirement", "exploratory"]
    steps: Annotated[list[Step], Field(min_length=1, max_length=12)]

    @model_validator(mode="after")
    def validate_case(self) -> Self:
        if len({step.id for step in self.steps}) != len(self.steps):
            raise ValueError("duplicate step id")
        checks = [step for step in self.steps
                  if isinstance(step, (AssertVisible, AssertUrl))]
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
```

## Complete example

```json
{
  "schema_version": "1.0.0",
  "objective": "Check required email validation",
  "cases": [{
    "id": "required-email",
    "title": "Required email is rejected",
    "intent": "requirement",
    "steps": [
      {"id":"open","action":"navigate","path":"/form","timeout_ms":30000},
      {"id":"submit","action":"click","target":{"kind":"role","role":"button","name":"Submit"},"timeout_ms":10000},
      {"id":"check","action":"assert_visible","target":{"kind":"text","text":"Email is required"},"oracle_ref":"FORM-001@1","timeout_ms":10000}
    ]
  }]
}
```

## Parsing, schema and semantic validation

1. Bound raw UTF-8 output to 64 KiB before parsing; accept exactly one JSON object, no Markdown fences. Reject duplicate JSON property keys at every depth, nonfinite numbers, nesting >16, malformed encoding and trailing data. Decode to JSON-native Python values without coercion, then `TestPlan.model_validate(value, strict=True)`. A library's ordinary JSON parser alone does not prove duplicate-key rejection.
2. All fields are required, including nullable `oracle_ref` on assertions. No defaults, numeric-string coercion, unknown properties, alternate action names or generic selector/code fields. Exact version only. Reject unsupported older/newer versions; never silently migrate model output.
3. JSON Schema describes shape, bounds and discriminated variants. Pydantic validators additionally enforce IDs and case intent. Runtime context validates max_cases requested, exact objective equality to accepted sanitized objective, nonempty normalized strings, URL canonicalization, locator/action permission, synthetic fill values, timeout clamping and oracle membership/equality. Each case must start with navigate to the accepted run target_path so fresh contexts have an explicit reproducible starting point. JSON Schema cannot enforce every runtime invariant.
4. Assertion oracle refs resolve to reviewed immutable OracleVersion rows within the same authorized fixture version. `assert_visible` means exactly the approved target becomes visible; `assert_url` means exact canonical path/query equality, never regex. Do not add arbitrary assertion operators in v1. Requirement target/path must equal the supplied oracle assertion; matching an ID alone is insufficient. Unknown/mismatched oracle rejects the plan.
5. Exploratory assertions explicitly use null refs; their observations remain inconclusive and cannot become product pass/verified claims. Mixed requirement/exploratory assertions within a case are rejected. No model-generated UUIDs, severity, diagnosis, code, permissions, absolute origin or expected-result authority are accepted.
6. Locators are exact role+accessible name or exact visible text with one match; fill permits only approved editable textbox/combobox targets. Zero/multiple matches on action resolution are test_error. A valid oracle's missing expected visible target is an assertion failure only after fixture availability and the oracle context are established; it is not silently classified as a locator error. Distinguish this from an action locator failure.
7. The strict model is not itself authorization. Trusted code revalidates, canonicalizes and hashes serialized plan bytes, then seals those bytes with the immutable policy snapshot into a run-scoped execution command. `frozen=True` prevents field reassignment, not deep mutation of Python lists; never share mutable model instances across the trust boundary.

Generate the companion schema with `TestPlan.model_json_schema(mode="validation")`. JSON Schema is a documentation artifact until generation/drift checks are wired into application CI. Pin the Pydantic dependency when implementing; changing its generated schema requires review. Every wire-format change gets a new explicit schema_version and retained reader definition; HTTP API/prompt/model/policy versions are independent. Provider structured-output compatibility is a separate pre-live-call gate; adapters may transform provider constraints, but cannot relax canonical validation.

Use Pydantic's documented [strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/), [discriminated unions](https://docs.pydantic.dev/latest/concepts/unions/), [configuration](https://docs.pydantic.dev/latest/api/config/) and [JSON Schema generation](https://docs.pydantic.dev/latest/concepts/json_schema/). These library features support structural validation; the independent safety policy remains mandatory.

## Required contract checks

Accept the example and an exploratory null-ref case. Reject extra fields at every model level, unknown actions/versions/target kinds, numeric or boolean timeouts, duplicate case/step IDs, missing assertions, wrong intent/ref combination, empty plans, >5 cases and >12 steps. Verify generated schema drift and the full parsing/contextual policy suite separately. Documentation validation results are recorded in the change report; they do not establish browser safety.
