@echo off
title English AI Agent - Stop Application

echo 🛑 English AI Agent - Stop Application
echo =========================================

REM Determine which compose file to use
if exist "docker-compose.windows.yml" (
    set COMPOSE_FILE=docker-compose.windows.yml
) else (
    set COMPOSE_FILE=docker-compose.prod.yml
)

echo Using compose file: %COMPOSE_FILE%

echo 🔄 Stopping containers...
docker-compose -f %COMPOSE_FILE% down

echo 🧹 Cleaning up...
docker system prune -f

echo ✅ Application stopped and cleaned up!
echo.

echo 💡 To restart the application:
echo    - Double-click start.bat
echo    - Or run: docker-compose -f %COMPOSE_FILE% up -d

pause 