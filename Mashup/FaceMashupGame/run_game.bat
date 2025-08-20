@echo off
cd /d "D:\Swapnil\Hackathon-2024\FaceMashupGame"
echo 🎭 Face Mashup Game Launcher
echo ============================
echo.
echo Checking setup...
python test_setup.py
echo.
echo Starting game...
echo Press any key to launch the Face Mashup Game
pause > nul
python main.py
echo.
echo Game ended. Press any key to close...
pause > nul
