The deterministic smoke planner lives in `backend/src/testpilot/planner.py`.
It is explicit, fixture-compatible and makes no provider requests. Planned/live
mode returns 503 until a provider adapter, token/spend reservations and terms are
configured and tested. No silent fallback from planned to smoke mode exists.
