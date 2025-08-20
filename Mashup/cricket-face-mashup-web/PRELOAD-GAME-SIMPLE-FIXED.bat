@echo off
title Cricket Face Mashup - SIMPLE PRELOAD (FIXED)
echo.
echo 🏏 CRICKET FACE MASHUP - SIMPLE RELIABLE VERSION
echo ========================================
echo ⚡ Simple, fast, and reliable startup!
echo.

REM Kill existing processes
echo 🔄 Cleaning up existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

REM Get current directory dynamically
set PROJECT_DIR=%~dp0
echo 📁 Project directory: %PROJECT_DIR%

REM Set Python path
set PYTHON_EXE=C:\Users\swapnil.w\AppData\Local\Programs\Python\Python313\python.exe

echo 🐍 Using Python: %PYTHON_EXE%

REM Start backend in separate window
echo 🚀 Starting backend...
cd /d "%PROJECT_DIR%backend"
start "Backend - Keep This Open" cmd /k "echo 🔥 BACKEND STARTING... && "%PYTHON_EXE%" preload_main.py"

REM Wait for backend
echo ⏳ Waiting 10 seconds for backend...
timeout /t 10 /nobreak > nul

REM Setup frontend
echo 🌐 Setting up frontend...
cd /d "%PROJECT_DIR%frontend"

REM Copy preload configuration
echo 📋 Copying preload configuration...
copy "src\App-preload.js" "src\App.js" /y > nul

REM Start frontend in separate window
echo 🚀 Starting frontend...
start "Frontend - Keep This Open" cmd /k "echo 🔥 FRONTEND STARTING... && echo 📦 Installing dependencies if needed... && npm install && echo 🎮 Starting development server... && set BROWSER=none && npm start"

echo.
echo ✅ SIMPLE SETUP COMPLETE!
echo.
echo 📋 WHAT HAPPENS NEXT:
echo    1. Backend window: Shows Python server logs
echo    2. Frontend window: Shows React compilation
echo    3. Wait 20-30 seconds for React to compile
echo    4. Game will be ready at: http://localhost:3000
echo.
echo 🎯 SERVICES:
echo    • Backend API: http://localhost:8001
echo    • Frontend UI: http://localhost:3000 (wait for compilation)
echo.
echo 💡 TROUBLESHOOTING:
echo    • Keep both windows open
echo    • Wait for "Compiled successfully!" in frontend window
echo    • If port conflicts, close other applications using ports 3000/8001
echo.

REM Wait a bit then try to open browser
echo ⏳ Waiting 25 seconds before opening browser...
timeout /t 25 /nobreak > nul

echo 🌐 Opening game...
start http://localhost:3000

echo.
echo 🎮 Your game should be ready!
echo 📖 If not ready yet, wait for "Compiled successfully!" message
echo.

pause
