#!/usr/bin/env python3
"""
Startup script that ensures the app module can be found
"""
import sys
import os
import uvicorn

print("🚀 AI Backend startup script starting...")
print(f"📁 Current directory: {os.getcwd()}")
print(f"📂 Files in current directory:")
try:
    files = [f for f in os.listdir('.') if f.endswith('.py')][:10]
    for f in files:
        print(f"   - {f}")
except Exception as e:
    print(f"   Error listing files: {e}")

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Also ensure we can find the app module
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set PYTHONPATH environment variable as well
os.environ['PYTHONPATH'] = current_dir

print(f"🐍 Python path updated: {current_dir}")
print(f"🌍 Environment PYTHONPATH: {os.environ.get('PYTHONPATH')}")

# Import the app from main_unified.py only
try:
    from main_unified import app
    print("✅ Successfully imported app from main_unified.py")
except ImportError as e:
    print(f"❌ Failed to import app from main_unified.py: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Directory contents: {os.listdir('.')}")
    sys.exit(1)

if __name__ == "__main__":
    # Get PORT from environment with validation
    port_env = os.environ.get("PORT", "8000")
    try:
        port = int(port_env)
        if not (1 <= port <= 65535):
            print(f"⚠️ PORT {port} out of range, using default 8000")
            port = 8000
    except (ValueError, TypeError):
        print(f"⚠️ Invalid PORT '{port_env}', using default 8000")
        port = 8000
    
    print(f"🌐 Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)