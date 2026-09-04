#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/Backend"

if [ ! -f .env ]; then cp .env.example .env; fi
if grep -q '^SECRET_KEY=replace-with-a-long-random-secret' .env; then
  SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
  sed -i "s#^SECRET_KEY=.*#SECRET_KEY=$SECRET#" .env
fi

if [ ! -d backend_venv ]; then python3 -m venv backend_venv; fi
source backend_venv/bin/activate
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
python app.py
