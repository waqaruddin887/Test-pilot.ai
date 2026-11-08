"""Owned synthetic fixtures. Hidden variant selection never enters planner inputs."""

import hashlib
import json
import os
from pathlib import Path

ROOT = (
    Path(os.environ["TESTPILOT_FIXTURES"])
    if "TESTPILOT_FIXTURES" in os.environ
    else Path(__file__).resolve().parents[3] / "fixtures"
)
CATALOG = json.loads((ROOT / "requirements/oracles.json").read_text())
ORACLES = {item["ref"]: item for item in CATALOG["oracles"]}
PATHS = frozenset({o["path"] for o in ORACLES.values()} | {"/destination", "/lost"})
SOURCE_HASH = hashlib.sha256((ROOT / "requirements/oracles.json").read_bytes()).hexdigest()


def html(path: str, defective: bool) -> str:
    """Select only repository files. No arbitrary input is evaluated or interpolated."""
    if path not in PATHS:
        raise ValueError("fixture path denied")
    variant = (
        "site"
        if os.environ.get("TESTPILOT_ISOLATED") == "1"
        else "defective"
        if defective
        else "good"
    )
    return (ROOT / variant / f"{path[1:]}.html").read_text()
