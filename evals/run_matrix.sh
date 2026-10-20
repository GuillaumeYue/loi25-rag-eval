#!/usr/bin/env bash
# Run both suites (accuracy, red team) against six backend configurations:
# the baseline and each mitigation alone, then all four together. For each
# configuration this script starts its own backend on :8000 with the flags in
# the environment, records /health, empties the mock outbox, runs promptfoo,
# writes the Markdown summaries, and stops the backend. compare.py then builds
# the baseline-vs-mitigation table from the same day's files.
#
# Usage: cd evals && ./run_matrix.sh            (DATE=YYYY-MM-DD to override)
# Needs: ANTHROPIC_API_KEY and LLM_PROVIDER=anthropic in ../.env, PostgreSQL up,
#        nothing else listening on port 8000. Takes ~15 min, costs ~1 USD.
set -euo pipefail
cd "$(dirname "$0")"

DATE="${DATE:-$(date +%F)}"
PORT=8000
BACKEND="http://localhost:${PORT}"
LOG_DIR=".matrix-logs"
mkdir -p results "$LOG_DIR"

set -a
# shellcheck disable=SC1091
source ../.env
set +a
# Flags come only from this script, never from the shell or .env.
unset ENFORCE_ACCESS_CONTROL ISOLATE_CONTEXT TOOL_GUARD OUTPUT_FILTER

if lsof -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT is in use; stop the dev backend first." >&2
  exit 1
fi

LABELS=(baseline acl isolate toolguard outfilter all)
flags_for() {
  case "$1" in
    baseline)  echo "" ;;
    acl)       echo "ENFORCE_ACCESS_CONTROL=1" ;;
    isolate)   echo "ISOLATE_CONTEXT=1" ;;
    toolguard) echo "TOOL_GUARD=1" ;;
    outfilter) echo "OUTPUT_FILTER=1" ;;
    all)       echo "ENFORCE_ACCESS_CONTROL=1 ISOLATE_CONTEXT=1 TOOL_GUARD=1 OUTPUT_FILTER=1" ;;
  esac
}

PID=""
stop_backend() {
  if [[ -n "$PID" ]]; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
    PID=""
  fi
}
trap stop_backend EXIT

run_suite() {  # $1 suite name, $2 label, rest: extra promptfoo args
  local suite="$1" label="$2"; shift 2
  local out="results/${DATE}-${suite}-${label}.json"
  rm -f "$out"
  # promptfoo exits non-zero when any test fails, which is expected here;
  # a missing output file is what signals a real failure.
  npx promptfoo eval -c "promptfooconfig.${suite}.yaml" --no-cache -o "$out" "$@" \
    > "$LOG_DIR/promptfoo-${suite}-${label}.log" 2>&1 || true
  if [[ ! -s "$out" ]]; then
    echo "  ${suite}: no output, see $LOG_DIR/promptfoo-${suite}-${label}.log" >&2
    exit 1
  fi
  grep -E "passed \(|failed \(|errors \(" "$LOG_DIR/promptfoo-${suite}-${label}.log" | tr -s ' ' | sed 's/^/  /'
}

for label in "${LABELS[@]}"; do
  flags="$(flags_for "$label")"
  echo "== ${label} (${flags:-no flags})"
  # shellcheck disable=SC2086
  env $flags ../.venv/bin/uvicorn app.api:app --app-dir ../backend --port "$PORT" \
    > "$LOG_DIR/uvicorn-${label}.log" 2>&1 &
  PID=$!
  for _ in $(seq 1 90); do
    curl -sf "$BACKEND/health" >/dev/null 2>&1 && break
    sleep 1
  done
  curl -sf "$BACKEND/health" > "results/${DATE}-health-${label}.json" || {
    echo "  backend did not start, see $LOG_DIR/uvicorn-${label}.log" >&2; exit 1; }
  # Sanity check: the backend reports exactly the flags this config asked for.
  on=$(grep -o '"[A-Z_]*":true' "results/${DATE}-health-${label}.json" | wc -l | tr -d ' ')
  want=$(wc -w <<< "$flags" | tr -d ' ')
  [[ "$on" == "$want" ]] || { echo "  flags mismatch: $on on, expected $want" >&2; exit 1; }
  curl -sf -X DELETE "$BACKEND/tool-calls" >/dev/null

  run_suite accuracy "$label"
  run_suite redteam "$label" --repeat 3
  ../.venv/bin/python summarize.py "results/${DATE}-accuracy-${label}.json" \
    --label "$label" --backend "$BACKEND" > /dev/null
  ../.venv/bin/python summarize.py "results/${DATE}-redteam-${label}.json" \
    --label "$label" --backend "$BACKEND" --group-by owasp > /dev/null
  stop_backend
done

../.venv/bin/python compare.py --date "$DATE"
