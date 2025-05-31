@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "VENV_PATH=%SCRIPT_DIR%venv"
set "LOGS_DIR=%SCRIPT_DIR%logs"

echo Activating Python virtual environment...
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    pause
    exit /b 1
)
call "%VENV_PATH%\Scripts\activate.bat"
echo.

if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

echo Starting Rasa Server...
cd "%SCRIPT_DIR%rasa"
start "Rasa Server" cmd /c "rasa run > "%LOGS_DIR%\rasa_server.log" 2>&1"
cd "%SCRIPT_DIR%"
timeout /t 3 /nobreak > nul

echo Starting Rasa Actions Server...
cd "%SCRIPT_DIR%rasa"
start "Rasa Actions" cmd /c "rasa run actions > "%LOGS_DIR%\rasa_actions.log" 2>&1"
cd "%SCRIPT_DIR%"
timeout /t 3 /nobreak > nul

echo Starting Python HTTP Server for UI...
start "HTTP Server" cmd /c "python -m http.server 35109 --directory UI > "%LOGS_DIR%\http_server.log" 2>&1"
timeout /t 2 /nobreak > nul

echo Starting Main Python Assistant (core/main.py)...
echo Press Ctrl+C in this window to stop the assistant.
echo Other services (Rasa, HTTP Server) will need to be closed manually from their windows or Task Manager.
python core/main.py

echo Main assistant script finished.
echo.
echo ======================================================================
echo REMINDER: Rasa Server, Rasa Actions, and HTTP Server may still be running in separate windows or as background processes.
echo Please close them manually or use Task Manager to stop them.
echo Look for processes named 'rasa.exe' or 'python.exe' (for the http server).
echo ======================================================================
pause
endlocal
