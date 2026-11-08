"""Explicit deterministic smoke baseline. No provider call is made."""

import time

from testpilot.fixtures import ORACLES
from testpilot.policy import parse_plan, validate_plan

PROMPT_VERSION = "smoke-1"


def plan_fixture(objective: str, target_path: str, observation: dict, max_cases: int = 1):
    started = time.monotonic()
    # Observation is bounded discovery data, never executed or promoted to policy.
    if len(str(observation).encode()) > 65536:
        raise ValueError("observation too large")
    oracle = next((o for o in ORACLES.values() if o["path"] == target_path), None)
    if oracle is None:
        raise ValueError("no fixture requirement for target")
    steps = [{"id": "open", "action": "navigate", "path": target_path, "timeout_ms": 5000}]

    def fill(name, value):
        steps.append(
            {
                "id": f"fill-{len(steps)}",
                "action": "fill",
                "target": {"kind": "role", "role": "textbox", "name": name},
                "value": value,
                "timeout_ms": 1000,
            }
        )

    if target_path == "/email":
        fill("Email", "not-an-email")
    if target_path == "/login":
        fill("Username", "nobody")
        fill("Fake password", "wrong")
    if target_path in {"/form", "/email", "/login", "/navigation"}:
        name = {
            "/form": "Submit",
            "/email": "Submit",
            "/login": "Sign in",
            "/navigation": "Continue",
        }[target_path]
        steps.append(
            {
                "id": "activate",
                "action": "click",
                "target": {
                    "kind": "role",
                    "role": "link" if target_path == "/navigation" else "button",
                    "name": name,
                },
                "timeout_ms": 1000,
            }
        )
    steps.append(
        {"id": "check", **oracle["assertion"], "oracle_ref": oracle["ref"], "timeout_ms": 750}
    )
    import json

    raw = json.dumps(
        {
            "schema_version": "1.0.0",
            "objective": objective,
            "cases": [
                {
                    "id": "requirement",
                    "title": oracle["requirement"],
                    "intent": "requirement",
                    "steps": steps,
                }
            ],
        }
    ).encode()
    plan = parse_plan(raw)
    validate_plan(plan, objective, target_path, max_cases)
    return plan, {
        "kind": "deterministic_smoke",
        "model": "none",
        "prompt_version": PROMPT_VERSION,
        "latency_ms": round((time.monotonic() - started) * 1000, 3),
        "input_tokens": None,
        "output_tokens": None,
        "cost": None,
        "provider_called": False,
    }
