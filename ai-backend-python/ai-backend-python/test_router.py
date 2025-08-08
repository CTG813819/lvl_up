#!/usr/bin/env python3
"""
Test script to verify the enhanced Project Horus router is working
"""

import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_enhanced_router():
    """Test the enhanced Project Horus router"""
    try:
        # Import the router
        from app.routers.project_horus_enhanced import router
        print("✅ Router imported successfully")
        
        # Check routes
        routes = [route.path for route in router.routes]
        print(f"✅ Found {len(routes)} routes:")
        for route in routes:
            print(f"   - {route}")
        
        # Test the service
        from app.services.project_horus_service import project_horus_service
        print("✅ Project Horus service imported successfully")
        
        # Test a simple method
        status = await project_horus_service.get_project_horus_status()
        print(f"✅ Service status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_router())
    sys.exit(0 if success else 1) 