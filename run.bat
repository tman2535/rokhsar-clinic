@echo off
rem ============================================================
rem  Rokhsar clinic - one-click local start for Windows
rem  First run: creates .venv, installs packages, builds the
rem  database and loads demo content. Later runs just start.
rem  Stop the server with Ctrl+C.
rem ============================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

rem --- find Python 3.10+ -------------------------------------------
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (where python >nul 2>nul && set "PY=python")
if not defined PY goto :nopython
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" || goto :nopython

rem --- virtual environment ------------------------------------------
if not exist ".venv\Scripts\python.exe" (
  echo [1/5] Creating virtual environment...
  %PY% -m venv .venv || goto :fail
)
set "VPY=.venv\Scripts\python.exe"

echo [2/5] Installing packages ^(first run takes a few minutes^)...
"%VPY%" -m pip install --disable-pip-version-check -q --upgrade pip || goto :fail
"%VPY%" -m pip install --disable-pip-version-check -q -r requirements.txt || goto :fail

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo       Created .env from .env.example
)

echo [3/5] Preparing the database...
"%VPY%" manage.py migrate --noinput || goto :fail

echo [4/5] Loading demo content and accounts...
"%VPY%" manage.py seed_demo --if-empty || goto :fail

echo.
echo [5/5] Server is starting:
echo       Website : http://127.0.0.1:8000/fa/
echo       Panel   : http://127.0.0.1:8000/panel/   ^(doctor / doctor12345^)
echo       Admin   : http://127.0.0.1:8000/admin/   ^(admin / admin12345^)
echo       Press Ctrl+C to stop.
echo.
start "" cmd /c "timeout /t 4 /nobreak >nul & start http://127.0.0.1:8000/fa/"
"%VPY%" manage.py runserver 127.0.0.1:8000
goto :eof

:nopython
echo.
echo Python 3.10 or newer was not found.
echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH",
echo then run this file again.
pause
exit /b 1

:fail
echo.
echo Something went wrong - read the message above.
echo If it is a network error during package install, check your internet/VPN and run again.
pause
exit /b 1
