@echo off
cd /d "%~dp0"

REM Create .env from .env.example if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating .env from .env.example...
    copy .env.example .env >nul
    echo [INFO] Please edit .env and add your API keys.
    echo [INFO] Starting in DEMO MODE.
)

REM Use the virtual environment Python (required for fastapi, chromadb, etc.)
echo [INFO] Starting IP-SAKTI Ayurveda IPR Assistant...
.venv\Scripts\python app.py
pause
