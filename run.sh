#!/usr/bin/env bash
# One-command local start (Linux / macOS). Safe to run again.
set -e
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
[ -d .venv ] || $PY -m venv .venv
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
[ -f .env ] || cp .env.example .env
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py runserver 0.0.0.0:8000
