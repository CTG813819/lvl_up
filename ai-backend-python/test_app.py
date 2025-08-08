#!/usr/bin/env python3
"""
Minimal test to check if the enhanced router is being included in the FastAPI app
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_inclusion():
    """Test if the enhanced router is included in the app"""
    try:
        # Import the app
        from main_unified import app
        print("✅ App imported successfully")
        
        # Check all routes
        all_routes = [route.path for route in app.routes if hasattr(route, 'path')]
        enhanced_routes = [route for route in all_routes if 'project-horus-enhanced' in route]
        
        print(f"✅ Found {len(enhanced_routes)} enhanced routes:")
        for route in enhanced_routes:
            print(f"   - {route}")
        
        # Check if the status endpoint is available
        status_routes = [route for route in all_routes if 'project-horus-enhanced/status' in route]
        print(f"✅ Status routes found: {len(status_routes)}")
        
        return len(enhanced_routes) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_inclusion()
    sys.exit(0 if success else 1) 