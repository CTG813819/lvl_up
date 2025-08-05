#!/bin/bash
# Updated AI Backend Startup Script - New Frequencies
echo "Starting LVL UP AI Backend with Updated Frequencies..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/app"
export AI_BACKEND_ENV="production"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Start the updated backend
echo "Starting updated AI backend..."
python main_updated.py

echo "Updated AI backend started successfully!"
echo "New Schedule:"
echo "  * Imperium: Every 1.5 hours (starts immediately)"
echo "  * Sandbox: Every 2 hours (starts 30min after Imperium)"
echo "  * Guardian: Every 5 hours (starts 1hr after Imperium)"
echo "  * Custodes: Every 1.5 hours (starts 1.5hr after Imperium, tests others)"
