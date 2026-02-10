@echo off
echo ========================================================
echo Starting Weibo Analysis System (Local Dev Mode)
echo ========================================================

REM Check if Redis is running (Optional check)
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [CHECK] Redis is running.
) else (
    echo [WARNING] Redis is NOT running. Please start Redis server first!
)

REM Check if MySQL is accessible (Simple check)
REM This requires mysql client in path, skipping strict check to avoid blocking

echo.
echo [1/3] Starting Backend (Flask)...
start "Backend API" cmd /k "cd src && python app.py"

echo.
echo [2/3] Starting Celery Worker...
start "Celery Worker" cmd /k "cd src && celery -A tasks.celery_worker worker --loglevel=info --pool=solo"

echo.
echo [3/3] Starting Frontend (Vue)...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo All services started in separate windows.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:5000
echo ========================================================
pause
