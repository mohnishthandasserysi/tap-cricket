@echo off
echo.
echo ========================================
echo    Edge Detection System Tests
echo ========================================
echo.
echo This will test the complete edge detection pipeline:
echo - Basic functionality
echo - Different configurations
echo - Noise handling
echo - Pipeline steps
echo - Performance testing
echo.
echo Results will be saved to Output/test_edge_detection_*
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
echo Starting edge detection tests...
echo.

REM Run the edge detection tests
python test_edge_detection.py

echo.
echo Tests completed. Check the Output directory for results.
pause
