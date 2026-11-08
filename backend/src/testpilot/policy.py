"""Fail-closed parser and fixture authority, independent of model instructions."""

import json
from urllib.parse import urlsplit

from testpilot.contracts import AssertUrl, AssertVisible, Click, Fill, Navigate, TestPlan
from testpilot.fixtures import ORACLES, PATHS

ORIGIN = "http://fixture.test"
FILLS = {
    ("/form", "Email"): {""},
    ("/email", "Email"): {"not-an-email"},
    ("/login", "Username"): {"nobody"},
    ("/login", "Fake password"): {"wrong"},
}
CLICKS = {
    ("/form", "button", "Submit"),
    ("/email", "button", "Submit"),
    ("/login", "button", "Sign in"),
    ("/navigation", "link", "Continue"),
}


def path_allowed(path: str) -> str:
    if path not in PATHS:
        raise ValueError("path not explicitly authorized")
    return path


def request_allowed(url: str, method: str) -> bool:
    parsed = urlsplit(url)
    return (
        method == "GET"
        and parsed.scheme == "http"
        and parsed.netloc == "fixture.test"
        and not parsed.query
        and not parsed.fragment
        and parsed.path in PATHS
    )


def parse_plan(raw: bytes) -> TestPlan:
    if len(raw) > 65536:
        raise ValueError("plan exceeds 64 KiB")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError("nonfinite JSON number")

    value = json.loads(
        raw.decode("utf-8", errors="strict"),
        object_pairs_hook=pairs,
        parse_constant=reject_constant,
    )

    def depth(node, level=0):
        if level > 16:
            raise ValueError("JSON nesting exceeds 16")
        if isinstance(node, dict):
            for child in node.values():
                depth(child, level + 1)
        elif isinstance(node, list):
            for child in node:
                depth(child, level + 1)

    depth(value)
    return TestPlan.model_validate(value, strict=True)


def validate_plan(plan: TestPlan, objective: str, target_path: str, max_cases: int) -> None:
    path_allowed(target_path)
    if plan.objective != objective or not objective.strip() or len(plan.cases) > max_cases:
        raise ValueError("objective or case budget mismatch")
    for case in plan.cases:
        first = case.steps[0]
        if not isinstance(first, Navigate) or first.path != target_path:
            raise ValueError("case must begin at accepted target")
        current_path = target_path
        for step in case.steps:
            if isinstance(step, Navigate):
                path_allowed(step.path)
                if step.path != target_path:
                    raise ValueError("navigation outside case scope")
                current_path = step.path
            elif isinstance(step, Click):
                t = step.target
                if t.kind != "role" or (current_path, t.role, t.name) not in CLICKS:
                    raise ValueError("unapproved control")
            elif isinstance(step, Fill):
                if step.target.role != "textbox" or step.value not in FILLS.get(
                    (current_path, step.target.name), set()
                ):
                    raise ValueError("unapproved synthetic field/value")
            elif isinstance(step, (AssertVisible, AssertUrl)):
                if isinstance(step, AssertUrl):
                    path_allowed(step.path)
                if step.oracle_ref is None:
                    continue
                oracle = ORACLES.get(step.oracle_ref)
                expected = step.model_dump(exclude={"id", "timeout_ms", "oracle_ref"})
                if not oracle or oracle["path"] != target_path or expected != oracle["assertion"]:
                    raise ValueError("oracle provenance/assertion mismatch")
