#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env ]]; then
  .venv/bin/python scripts/setup_local.py
fi
set -a
source .env
set +a
export NEXT_TELEMETRY_DISABLED=1
.venv/bin/alembic upgrade head
.venv/bin/python scripts/init_db.py
pids=()
cleanup() {
  trap - INT TERM EXIT
  for pid in "${pids[@]}"; do kill -TERM -- "-$pid" 2>/dev/null || true; done
  for pid in "${pids[@]}"; do wait "$pid" 2>/dev/null || true; done
}
trap cleanup INT TERM EXIT
setsid .venv/bin/python -m uvicorn testpilot.api:app --host 127.0.0.1 --port 8000 &
pids+=("$!")
setsid .venv/bin/python -m testpilot.worker &
pids+=("$!")
setsid pnpm dev &
pids+=("$!")
echo 'Open http://localhost:3000. Ctrl-C stops all local services.'
wait -n "${pids[@]}"
