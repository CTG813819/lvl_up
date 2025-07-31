#!/bin/bash

# HORUS Project Berserk Startup Script
echo "Starting HORUS Project Berserk AI System..."

# Navigate to project directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment
source venv/bin/activate

# Start HORUS on port 8003
echo "Launching HORUS on port 8003..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

echo "HORUS Project Berserk is now running on port 8003"