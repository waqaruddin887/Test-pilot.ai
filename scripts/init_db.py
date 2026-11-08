from testpilot.db import Base, OracleVersion, Slot, database
from testpilot.fixtures import ORACLES, SOURCE_HASH

engine, sessions = database()
Base.metadata.create_all(engine)
with sessions.begin() as session:
    if not session.get(Slot, 1):
        session.add(Slot(id=1))
    for ref, oracle in ORACLES.items():
        if not session.get(OracleVersion, ref):
            session.add(OracleVersion(id=ref, specification=oracle, source_sha256=SOURCE_HASH))
print("Initialized disposable local development data; oracles await human review.")
