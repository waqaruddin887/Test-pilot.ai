from testpilot.db import OracleVersion, Slot, database
from testpilot.fixtures import ORACLES, SOURCE_HASH

engine, sessions = database()
with sessions.begin() as session:
    if not session.get(Slot, 1):
        session.add(Slot(id=1))
    for ref, oracle in ORACLES.items():
        existing = session.get(OracleVersion, ref)
        if existing and (existing.source_sha256 != SOURCE_HASH or existing.specification != oracle):
            raise RuntimeError(
                "Published oracle source changed under an existing revision; use a new version/store."
            )
        if not existing:
            session.add(OracleVersion(id=ref, specification=oracle, source_sha256=SOURCE_HASH))
print("Initialized disposable local development data; oracles await human review.")
