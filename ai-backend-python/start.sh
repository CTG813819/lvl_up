#!/bin/bash
# Railway startup script using main_unified.py

echo "🚀 Starting Railway AI Backend with main_unified.py..."
echo "📁 Current directory: $(pwd)"
echo "📂 Files in directory:"
ls -la *.py | head -20

# Check if main_unified.py exists
if [ -f "main_unified.py" ]; then
    echo "✅ Found main_unified.py"
else
    echo "❌ main_unified.py not found!"
    echo "📋 Looking for Python files:"
    find . -name "*.py" -type f | head -20
fi

# Start the server with main_unified.py
echo "🌐 Starting server on port ${PORT:-8000}..."
python -m uvicorn main_unified:app --host 0.0.0.0 --port ${PORT:-8000}