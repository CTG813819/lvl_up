#!/usr/bin/env python3
"""
Startup script that ensures the app module can be found
"""
import sys
import os
import uvicorn

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Also ensure we can find the app module
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set PYTHONPATH environment variable as well
os.environ['PYTHONPATH'] = current_dir

# Now we can import the app - prioritize main_unified.py
try:
    from main_unified import app
    print("✅ Successfully imported app from main_unified.py")
except ImportError:
    try:
        from main import app
        print("✅ Successfully imported app from main.py")
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        print(f"Directory contents: {os.listdir('.')}")
        sys.exit(1)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🌐 Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)