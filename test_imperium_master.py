#!/usr/bin/env python3
"""
Test script for Imperium Master Orchestrator
Tests all major functionality including persistence and analytics
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta

# Configuration
<<<<<<< HEAD
BASE_URL = "http://localhost:8000"
=======
BASE_URL = "http://ec2-34-202-215-209.compute-1.amazonaws.com:4001"
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
API_BASE = f"{BASE_URL}/api/imperium"

class ImperiumMasterTester:
    """Test suite for Imperium Master Orchestrator"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
<<<<<<< HEAD
            await self.  # Removed - async generators should use async context
=======
            await self.session.close()
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
    
    async def test_endpoint(self, method, endpoint, data=None, expected_status=200):
        """Test an API endpoint"""
        url = f"{API_BASE}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    status = response.status
                    result = await response.json() if response.status == 200 else await response.text()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    status = response.status
                    result = await response.json() if response.status == 200 else await response.text()
            elif method.upper() == "DELETE":
                async with self.session.delete(url, json={"source": "example.com"}) as response:
                    status = response.status
                    result = await response.json() if response.status == 200 else await response.text()
            
            success = status == expected_status
            self.test_results.append({
                "endpoint": endpoint,
                "method": method,
                "status": status,
                "expected": expected_status,
                "success": success,
                "result": result
            })
            
            print(f"{'✅' if success else '❌'} {method} {endpoint} - Status: {status}")
            if not success:
                print(f"   Expected: {expected_status}, Got: {status}")
                print(f"   Response: {result}")
            
            return success, result
            
        except Exception as e:
            print(f"❌ {method} {endpoint} - Exception: {str(e)}")
            self.test_results.append({
                "endpoint": endpoint,
                "method": method,
                "status": "ERROR",
                "expected": expected_status,
                "success": False,
                "result": str(e)
            })
            return False, str(e)
    
    async def test_core_orchestration(self):
        """Test core orchestration endpoints"""
        print("\n🎯 Testing Core Orchestration")
        print("=" * 50)
        
        # Test system status
        await self.test_endpoint("GET", "/status")
        
        # Test agent registration
        await self.test_endpoint("POST", "/agents/register", {
            "agent_id": "test_agent",
            "agent_type": "TestAI",
            "priority": "high"
        })
        
        # Test getting all agents
        await self.test_endpoint("GET", "/agents")
        
        # Test getting specific agent
        await self.test_endpoint("GET", "/agents/test_agent")
        
        # Test learning cycles
        await self.test_endpoint("GET", "/cycles")
        
        # Test dashboard
        await self.test_endpoint("GET", "/dashboard")
    
    async def test_persistence_endpoints(self):
        """Test persistence endpoints"""
        print("\n🗄️ Testing Persistence Endpoints")
        print("=" * 50)
        
        # Test getting persisted agent metrics
        await self.test_endpoint("GET", "/persistence/agent-metrics")
        
        # Test persisting agent metrics
        await self.test_endpoint("POST", "/persistence/agent-metrics", "test_agent")
        
        # Test getting persisted learning cycles
        await self.test_endpoint("GET", "/persistence/learning-cycles")
        
        # Test learning analytics
        await self.test_endpoint("GET", "/persistence/learning-analytics")
        
        # Test with filters
        await self.test_endpoint("GET", "/persistence/learning-analytics?agent_id=test_agent")
    
    async def test_event_logging(self):
        """Test event logging functionality"""
        print("\n📝 Testing Event Logging")
        print("=" * 50)
        
        # Test logging a learning event
        await self.test_endpoint("POST", "/persistence/log-learning-event", {
            "event_type": "test_learning",
            "agent_id": "test_agent",
            "agent_type": "TestAI",
            "topic": "test topic",
            "results_count": 3,
            "impact_score": 0.7
        })
        
        # Test logging with more data
        await self.test_endpoint("POST", "/persistence/log-learning-event", {
            "event_type": "internet_learning",
            "agent_id": "test_agent",
            "agent_type": "TestAI",
            "topic": "AI orchestration",
            "results_count": 5,
            "results_sample": ["result1", "result2"],
            "insights": ["insight1", "insight2"],
            "processing_time": 2.5,
            "impact_score": 0.8,
            "event_data": {"source": "test", "timestamp": datetime.now().isoformat()}
        })
    
    async def test_internet_learning(self):
        """Test internet learning functionality"""
        print("\n🌐 Testing Internet Learning")
        print("=" * 50)
        
        # Test getting internet learning log
        await self.test_endpoint("GET", "/internet-learning/log")
        
        # Test getting internet learning impact
        await self.test_endpoint("GET", "/internet-learning/impact")
        
        # Test getting learning interval
        await self.test_endpoint("GET", "/internet-learning/interval")
        
        # Test setting learning interval
        await self.test_endpoint("POST", "/internet-learning/interval", {
            "interval": 900  # 15 minutes
        })
        
        # Test getting learning topics
        await self.test_endpoint("GET", "/internet-learning/topics")
        
        # Test setting learning topics
        await self.test_endpoint("POST", "/internet-learning/topics", {
            "topics": {
                "test_agent": ["test topic 1", "test topic 2"]
            }
        })
    
    async def test_trusted_sources(self):
        """Test trusted sources functionality"""
        print("\n🔒 Testing Trusted Sources")
        print("=" * 50)
        
        # Test getting trusted sources
        await self.test_endpoint("GET", "/trusted-sources")
        
