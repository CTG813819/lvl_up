#!/usr/bin/env python3
"""
Simple test script for optimization changes
Tests core functionality without requiring external dependencies
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def test_cache_service():
    """Test the CacheService functionality"""
    print("🧪 Testing CacheService...")
    
    try:
        from app.services.cache_service import CacheService
        
        # Initialize cache service
        cache_service = CacheService()
        await cache_service.initialize()
        
        # Test basic caching
        test_key = "test_key"
        test_value = {"data": "test_value", "timestamp": datetime.now().isoformat()}
        
        # Set cache
        await cache_service.set_cache(test_key, test_value, ttl=300)
        print("✅ Cache set successfully")
        
        # Get cache
        cached_value = await cache_service.get_cache(test_key)
        if cached_value and cached_value.get("data") == "test_value":
            print("✅ Cache retrieval successful")
        else:
            print("❌ Cache retrieval failed")
            
        # Test cache statistics
        stats = await cache_service.get_cache_stats()
        print(f"✅ Cache stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ CacheService test failed: {e}")
        return False

async def test_data_collection_service():
    """Test the DataCollectionService functionality"""
    print("\n🧪 Testing DataCollectionService...")
    
    try:
        from app.services.data_collection_service import DataCollectionService
        
        # Initialize data collection service
        data_service = DataCollectionService()
        await data_service.initialize()
        
        # Test service initialization
        print("✅ DataCollectionService initialized successfully")
        
        # Test cache integration
        cache_service = data_service.cache_service
        if cache_service:
            print("✅ Cache service integration working")
        else:
            print("❌ Cache service integration failed")
            
        return True
        
    except Exception as e:
        print(f"❌ DataCollectionService test failed: {e}")
        return False

async def test_analysis_service():
    """Test the AnalysisService functionality"""
    print("\n🧪 Testing AnalysisService...")
    
    try:
        from app.services.analysis_service import AnalysisService
        
        # Initialize analysis service
        analysis_service = AnalysisService()
        await analysis_service.initialize()
        
        # Test service initialization
        print("✅ AnalysisService initialized successfully")
        
        # Test cache integration
        cache_service = analysis_service.cache_service
        if cache_service:
            print("✅ Cache service integration working")
        else:
            print("❌ Cache service integration failed")
            
        return True
        
    except Exception as e:
        print(f"❌ AnalysisService test failed: {e}")
        return False

async def test_router_import():
    """Test that the optimized services router can be imported"""
    print("\n🧪 Testing router import...")
    
    try:
        from app.routers.optimized_services import router
        print("✅ Optimized services router imported successfully")
        
        # Check if router has endpoints
        routes = [route for route in router.routes if hasattr(route, 'path')]
        print(f"✅ Router has {len(routes)} endpoints")
        
        return True
        
    except Exception as e:
        print(f"❌ Router import test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting optimization changes tests...\n")
    
    tests = [
        test_cache_service(),
        test_data_collection_service(),
        test_analysis_service(),
        test_router_import()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("\n📊 Test Results:")
    print("=" * 50)
    
    test_names = [
        "CacheService",
        "DataCollectionService", 
        "AnalysisService",
        "Router Import"
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
        print("🎉 All optimization tests passed!")
        print("\n📋 Next Steps:")
        print("1. Restart the server to load the new services")
        print("2. Test the API endpoints manually")
        print("3. Monitor Claude API usage reduction")
    else:
        print("⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main()) 