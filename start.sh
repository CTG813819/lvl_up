#!/bin/bash
set -e

echo "Starting AI Backend on port 8000"

# Run the application
exec uvicorn main:app --host 0.0.0.0 --port 8000 