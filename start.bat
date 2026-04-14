@echo off
chcp 65001 >nul
title AI Smart CS - Start

echo ==============================
echo   Starting Redis (6379)
echo ==============================
:: Check if Redis is already running
netstat -ano | findstr ":6379.*LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo Redis is already running, skipping...
) else (
    if exist "C:\Program Files\Redis\redis-server.exe" (
        start "Redis" /min "C:\Program Files\Redis\redis-server.exe"
        echo Redis started.
    ) else (
        echo [WARNING] redis-server.exe not found! Backend may fail.
        echo Please install Redis: https://github.com/tporadowski/redis/releases
    )
)

echo ==============================
echo   Starting Frontend (5175)
echo ==============================
cd /d "%~dp0frontend"
start "Frontend" cmd /k "npm run dev"

echo ==============================
echo   Starting Backend (8015)
echo ==============================
cd /d "%~dp0backend"
start "Backend" cmd /k "python -m alembic -c alembic.ini upgrade head && python -m uvicorn app.main_v2:app --host 0.0.0.0 --port 8015 --reload"

echo.
echo Redis:    localhost:6379
echo Frontend: http://localhost:5175
echo Backend:  http://localhost:8015
echo API Docs: http://localhost:8015/docs
echo.
pause
