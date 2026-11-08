"""Fixed 30-trial baseline; labels stay in harness, never in planner projection."""

import asyncio
import hashlib
import json
import random
import statistics
import subprocess
import time
from pathlib import Path

from testpilot.domain import digest
from testpilot.fixtures import ROOT, SOURCE_HASH
from testpilot.isolation import invoke
from testpilot.planner import plan_fixture


async def main():
    manifest = json.loads(Path("evaluation/manifests/smoke-v1.json").read_text())
    report = {
        "manifest": manifest,
        "manifest_sha256": digest(manifest),
        "oracle_sha256": SOURCE_HASH,
        "fixture_source_sha256": digest(
            {
                str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(ROOT.glob("*/*.html"))
            }
        ),
        "git_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip()
        or None,
        "source_files_sha256": {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(Path("backend/src/testpilot").glob("*.py"))
        }
        | {
            "scripts/evaluate.py": hashlib.sha256(
                Path("scripts/evaluate.py").read_bytes()
            ).hexdigest()
        },
        "started_at": time.time(),
        "reference_checks": [],
        "trials": [],
        "exclusions": [],
    }
    Path("evaluation/results/latest.json").write_text(json.dumps(report, indent=2) + "\n")
    # Independent handwritten checks establish paired behavior before planner evaluation.
    for path in manifest["scenarios"]:
        for defective in [False, True]:
            try:
                result = await invoke(
                    {"kind": "reference", "target_path": path, "defective": defective}
                )
            except Exception as exc:
                report["reference_checks"].append(
                    {"path": path, "defective": defective, "error": type(exc).__name__}
                )
                report["aborted"] = "reference_execution_error"
                Path("evaluation/results/latest.json").write_text(
                    json.dumps(report, indent=2) + "\n"
                )
                raise
            row = {"path": path, "defective": defective, **result}
            report["reference_checks"].append(row)
            Path("evaluation/results/latest.json").write_text(json.dumps(report, indent=2) + "\n")
            if result["conforms"] == defective:
                raise RuntimeError("reference ground truth failed: " + path)
    trials = [
        (path, defective, repeat)
        for path in manifest["scenarios"]
        for defective in [False, True]
        for repeat in range(3)
    ]
    random.Random(manifest["shuffle_seed"]).shuffle(trials)
    for index, (path, defective, repeat) in enumerate(trials):
        start = time.monotonic()
        row = {
            "path": path,
            "defective": defective,
            "repeat": repeat,
            "schema_valid": False,
            "policy_accepted": False,
            "reproduced": False,
            "evidence_complete": False,
            "error": None,
        }
        try:
            observation = await invoke(
                {"kind": "discover", "target_path": path, "defective": defective}
            )
            # No variant, hidden labels or reference results are supplied to planner.
            plan, metadata = plan_fixture(
                "Check independent fixture requirement", path, observation
            )
            row["schema_valid"] = True
            row["policy_accepted"] = True
            command = {
                "kind": "execute",
                "target_path": path,
                "defective": defective,
                "plan": plan.model_dump(),
                "objective": plan.objective,
                "max_cases": 1,
            }
            initial = await invoke(command)
            row["browser"] = initial["browser"]
            row["assessment"] = initial["assessment"]
            row["attempted_steps"] = len(initial["steps"])
            row["completed_steps"] = sum(
                s["status"] in {"passed", "assertion_failed"} for s in initial["steps"]
            )
            row["artifacts"] = [
                {"kind": a["kind"], "sha256": a["sha256"]} for a in initial["artifacts"]
            ]
            row["planner"] = metadata
            if initial["assessment"] == "suspected":
                reproduction = await invoke(command)
                row["reproduction_attempted"] = True
                row["reproduced"] = reproduction["assessment"] == "suspected"
                row["artifacts"] += [
                    {"kind": a["kind"], "sha256": a["sha256"]} for a in reproduction["artifacts"]
                ]
                row["attempted_steps"] += len(reproduction["steps"])
                row["completed_steps"] += sum(
                    s["status"] in {"passed", "assertion_failed"} for s in reproduction["steps"]
                )
                row["evidence_complete"] = len(row["artifacts"]) == 4
            row["reproduced_oracle_candidate"] = row["reproduced"] and row["evidence_complete"]
            # Human oracle review has not happened in this evaluation; no verified/accepted claim.
            row["machine_verified"] = False
            row["human_confirmed"] = False
        except Exception as exc:
            row["error"] = type(exc).__name__
        row["latency_seconds"] = round(time.monotonic() - start, 3)
        report["trials"].append(row)
        Path("evaluation/results/latest.json").write_text(json.dumps(report, indent=2) + "\n")
        print(
            f"{index + 1}/30 {path} {'seeded' if defective else 'control'}: {row.get('assessment', row['error'])}",
            flush=True,
        )
    rows = report["trials"]
    hits = {r["path"] for r in rows if r["defective"] and r.get("reproduced_oracle_candidate")}
    false_claims = {
        r["path"] for r in rows if not r["defective"] and r.get("reproduced_oracle_candidate")
    }
    report["counters"] = {
        "trials": len(rows),
        "schema_valid": sum(r["schema_valid"] for r in rows),
        "policy_accepted": sum(r["policy_accepted"] for r in rows),
        "execution_errors": sum(
            r["error"] is not None or r.get("assessment") == "test_error" for r in rows
        ),
        "attempted_steps": sum(r.get("attempted_steps", 0) for r in rows),
        "completed_steps": sum(r.get("completed_steps", 0) for r in rows),
        "unique_seeded_defects": 5,
        "unique_reproduced_candidates": len(hits) + len(false_claims),
        "unique_true_candidates": len(hits),
        "candidate_recall": {"numerator": len(hits), "denominator": 5},
        "candidate_precision": {
            "numerator": len(hits),
            "denominator": len(hits) + len(false_claims),
        },
        "false_positive_control_trials": sum(
            not r["defective"] and r.get("reproduced_oracle_candidate", False) for r in rows
        ),
        "control_trials": 15,
        "reproduction_attempts": sum(r.get("reproduction_attempted", False) for r in rows),
        "reproductions": sum(r["reproduced"] for r in rows),
        "evidence_complete_candidates": sum(r["evidence_complete"] for r in rows),
        "machine_verified": 0,
        "human_confirmed": 0,
        "machine_precision": None,
        "machine_recall": {"numerator": 0, "denominator": 5},
        "human_precision": None,
        "live_provider_calls": 0,
        "tokens": None,
        "cost": None,
        "median_latency_seconds": statistics.median(r["latency_seconds"] for r in rows),
    }
    report["finished_at"] = time.time()
    Path("evaluation/results/latest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["counters"], indent=2))


if __name__ == "__main__":
    asyncio.run(main())
