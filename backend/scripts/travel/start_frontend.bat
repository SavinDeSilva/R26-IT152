@echo off
set ROOT=%~dp0..
cd /d "%ROOT%\frontend"
if not exist node_modules (
  echo Installing frontend dependencies...
  call npm install
)
echo Starting Vite frontend on http://localhost:5173
call npm run dev
