#!/bin/bash
# Final AI Backend Startup Script - New Schedule
echo "Starting LVL UP AI Backend with Final Schedule..."

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

# Start the final backend
echo "Starting final AI backend..."
python main_final.py

echo "Final AI backend started successfully!"
echo "Final Schedule:"
echo "  * Imperium: Every 1 hour (starts immediately)"
echo "  * Custodes: Tests after Imperium completes"
echo "  * Guardian: 30-40 minutes after Custodes"
echo "  * Custodes: Tests after Guardian"
echo "  * Sandbox: Every 2 hours"
echo "  * Custodes: Tests after Sandbox"
