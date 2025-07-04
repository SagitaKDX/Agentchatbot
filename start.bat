@echo off
title English AI Agent - Windows Startup

echo 🪟 English AI Agent - Windows Startup
echo =====================================

REM Check if Docker is running
docker version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Check if environment file exists
if not exist ".env.production" (
    if exist "backend\env.example" (
        copy "backend\env.example" ".env.production"
        echo ✅ Created .env.production from template
        echo ⚠️ Please edit .env.production with your AWS credentials
        echo Opening .env.production in notepad...
        notepad .env.production
        echo Press any key after editing the file...
        pause >nul
    ) else (
        echo ❌ backend\env.example not found
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
)

echo 🚀 Starting application...

REM Use Windows-specific compose file if available
if exist "docker-compose.windows.yml" (
    set COMPOSE_FILE=docker-compose.windows.yml
) else (
    set COMPOSE_FILE=docker-compose.prod.yml
)

echo Using compose file: %COMPOSE_FILE%

REM Stop any running containers
docker-compose -f %COMPOSE_FILE% down

REM Build and start containers
docker-compose -f %COMPOSE_FILE% build
docker-compose -f %COMPOSE_FILE% up -d

echo ✅ Application started!
echo 🌐 Frontend: http://localhost
echo 🔌 Backend API: http://localhost:5000

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Test health
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/health' -TimeoutSec 10; Write-Host '✅ Backend is healthy!' -ForegroundColor Green } catch { Write-Host '⚠️ Backend not responding yet' -ForegroundColor Yellow }"

echo.
echo 📊 Starting monitoring...
echo Press Ctrl+C to stop monitoring
echo.

REM Start monitoring
powershell -ExecutionPolicy Bypass -File "monitor.ps1" -Compact

pause 