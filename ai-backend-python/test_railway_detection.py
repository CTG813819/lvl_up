#!/usr/bin/env python3
"""
Test Railway environment detection
This script helps verify that Railway environment detection is working correctly
"""

import os
import sys
import asyncio

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.railway_utils import is_railway_environment, should_skip_external_requests, get_environment_info

def test_railway_detection():
    """Test Railway environment detection"""
    print("🔍 TESTING RAILWAY ENVIRONMENT DETECTION")
    print("=" * 50)
    
    # Check current environment
    print(f"📊 Environment Info:")
    env_info = get_environment_info()
    for key, value in env_info.items():
        print(f"   {key}: {value}")
    
    print(f"\n🌍 Environment Variables:")
    railway_vars = [
        "PORT",
        "RAILWAY_ENVIRONMENT_NAME", 
        "RAILWAY_SERVICE_ID",
        "RAILWAY_PROJECT_ID",
        "RAILWAY_DEPLOYMENT_ID",
        "RAILWAY_PUBLIC_DOMAIN"
    ]
    
    for var in railway_vars:
        value = os.getenv(var)
        status = "✅ SET" if value else "❌ NOT SET"
        print(f"   {var}: {status} ({value})")
    
    print(f"\n🔧 Detection Results:")
    print(f"   is_railway_environment(): {is_railway_environment()}")
    print(f"   should_skip_external_requests(): {should_skip_external_requests()}")
    
    # Test with mock Railway environment
    print(f"\n🧪 Testing with mock Railway environment:")
    os.environ["PORT"] = "8000"
    print(f"   Set PORT=8000")
    print(f"   is_railway_environment(): {is_railway_environment()}")
    print(f"   should_skip_external_requests(): {should_skip_external_requests()}")
    
    # Clean up
    if "PORT" in os.environ:
        del os.environ["PORT"]

if __name__ == "__main__":
    test_railway_detection()