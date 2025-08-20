@echo off
echo.
echo ========================================
echo    Cricket Face Mashup - Horizontal
echo ========================================
echo.
echo Starting horizontal face mashup server...
echo.
echo Features:
echo - Horizontal transparency gradient
echo - Configurable transition points
echo - Canny edge detection
echo - Real-time configuration updates
echo.
echo Server will start on: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import cv2, numpy, fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install opencv-python numpy fastapi uvicorn
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
)

echo.
echo Starting server...
echo.

REM Start the horizontal mashup server
python horizontal_main.py

echo.
echo Server stopped.
pause
