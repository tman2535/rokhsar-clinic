#!/usr/bin/env bash
# =============================================================
#  Rokhsar clinic — one-command local start (Linux / macOS)
#  First run: creates .venv, installs packages, builds the
#  database and loads demo content. Later runs just start.
#  Usage:  ./run.sh            (or: bash run.sh)
#  Stop the server with Ctrl+C.
# =============================================================
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8

# --- find Python 3.10+ ------------------------------------------
PY=""
for cand in "${PYTHON:-}" python3.13 python3.12 python3.11 python3.10 python3; do
  [ -n "$cand" ] || continue
  if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then
    PY="$cand"; break
  fi
done
if [ -z "$PY" ]; then
  echo "Python 3.10 or newer was not found. Install it (e.g. 'sudo apt install python3 python3-venv' or from python.org) and run again."
  exit 1
fi

# --- virtual environment -----------------------------------------
if [ ! -x .venv/bin/python ]; then
  echo "[1/5] Creating virtual environment..."
  "$PY" -m venv .venv || { echo "On Debian/Ubuntu run: sudo apt install python3-venv"; exit 1; }
fi
VPY=.venv/bin/python

echo "[2/5] Installing packages (first run takes a few minutes)..."
"$VPY" -m pip install --disable-pip-version-check -q --upgrade pip
"$VPY" -m pip install --disable-pip-version-check -q -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "      Created .env from .env.example"
fi

echo "[3/5] Preparing the database..."
"$VPY" manage.py migrate --noinput

echo "[4/5] Loading demo content and accounts..."
"$VPY" manage.py seed_demo --if-empty

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
echo
echo "[5/5] Server is starting:"
echo "      Website : http://$HOST:$PORT/fa/"
echo "      Panel   : http://$HOST:$PORT/panel/   (doctor / doctor12345)"
echo "      Admin   : http://$HOST:$PORT/admin/   (admin / admin12345)"
echo "      Press Ctrl+C to stop."
echo
# Open the browser a moment after the server starts (if a desktop is available).
( sleep 4; { command -v xdg-open >/dev/null && xdg-open "http://$HOST:$PORT/fa/"; } || { command -v open >/dev/null && open "http://$HOST:$PORT/fa/"; } ) >/dev/null 2>&1 &
exec "$VPY" manage.py runserver "$HOST:$PORT"
