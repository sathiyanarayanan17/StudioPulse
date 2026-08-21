#!/bin/bash
# StudioPulse AI - Setup Script for Linux/Mac

echo "============================================"
echo "  StudioPulse AI - Project Setup"
echo "============================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Please install Python 3.11+ from https://python.org"
    exit 1
fi

echo "[1/4] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[2/4] Installing dependencies..."
pip install -r requirements.txt

echo "[3/4] Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
    echo "Please edit .env with your credentials."
else
    echo ".env already exists, skipping."
fi

echo "[4/4] Verifying installation..."
python -c "import vertexai; import httpx; import structlog; print('All dependencies installed successfully!')"

echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "To run in DEMO MODE (no credentials needed):"
echo "  python -m src.demo"
echo ""
echo "To run in PRODUCTION MODE:"
echo "  1. Edit .env with your Google Cloud and Grafana credentials"
echo "  2. python -m src.main"
echo ""
echo "Dashboard will be available at: http://localhost:8080"
echo "============================================"
