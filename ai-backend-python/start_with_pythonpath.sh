#!/bin/bash
# Startup script that ensures correct Python module path

echo "🚀 Starting AI Backend with correct PYTHONPATH..."
echo "📁 Current directory: $(pwd)"

# Export PYTHONPATH to include current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
echo "🔧 PYTHONPATH set to: $PYTHONPATH"

# Check which main file to use
if [ -f "main.py" ]; then
    echo "✅ Using main.py"
    MAIN_FILE="main"
elif [ -f "main_unified.py" ]; then
    echo "✅ Using main_unified.py"
    MAIN_FILE="main_unified"
else
    echo "❌ No main file found!"
    exit 1
fi

# Start the server
echo "🌐 Starting server on port ${PORT:-8000}..."
python -m uvicorn ${MAIN_FILE}:app --host 0.0.0.0 --port ${PORT:-8000}