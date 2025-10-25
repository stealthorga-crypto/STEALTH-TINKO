@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Windows batch launcher for Tinko Recovery Platform
set PORT_BACKEND=%PORT_BACKEND%
if "%PORT_BACKEND%"=="" set PORT_BACKEND=8010
set API_URL=http://127.0.0.1:%PORT_BACKEND%

pushd %~dp0

REM Start backend
start "tinko-backend" /MIN "C:\Python313\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port %PORT_BACKEND% --reload

REM Small delay
ping -n 3 127.0.0.1 > nul

REM Start frontend (pass env)
set NEXT_PUBLIC_API_URL=%API_URL%
cd tinko-console
if not exist node_modules (
  npm install
)
start "tinko-frontend" /MIN cmd /c "set NEXT_PUBLIC_API_URL=%NEXT_PUBLIC_API_URL% && npm run dev"

popd

echo Backend:  %API_URL%/docs
echo Frontend: http://localhost:3000
echo Health:   %API_URL%/healthz

endlocal
