#!/bin/bash
# Start the backend server on all network interfaces

cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.deps_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.deps_installed
fi

# Start the server
echo "Starting backend server on 0.0.0.0:8000..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
