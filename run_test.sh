#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT/Backend"
pytest "$ROOT/Tests" -q
