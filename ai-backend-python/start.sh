#!/bin/bash
# Simple shell script to handle PORT environment variable properly

# Get PORT from environment or default to 8000
PORT=${PORT:-8000}

# Start uvicorn with the resolved port
exec python -m uvicorn main_unified:app --host 0.0.0.0 --port $PORT