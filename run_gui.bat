@echo off
setlocal

REM Run the GUI from this folder (double-click this file)
cd /d "%~dp0"

python gui.py

if errorlevel 1 (
  echo.
  echo Failed to start GUI.
  echo Make sure Python is installed and added to PATH.
  echo You can test by running: python --version
  echo.
)

pause
endlocal