<<<<<<< HEAD
                  # Test adding trusted source
          await self.test_endpoint("POST", "/trusted-sources", {
              "url": "https://example.com"
          })
          
          # Test removing trusted source
          await self.test_endpoint("DELETE", "/trusted-sources", {
              "url": "https://example.com"
          })
=======
        # Test adding trusted source
        await self.test_endpoint("POST", "/trusted-sources", {
            "url": "https://example.com"
        })
        
        # Test removing trusted source
        await self.test_endpoint("DELETE", "/trusted-sources", {
            "url": "https://example.com"
        })
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
    
    async def test_internet_learning_result_persistence(self):
        """Test internet learning result persistence"""
        print("\n💾 Testing Internet Learning Result Persistence")
        print("=" * 50)
        
        # Test persisting internet learning result
        await self.test_endpoint("POST", "/persistence/internet-learning-result", {
            "agent_id": "test_agent",
            "topic": "AI orchestration",
            "source": "stackoverflow",
            "result": {
                "title": "Test Learning Result",
                "url": "https://example.com/test",
                "summary": "This is a test learning result",
                "content": "Detailed content here",
                "score": 10,
                "stars": 5
            }
        })
    
    async def test_agent_management(self):
        """Test agent management functionality"""
        print("\n🤖 Testing Agent Management")
        print("=" * 50)
        
        # Test pausing agent
        await self.test_endpoint("POST", "/agents/test_agent/pause")
        
        # Test resuming agent
        await self.test_endpoint("POST", "/agents/test_agent/resume")
        
        # Test adding agent topic
        await self.test_endpoint("POST", "/agents/test_agent/topics", {
            "topic": "new test topic"
        })
    
    async def test_cleanup(self):
        """Test cleanup operations"""
        print("\n🧹 Testing Cleanup")
        print("=" * 50)
        
        # Test unregistering agent
        await self.test_endpoint("DELETE", "/agents/test_agent")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Imperium Master Orchestrator Tests")
        print(f"Base URL: {BASE_URL}")
        print(f"API Base: {API_BASE}")
        
        start_time = time.time()
        
        # Run all test suites
        await self.test_core_orchestration()
        await self.test_persistence_endpoints()
        await self.test_event_logging()
        await self.test_internet_learning()
        await self.test_trusted_sources()
        await self.test_internet_learning_result_persistence()
        await self.test_agent_management()
        await self.test_cleanup()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        self.print_summary(duration)
    
    def print_summary(self, duration):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['method']} {result['endpoint']}")
                    print(f"    Status: {result['status']}, Expected: {result['expected']}")
        
        print("\n✅ Successful Tests:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['method']} {result['endpoint']}")
        
        # Save detailed results
        with open("imperium_test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "duration": duration,
                "summary": {
                    "total": total_tests,
                    "successful": successful_tests,
                    "failed": failed_tests,
                    "success_rate": (successful_tests/total_tests)*100
                },
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: imperium_test_results.json")


async def main():
    """Main function"""
    print("Imperium Master Orchestrator Test Suite")
    print("=" * 50)
    
    # Check if service is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/docs") as response:
                if response.status != 200:
                    print(f"❌ Service not accessible at {BASE_URL}")
                    print("Please ensure the Imperium service is running:")
                    print("  uvicorn app.main:app --reload")
                    return
    except Exception as e:
        print(f"❌ Cannot connect to service at {BASE_URL}")
        print(f"Error: {str(e)}")
        print("Please ensure the Imperium service is running:")
        print("  uvicorn app.main:app --reload")
        return
    
    print("✅ Service is accessible")
    
    # Run tests
    async with ImperiumMasterTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 