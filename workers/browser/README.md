The isolated browser entry point is `testpilot.browser`, launched only through
`testpilot.isolation`. It receives bounded commands over stdin/stdout, no DB/provider
credentials or host private directory. Run `python scripts/probe.py` to prove this
host supports the restricted offline mode. Never launch the autonomous runner with
`--no-sandbox` or outside the supervisor.
