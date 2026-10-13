#!/usr/bin/env bash
# =============================================================
#  Rokhsar clinic — production start (Linux server, no root needed)
#  - creates .venv and installs packages
#  - creates .env with a random secret key on first run (DEBUG off)
#  - migrates, collects static files, loads content (no demo users)
#  - starts gunicorn on 127.0.0.1:8001 (put nginx in front of it)
#
#  Usage:  bash deploy/production.sh example.ir
#          (domain only needed on the first run, to write .env)
# =============================================================
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
DOMAIN="${1:-}"
BIND="${BIND:-127.0.0.1:8001}"
WORKERS="${WORKERS:-3}"

PY=""
for cand in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then PY="$cand"; break; fi
done
[ -n "$PY" ] || { echo "Python 3.10+ not found (sudo apt install python3 python3-venv)"; exit 1; }

[ -x .venv/bin/python ] || "$PY" -m venv .venv
VPY=.venv/bin/python
"$VPY" -m pip install --disable-pip-version-check -q --upgrade pip
"$VPY" -m pip install --disable-pip-version-check -q -r requirements.txt

if [ ! -f .env ]; then
  [ -n "$DOMAIN" ] || { echo "First run: give your domain, e.g.  bash deploy/production.sh example.ir"; exit 1; }
  SECRET=$("$VPY" -c 'import secrets; print(secrets.token_urlsafe(50))')
  cat > .env <<ENV
DJANGO_SECRET_KEY=$SECRET
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
SITE_BASE_URL=https://$DOMAIN
DEMO_CONTENT=1
SERVE_MEDIA=0
# Set to 1 once https (certbot) is working:
SECURE_COOKIES=0
ENV
  chmod 600 .env
  echo "Created .env for $DOMAIN (DEBUG off, random secret key)."
fi

"$VPY" manage.py migrate --noinput
"$VPY" manage.py collectstatic --noinput -v0
"$VPY" manage.py seed_demo --if-empty --no-users

# Ask for an administrator account once.
if ! "$VPY" manage.py shell -c "from django.contrib.auth.models import User; import sys; sys.exit(0 if User.objects.filter(is_superuser=True).exists() else 1)"; then
  if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
    "$VPY" manage.py createsuperuser --noinput --email "${DJANGO_SUPERUSER_EMAIL:-admin@localhost}"
  else
    echo "Create the administrator account:"
    "$VPY" manage.py createsuperuser
  fi
fi

"$VPY" manage.py check --deploy --fail-level ERROR
echo "Starting gunicorn on $BIND ..."
exec .venv/bin/gunicorn config.wsgi --bind "$BIND" --workers "$WORKERS" --timeout 60 --access-logfile - --error-logfile -
