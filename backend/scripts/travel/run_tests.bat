@echo off
set ROOT=%~dp0..
cd /d "%ROOT%"

echo === Installing backend deps ===
cd backend
call .venv\Scripts\activate
pip install -q reportlab==4.2.2
cd ..

echo === Running API tests (backend must be running on port 5002) ===
python scripts\test_api_flow.py
if errorlevel 1 (
  echo.
  echo Tests failed. Start backend first in another window:
  echo   cd backend ^& .venv\Scripts\activate ^& python run.py
  exit /b 1
)

echo.
echo === All tests passed ===
echo.
echo Start the app:
echo   Window 1: cd backend ^& .venv\Scripts\activate ^& python run.py
echo   Window 2: cd frontend ^& npm install ^& npm run dev
echo   Open: http://localhost:5173
