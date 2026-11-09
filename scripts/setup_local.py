"""Create private local config once; do not overwrite existing configuration."""

import secrets
from pathlib import Path

path = Path(".env")
if path.exists():
    print(".env already exists; preserved.")
else:
    template = Path(".env.example").read_text()
    template = template.replace(
        "TESTPILOT_OPERATOR_SECRET=\n",
        "TESTPILOT_OPERATOR_SECRET=" + secrets.token_urlsafe(32) + "\n",
    )
    template = template.replace(
        "TESTPILOT_CLI_TOKEN=\n", "TESTPILOT_CLI_TOKEN=" + secrets.token_urlsafe(32) + "\n"
    )
    with path.open("x") as output:
        path.chmod(0o600)
        output.write(template)
    print("Created private .env. Use its operator secret to unlock the local UI.")
