@echo off
set ROOT=%~dp0..\..\..
cd /d "%ROOT%\components\shared\frontend"
if not exist node_modules (
  echo Installing frontend dependencies...
  call npm install
)
echo Starting Vite frontends
call npm run dev
