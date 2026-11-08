import asyncio
import json

from testpilot.isolation import invoke

print(json.dumps(asyncio.run(invoke({"kind": "probe"})), indent=2))
