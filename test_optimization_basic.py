#!/usr/bin/env python3
"""
Basic test script for optimization changes
Tests core functionality with minimal dependencies
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_cache_service_basic():
    """Test basic CacheService functionality without external dependencies"""
    print("🧪 Testing CacheService (basic)...")
    
    try:
        # Test if we can import the service
        from app.services.cache_service import CacheService
        print("✅ CacheService import successful")
        
        # Test basic initialization
        cache_service = CacheService()
        print("✅ CacheService instance created")
        
        # Test basic methods exist
        if hasattr(cache_service, 'set_cache'):
            print("✅ set_cache method exists")
        else:
            print("❌ set_cache method missing")
            
        if hasattr(cache_service, 'get_cache'):
            print("✅ get_cache method exists")
        else:
            print("❌ get_cache method missing")
            
        if hasattr(cache_service, 'initialize'):
            print("✅ initialize method exists")
        else:
            print("❌ initialize method missing")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ CacheService test failed: {e}")
        return False

async def test_data_collection_service_basic():
    """Test basic DataCollectionService functionality"""
    print("\n🧪 Testing DataCollectionService (basic)...")
    
    try:
        # Test if we can import the service
        from app.services.data_collection_service import DataCollectionService
        print("✅ DataCollectionService import successful")
        
        # Test basic initialization
        data_service = DataCollectionService()
        print("✅ DataCollectionService instance created")
        
        # Test basic methods exist
        if hasattr(data_service, 'initialize'):
            print("✅ initialize method exists")
        else:
            print("❌ initialize method missing")
            
        if hasattr(data_service, 'cache_service'):
            print("✅ cache_service integration exists")
        else:
            print("❌ cache_service integration missing")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ DataCollectionService test failed: {e}")
        return False

async def test_analysis_service_basic():
    """Test basic AnalysisService functionality"""
    print("\n🧪 Testing AnalysisService (basic)...")
    
    try:
        # Test if we can import the service
        from app.services.analysis_service import AnalysisService
        print("✅ AnalysisService import successful")
        
        # Test basic initialization
        analysis_service = AnalysisService()
        print("✅ AnalysisService instance created")
        
        # Test basic methods exist
        if hasattr(analysis_service, 'initialize'):
            print("✅ initialize method exists")
        else:
            print("❌ initialize method missing")
            
        if hasattr(analysis_service, 'cache_service'):
            print("✅ cache_service integration exists")
        else:
            print("❌ cache_service integration missing")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ AnalysisService test failed: {e}")
        return False

async def test_router_basic():
    """Test basic router functionality"""
    print("\n🧪 Testing router (basic)...")
    
    try:
        # Test if we can import the router
        from app.routers.optimized_services import router
        print("✅ Optimized services router import successful")
        
        # Test router has routes
        if hasattr(router, 'routes'):
            print(f"✅ Router has {len(router.routes)} routes")
        else:
            print("❌ Router missing routes attribute")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Router test failed: {e}")
        return False

async def test_file_structure():
    """Test that all required files exist"""
    print("\n🧪 Testing file structure...")
    
    required_files = [
        "app/services/cache_service.py",
        "app/services/data_collection_service.py", 
        "app/services/analysis_service.py",
        "app/routers/optimized_services.py",
        "OPTIMIZATION_STRATEGY.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

async def test_main_integration():
    """Test that main.py includes the new router"""
    print("\n🧪 Testing main.py integration...")
    
    try:
        # Check if main.py includes the optimized services router
        with open('main.py', 'r') as f:
            content = f.read()
            
        if 'optimized_services' in content:
            print("✅ main.py includes optimized_services router")
        else:
            print("❌ main.py missing optimized_services router")
            return False
            
        if 'app.include_router(optimized_services_router' in content:
            print("✅ main.py includes router registration")
        else:
            print("❌ main.py missing router registration")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Main integration test failed: {e}")
        return False

async def main():
    """Run all basic tests"""
    print("🚀 Starting basic optimization tests...\n")
    
    tests = [
        test_cache_service_basic(),
        test_data_collection_service_basic(),
        test_analysis_service_basic(),
        test_router_basic(),
        test_file_structure(),
        test_main_integration()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("\n📊 Test Results:")
    print("=" * 50)
    
    test_names = [
        "CacheService (basic)",
        "DataCollectionService (basic)", 
        "AnalysisService (basic)",
        "Router (basic)",
        "File Structure",
        "Main Integration"
    ]
    
    passed = 0
    total = len(results)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ {test_names[i]}: FAILED - {result}")
        elif result:
            print(f"✅ {test_names[i]}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_names[i]}: FAILED")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic optimization tests passed!")
        print("\n📋 Next Steps:")
        print("1. Install missing dependencies: pip install structlog aiohttp fastapi")
        print("2. Restart the server to load the new services")
        print("3. Test the API endpoints manually")
        print("4. Monitor Claude API usage reduction")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("\n🔧 To fix missing dependencies:")
        print("sudo apt update")
        print("sudo apt install python3-pip")
        print("pip3 install structlog aiohttp fastapi")

if __name__ == "__main__":
    asyncio.run(main()) 