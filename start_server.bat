@echo off
cd /d "%~dp0"

REM Create .env from .env.example if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating .env from .env.example...
    copy .env.example .env >nul
    echo [INFO] Please edit .env and add your API keys.
    echo [INFO] Starting in DEMO MODE.
)

echo [INFO] Starting IP-SAKTI Ayurveda IPR Assistant...
python app.py
pause
