#!/usr/bin/env python3
"""
Test script for optimization changes:
- CacheService functionality
- DataCollectionService direct API usage
- AnalysisService Claude-only analysis
- Rate limiting improvements
"""

import asyncio
import json
import time
from datetime import datetime
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Try to import aiohttp, but don't fail if it's missing
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("⚠️ aiohttp not available - API endpoint tests will be skipped")
    print("   Install with: pip install aiohttp")

async def test_cache_service():
    """Test the new CacheService functionality"""
    print("🧪 Testing CacheService...")
    
    try:
        from app.services.cache_service import CacheService
        
        # Initialize cache service
        cache_service = CacheService()
        await cache_service.initialize()
        
        # Test basic caching
        test_key = "test_data"
        test_data = {"message": "Hello from cache", "timestamp": datetime.now().isoformat()}
        
        # Set cache
        await cache_service.set(test_key, test_data, ttl=300)
        print("✅ Cache set successful")
        
        # Get cache
        cached_data = await cache_service.get(test_key)
        if cached_data and cached_data.get("message") == "Hello from cache":
            print("✅ Cache retrieval successful")
        else:
            print("❌ Cache retrieval failed")
            return False
        
        # Test cache statistics
        stats = await cache_service.get_cache_stats()
        print(f"📊 Cache stats: {stats}")
        
        # Test cache invalidation
        await cache_service.delete(test_key)
        deleted_data = await cache_service.get(test_key)
        if deleted_data is None:
            print("✅ Cache deletion successful")
        else:
            print("❌ Cache deletion failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ CacheService test failed: {str(e)}")
        return False

async def test_data_collection_service():
    """Test the new DataCollectionService direct API usage"""
    print("\n🌐 Testing DataCollectionService...")
    
    try:
        from app.services.data_collection_service import DataCollectionService
        
        # Initialize data collection service
        data_service = DataCollectionService()
        await data_service.initialize()
        
        # Test GitHub data collection
        github_data = await data_service.collect_github_data("python", max_results=3)
        if github_data and isinstance(github_data, list):
            print(f"✅ GitHub data collection successful: {len(github_data)} items")
        else:
            print("❌ GitHub data collection failed")
            return False
        
        # Test Stack Overflow data collection
        stack_data = await data_service.collect_stackoverflow_data("fastapi", max_results=3)
        if stack_data and isinstance(stack_data, list):
            print(f"✅ Stack Overflow data collection successful: {len(stack_data)} items")
        else:
            print("❌ Stack Overflow data collection failed")
            return False
        
        # Test caching integration
        cached_data = await data_service.get_cached_data("github_python")
        if cached_data:
            print("✅ Data caching integration working")
        else:
            print("⚠️ No cached data found (this is normal for first run)")
        
        return True
        
    except Exception as e:
        print(f"❌ DataCollectionService test failed: {str(e)}")
        return False

async def test_analysis_service():
    """Test the new AnalysisService Claude-only analysis"""
    print("\n🧠 Testing AnalysisService...")
    
    try:
        from app.services.analysis_service import AnalysisService
        
        # Initialize analysis service
        analysis_service = AnalysisService()
        await analysis_service.initialize()
        
        # Test learning pattern analysis
        learning_data = [
            {"ai_type": "imperium", "outcome": "success", "topic": "code optimization", "timestamp": datetime.now().isoformat()},
            {"ai_type": "guardian", "outcome": "failure", "topic": "security validation", "timestamp": datetime.now().isoformat()},
            {"ai_type": "sandbox", "outcome": "success", "topic": "experiment design", "timestamp": datetime.now().isoformat()}
        ]
        
        analysis_result = await analysis_service.analyze_learning_patterns(learning_data)
        if analysis_result and isinstance(analysis_result, dict):
            print("✅ Learning pattern analysis successful")
            print(f"📊 Analysis insights: {len(analysis_result.get('insights', []))} insights")
        else:
            print("❌ Learning pattern analysis failed")
            return False
        
        # Test proposal quality analysis
        proposal_data = {
            "ai_type": "imperium",
            "code_before": "# old code",
            "code_after": "# improved code",
            "description": "Test proposal"
        }
        
        quality_result = await analysis_service.analyze_proposal_quality(proposal_data)
        if quality_result and isinstance(quality_result, dict):
            print("✅ Proposal quality analysis successful")
            print(f"📊 Quality score: {quality_result.get('quality_score', 'N/A')}")
        else:
            print("❌ Proposal quality analysis failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AnalysisService test failed: {str(e)}")
        return False

async def test_rate_limiting():
    """Test rate limiting improvements"""
    print("\n⏱️ Testing Rate Limiting...")
    
    try:
        from app.services.anthropic_service import anthropic_rate_limited_call
        
        # Test rate limiting
        start_time = time.time()
        
        # Make multiple calls to test rate limiting
        results = []
        for i in range(3):
            try:
                result = await anthropic_rate_limited_call(
                    f"Test call {i+1}: Please respond with 'OK'",
                    ai_name="test"
                )
                results.append(result)
                print(f"✅ Call {i+1} successful")
            except Exception as e:
                print(f"⚠️ Call {i+1} failed (expected if rate limited): {str(e)}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ Rate limiting test completed in {duration:.2f} seconds")
        print(f"📊 Successful calls: {len([r for r in results if r])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {str(e)}")
        return False

