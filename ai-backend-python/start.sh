#!/bin/bash
# Railway startup script using main_unified.py

echo "🚀 Starting Railway AI Backend with main_unified.py..."
echo "📁 Current directory: $(pwd)"
echo "🌍 Environment variables:"
echo "   PORT: ${PORT}"
echo "   PYTHONPATH: ${PYTHONPATH}"

# Set default port if not provided
if [ -z "$PORT" ]; then
    export PORT=8000
    echo "🔧 PORT not set, using default: 8000"
else
    echo "🔧 Using PORT: $PORT"
fi

# Validate port is numeric
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "❌ PORT value '$PORT' is not numeric, using default 8000"
    export PORT=8000
fi

# Check if main_unified.py exists
if [ -f "main_unified.py" ]; then
    echo "✅ Found main_unified.py"
else
    echo "❌ main_unified.py not found!"
    echo "📋 Looking for Python files:"
    find . -name "*.py" -type f | head -20
    exit 1
fi

# Start the server with main_unified.py
echo "🌐 Starting server on port $PORT..."
exec python -m uvicorn main_unified:app --host 0.0.0.0 --port $PORT