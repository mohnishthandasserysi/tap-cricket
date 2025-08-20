@echo off
title Test Split-Screen Face Blending
echo.
echo 🎯 TESTING NEW SPLIT-SCREEN FACE BLENDING
echo =========================================
echo.

REM Kill any existing processes
taskkill /f /im python.exe >nul 2>&1
echo 🔄 Cleaned existing processes

REM Start backend
echo 🚀 Starting backend with split-screen blending...
cd /d "D:\Swapnil\Hackathon-2024\cricket-face-mashup-web\backend"
start "Backend Test" cmd /k "echo 🎭 SPLIT-SCREEN FACE BLENDING BACKEND && C:\Users\swapnil.w\AppData\Local\Programs\Python\Python313\python.exe preload_main.py"

REM Wait for backend
echo ⏳ Waiting 8 seconds for backend to start...
timeout /t 8 /nobreak > nul

REM Test the API
echo 🧪 Testing create-mashup endpoint...
curl -X POST http://localhost:8001/create-mashup
echo.

echo.
echo ✅ Test complete!
echo 💡 If you see a large base64 response above, the split-screen blending is working!
echo 🎮 You can now test it in the frontend at: http://localhost:3000
echo.
pause

