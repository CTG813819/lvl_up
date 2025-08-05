#!/usr/bin/env python3
"""
Test script to verify unified main import works
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_unified_import():
    """Test importing the unified main"""
    print("🧪 Testing unified main import...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path[0]}")
    
    try:
        # Test importing the unified app
        from main_unified import app
        print("✅ Successfully imported unified app")
        
        # Test that app has the expected attributes
        if hasattr(app, 'routes'):
            print("✅ App has routes attribute")
        else:
            print("⚠️ App missing routes attribute")
            
        # Test that app can be called
        print("✅ App import test passed")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import unified app: {e}")
        print("📋 Available files in current directory:")
        for file in os.listdir("."):
            if file.endswith(".py"):
                print(f"  - {file}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_unified_import()
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Tests failed!")
        sys.exit(1) 