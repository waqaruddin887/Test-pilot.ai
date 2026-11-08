import json
from pathlib import Path

from testpilot.api import app
from testpilot.contracts import TestPlan

Path("packages/contracts/openapi.json").write_text(json.dumps(app.openapi(), indent=2) + "\n")
schema = json.dumps(TestPlan.model_json_schema(mode="validation"), indent=2) + "\n"
Path("packages/contracts/test-plan-v1.schema.json").write_text(schema)
# Canonical documentation schema must stay derived from the production model.
Path("docs/contracts/test-plan-v1.schema.json").write_text(schema)
