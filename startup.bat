@echo off
REM This script will start both servers in separate CMD windows

REM Get the current directory path
set PROJECT_DIR=%~dp0

REM Start Python API server in a new CMD window
start "Futu API Server" cmd /k "cd /d "%PROJECT_DIR%futu" && python api.py"

REM Start Node-RED server in a new CMD window
start "Node-RED Server" cmd /k "cd /d "%PROJECT_DIR%server" && node-red -u ."

REM Optional: Minimize this original window
REM timeout /t 1 >nul
REM if "%1"=="" powershell -window minimized -command "start cmd /k \"%~f0 minimized\" && exit"