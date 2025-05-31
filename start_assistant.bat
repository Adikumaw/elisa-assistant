@echo off
setlocal ENABLEDELAYEDEXPANSION

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%venv"
set "LOGS_DIR=%SCRIPT_DIR%logs"

rem Check for venv and activate
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo ERROR: Windows virtual environment not found at %VENV_DIR%\Scripts\activate.bat
    echo Please run: python -m venv venv
    pause
    exit /b 1
)
echo Activating Python virtual environment (Windows)...
call "%VENV_DIR%\Scripts\activate.bat"

rem Verify commands (optional)
echo Verifying commands in venv...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found in PATH after venv activation.
    pause
    exit /b 1
)
where rasa >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Rasa not found in PATH after venv activation.
    pause
    exit /b 1
)
echo Venv activated.

if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

echo Starting Rasa Server (Windows)...
cd "%SCRIPT_DIR%rasa"
rem Start in a new window that will stay open if rasa run keeps running
start "Rasa Server" cmd /c "rasa run > "%LOGS_DIR%\rasa_server.log" 2>&1"
cd "%SCRIPT_DIR%"
timeout /t 5 /nobreak > nul

echo Starting Rasa Actions Server (Windows)...
cd "%SCRIPT_DIR%rasa"
start "Rasa Actions" cmd /c "rasa run actions > "%LOGS_DIR%\rasa_actions.log" 2>&1"
cd "%SCRIPT_DIR%"
timeout /t 5 /nobreak > nul

echo Starting Python HTTP Server for UI (Windows)...
rem This python should be from the venv
start "UI HTTP Server" cmd /c "python -m http.server 35109 --directory UI > "%LOGS_DIR%\http_server.log" 2>&1"
timeout /t 2 /nobreak > nul

echo Starting Main Python Assistant (core/main.py)...
echo Press Ctrl+C in this window to stop the main assistant.
echo Other services (Rasa, HTTP Server) may need to be closed manually from their windows or Task Manager.
python core/main.py

echo Main assistant script finished.
echo.
echo ======================================================================
echo REMINDER: Rasa Server, Rasa Actions, and HTTP Server may still be running.
echo Please close them manually.
echo ======================================================================

rem Deactivate (optional as cmd session ends)
rem if exist "%VENV_DIR%\Scripts\deactivate.bat" (
rem     call "%VENV_DIR%\Scripts\deactivate.bat"
rem )
pause
endlocal