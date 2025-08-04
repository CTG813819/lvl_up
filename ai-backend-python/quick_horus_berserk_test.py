#!/usr/bin/env python3
"""
Quick test to verify Project Horus and Berserk router endpoints
Tests the actual router functionality without needing server startup
"""

def test_horus_endpoints():
    """Test Project Horus endpoint definitions"""
    print("🔬 Testing Project Horus Endpoint Definitions...")
    
    try:
        from app.routers.project_horus import router
        
        endpoints = []
        for route in router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = list(route.methods) if route.methods else ['GET']
                endpoints.append(f"{methods[0]} {route.path}")
        
        print(f"✅ Project Horus has {len(endpoints)} endpoints:")
        for endpoint in endpoints:
            print(f"   📍 {endpoint}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing Horus endpoints: {e}")
        return False

def test_berserk_endpoints():
    """Test Project Berserk endpoint definitions"""
    print("\n⚔️ Testing Project Berserk Endpoint Definitions...")
    
    try:
        from app.routers.project_berserk import router
        
        endpoints = []
        for route in router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = list(route.methods) if route.methods else ['GET']
                endpoints.append(f"{methods[0]} {route.path}")
        
        print(f"✅ Project Berserk has {len(endpoints)} endpoints:")
        
        # Show key endpoints
        key_endpoints = [ep for ep in endpoints if any(word in ep.lower() for word in ['status', 'learn', 'chaos', 'deploy'])]
        for endpoint in key_endpoints[:10]:  # Show first 10 key endpoints
            print(f"   📍 {endpoint}")
        
        if len(endpoints) > 10:
            print(f"   📍 ... and {len(endpoints) - 10} more endpoints")
        
        return True
    except Exception as e:
        print(f"❌ Error testing Berserk endpoints: {e}")
        return False

def test_railway_readiness():
    """Test Railway deployment readiness"""
    print("\n🚂 Testing Railway Deployment Readiness...")
    
    try:
        # Test that routers can be imported and used
        from fastapi import FastAPI
        from app.routers.project_horus import router as horus_router
        from app.routers.project_berserk import router as berserk_router
        
        # Create test app
        app = FastAPI(title="Railway Test App")
        
        # Include routers
        app.include_router(horus_router)
        app.include_router(berserk_router)
        
        # Generate OpenAPI schema
        schema = app.openapi()
        
        print("✅ FastAPI app creation: SUCCESS")
        print("✅ Router inclusion: SUCCESS") 
        print("✅ OpenAPI schema generation: SUCCESS")
        print(f"✅ Total API paths: {len(schema.get('paths', {}))}")
        
        return True
    except Exception as e:
        print(f"❌ Railway readiness test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Project Horus & Berserk Verification")
    print("=" * 50)
    
    results = []
    results.append(test_horus_endpoints())
    results.append(test_berserk_endpoints()) 
    results.append(test_railway_readiness())
    
    success_count = sum(results)
    total_tests = len(results)
    
    print(f"\n📊 Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("✅ ALL TESTS PASSED - Ready for Railway deployment!")
    else:
        print("⚠️ Some tests failed - check issues above")
    
    print(f"\n🎯 Project Horus & Berserk Status: {'READY' if success_count >= 2 else 'NEEDS FIXES'}")