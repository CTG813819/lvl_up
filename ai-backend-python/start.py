#!/usr/bin/env python3
"""
Railway Startup Script - Forces proper port detection
"""
import os
import sys

def main():
    # Force debug output that WILL appear
    port_env = os.environ.get("PORT")
    
    print("=" * 80, flush=True)
    print("🚀 RAILWAY STARTUP SCRIPT EXECUTING", flush=True)
    print(f"📍 PORT env var: '{port_env}'", flush=True)
    print(f"🔌 All env vars with PORT: {[k for k in os.environ.keys() if 'PORT' in k.upper()]}", flush=True)
    print(f"📊 Railway env vars: {[k for k in os.environ.keys() if 'RAILWAY' in k.upper()]}", flush=True)
    print("=" * 80, flush=True)
    
    # Determine the correct port
    if port_env and port_env.isdigit():
        port = int(port_env)
        print(f"✅ Using Railway assigned port: {port}", flush=True)
    else:
        port = 8000
        print(f"⚠️ PORT not set, defaulting to: {port}", flush=True)
    
    # Set PORT environment variable for uvicorn
    os.environ["PORT"] = str(port)
    
    print(f"🚀 Starting uvicorn on port {port}...", flush=True)
    
    # Import and run uvicorn - using ai-backend-python/main_unified.py
    sys.path.insert(0, './ai-backend-python')
    import uvicorn
    uvicorn.run(
        "main_unified:app",
        host="0.0.0.0", 
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()