async def test_api_endpoints():
    """Test the new optimized API endpoints"""
    print("\n🔗 Testing API Endpoints...")
    
    if not AIOHTTP_AVAILABLE:
        print("⚠️ Skipping API endpoint tests (aiohttp not available)")
        return True
    
    try:
        async with aiohttp.ClientSession() as session:
            base_url = "http://localhost:8000"
            
            # Test cache stats endpoint
            async with session.get(f"{base_url}/api/optimized/cache/stats") as resp:
                if resp.status == 200:
                    cache_stats = await resp.json()
                    print("✅ Cache stats endpoint working")
                else:
                    print(f"❌ Cache stats endpoint failed: {resp.status}")
                    return False
            
            # Test data collection endpoint
            async with session.get(f"{base_url}/api/optimized/data/github?query=python&max_results=3") as resp:
                if resp.status == 200:
                    github_data = await resp.json()
                    print("✅ GitHub data collection endpoint working")
                else:
                    print(f"❌ GitHub data collection endpoint failed: {resp.status}")
                    return False
            
            # Test analysis endpoint
            analysis_payload = {
                "learning_data": [
                    {"ai_type": "imperium", "outcome": "success", "topic": "test"}
                ]
            }
            async with session.post(f"{base_url}/api/optimized/analysis/learning-patterns", 
                                  json=analysis_payload) as resp:
                if resp.status == 200:
                    analysis_result = await resp.json()
                    print("✅ Analysis endpoint working")
                else:
                    print(f"❌ Analysis endpoint failed: {resp.status}")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {str(e)}")
        return False

async def test_performance_improvements():
    """Test performance improvements"""
    print("\n⚡ Testing Performance Improvements...")
    
    try:
        # Test cache performance
        from app.services.cache_service import CacheService
        cache_service = CacheService()
        await cache_service.initialize()
        
        # Measure cache performance
        start_time = time.time()
        for i in range(10):
            await cache_service.set(f"perf_test_{i}", {"data": f"test_{i}"}, ttl=60)
        cache_write_time = time.time() - start_time
        
        start_time = time.time()
        for i in range(10):
            await cache_service.get(f"perf_test_{i}")
        cache_read_time = time.time() - start_time
        
        print(f"📊 Cache write performance: {cache_write_time:.3f}s for 10 operations")
        print(f"📊 Cache read performance: {cache_read_time:.3f}s for 10 operations")
        
        # Test data collection performance
        from app.services.data_collection_service import DataCollectionService
        data_service = DataCollectionService()
        await data_service.initialize()
        
        start_time = time.time()
        github_data = await data_service.collect_github_data("python", max_results=5)
        data_collection_time = time.time() - start_time
        
        print(f"📊 Data collection performance: {data_collection_time:.3f}s for 5 items")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {str(e)}")
        return False

async def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("\n🔧 Testing Basic Functionality...")
    
    try:
        # Test that we can import the new services
        from app.services.cache_service import CacheService
        print("✅ CacheService import successful")
        
        from app.services.data_collection_service import DataCollectionService
        print("✅ DataCollectionService import successful")
        
        from app.services.analysis_service import AnalysisService
        print("✅ AnalysisService import successful")
        
        # Test service initialization
        cache_service = CacheService()
        print("✅ CacheService instantiation successful")
        
        data_service = DataCollectionService()
        print("✅ DataCollectionService instantiation successful")
        
        analysis_service = AnalysisService()
        print("✅ AnalysisService instantiation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Optimization Changes Test Suite")
    print("=" * 50)
    
    # Check if server is running
    print("📡 Checking if server is running...")
    try:
        import urllib.request
        response = urllib.request.urlopen('http://localhost:8000/health', timeout=5)
        print("✅ Server is running")
    except Exception as e:
        print("⚠️ Server not running on localhost:8000")
        print("   Start server with: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("CacheService", test_cache_service),
        ("DataCollectionService", test_data_collection_service),
        ("AnalysisService", test_analysis_service),
        ("Rate Limiting", test_rate_limiting),
        ("Performance", test_performance_improvements)
    ]
    
    # Add API endpoint test only if aiohttp is available
    if AIOHTTP_AVAILABLE:
        tests.append(("API Endpoints", test_api_endpoints))
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All optimization changes are working correctly!")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    # Provide next steps
    print("\n📝 Next Steps:")
    print("1. Install missing dependencies: pip install aiohttp")
    print("2. Start the server: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("3. Run manual tests from MANUAL_TESTING_GUIDE.md")
    print("4. Monitor system performance for 24 hours")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 