#!/usr/bin/env bash
set -e

echo "Starting Lyftr Scraper..."

# Check python
if ! command -v python3 &> /dev/null; then
  echo "python3 not found"
  exit 1
fi

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv || {
    echo "Failed to create venv. Install python3-venv and retry."
    exit 1
  }
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
