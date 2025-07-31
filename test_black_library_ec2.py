#!/usr/bin/env python3
"""
Test script for Black Library router on EC2
"""

try:
    from app.routers.black_library import router
    print("✅ Black Library router imported successfully")
except Exception as e:
    print(f"❌ Error importing Black Library router: {e}")

try:
    from app.main import app
    print("✅ Main app imported successfully with Black Library router")
except Exception as e:
    print(f"❌ Error importing main app: {e}")

print("🎯 Black Library integration test complete") 