@echo off
REM StudioPulse AI - Setup Script for Windows
echo ============================================
echo   StudioPulse AI - Project Setup
echo ============================================
echo.

REM Check Python version
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.11+ from https://python.org
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/4] Installing dependencies...
pip install -r requirements.txt

echo [3/4] Setting up configuration...
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example
    echo Please edit .env with your credentials.
) else (
    echo .env already exists, skipping.
)

echo [4/4] Verifying installation...
python -c "import vertexai; import httpx; import structlog; print('All dependencies installed successfully!')"

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo To run in DEMO MODE (no credentials needed):
echo   python -m src.demo
echo.
echo To run in PRODUCTION MODE:
echo   1. Edit .env with your Google Cloud and Grafana credentials
echo   2. python -m src.main
echo.
echo Dashboard will be available at: http://localhost:8080
echo ============================================
