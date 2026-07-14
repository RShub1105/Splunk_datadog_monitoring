#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:5000}"
REQUESTS="${REQUESTS:-30}"

for i in $(seq 1 "$REQUESTS"); do
  curl -fsS "$BASE_URL/" >/dev/null
  curl -fsS "$BASE_URL/health" >/dev/null
  curl -fsS "$BASE_URL/login" >/dev/null

  if (( i % 4 == 0 )); then
    curl -fsS "$BASE_URL/slow" >/dev/null
  fi

  if (( i % 5 == 0 )); then
    curl -fsS "$BASE_URL/error" >/dev/null || true
  fi

  if (( i % 10 == 0 )); then
    curl -fsS "$BASE_URL/cpu?limit=8000000" >/dev/null
  fi
done

echo "Generated $REQUESTS traffic rounds against $BASE_URL"
