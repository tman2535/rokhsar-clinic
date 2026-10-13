@echo off
rem One-command local start (Windows). Safe to run again.
cd /d "%~dp0"
if not exist .venv (py -3 -m venv .venv || python -m venv .venv)
call .venv\Scripts\activate.bat
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt
if not exist .env copy .env.example .env
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
