#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

if [ ! -d "$ROOT/Frontend/node_modules" ]; then
  (cd "$ROOT/Frontend" && npm install --no-audit --no-fund)
fi

"$ROOT/run_backend.sh" &
BACK_PID=$!
trap 'kill "$BACK_PID" 2>/dev/null || true' EXIT
(cd "$ROOT/Frontend" && npm run dev)
