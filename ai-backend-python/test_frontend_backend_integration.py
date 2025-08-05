#!/usr/bin/env python3
"""
Test Frontend-Backend Integration
================================

This script tests the integration between frontend and backend endpoints
to ensure the Custody Protocol data is flowing correctly.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class FrontendBackendIntegrationTest:
    """Test frontend-backend integration"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {},
            "summary": {}
        }
    
    async def test_custody_endpoint(self):
        """Test custody endpoint that frontend uses"""
        print("🔍 Testing custody endpoint...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test the main custody endpoint
                async with session.get(f"{self.base_url}/api/custody/", timeout=10) as response:
                    if response.status_code == 200:
                        data = await response.json()
                        
                        # Check if data structure matches frontend expectations
                        has_analytics = 'analytics' in data
                        has_ai_metrics = 'analytics' in data and 'ai_specific_metrics' in data['analytics']
                        has_recommendations = 'analytics' in data and 'recommendations' in data['analytics']
                        
                        self.test_results["tests"]["custody_endpoint"] = {
                            "status": "passed",
                            "status_code": response.status_code,
                            "has_analytics": has_analytics,
                            "has_ai_metrics": has_ai_metrics,
                            "has_recommendations": has_recommendations,
                            "data_structure": "correct" if has_analytics and has_ai_metrics else "incorrect"
                        }
                        
                        print(f"✅ Custody endpoint working - Status: {response.status_code}")
                        print(f"   Analytics present: {has_analytics}")
                        print(f"   AI metrics present: {has_ai_metrics}")
                        print(f"   Recommendations present: {has_recommendations}")
                        
                        # Show sample data structure
                        if has_ai_metrics:
                            ai_types = list(data['analytics']['ai_specific_metrics'].keys())
                            print(f"   AI types found: {ai_types}")
                            
                            for ai_type in ai_types:
                                ai_data = data['analytics']['ai_specific_metrics'][ai_type]
                                level = ai_data.get('custody_level', 1)
                                xp = ai_data.get('custody_xp', 0)
                                print(f"     {ai_type}: Level {level}, XP {xp}")
                        
                    else:
                        self.test_results["tests"]["custody_endpoint"] = {
                            "status": "failed",
                            "status_code": response.status_code,
                            "error": f"HTTP {response.status_code}"
                        }
                        print(f"❌ Custody endpoint failed - Status: {response.status_code}")
                        
        except Exception as e:
            self.test_results["tests"]["custody_endpoint"] = {
                "status": "error",
                "error": str(e)
            }
            print(f"❌ Custody endpoint error: {str(e)}")
    
    async def test_ai_agent_endpoints(self):
        """Test AI agent endpoints"""
        print("🔍 Testing AI agent endpoints...")
        
        ai_agents = ["imperium", "guardian", "sandbox", "conquest"]
        
        for agent in ai_agents:
            try:
                async with aiohttp.ClientSession() as session:
                    # Test agent status endpoint
                    async with session.get(f"{self.base_url}/api/{agent}/status", timeout=10) as response:
                        if response.status_code == 200:
                            data = await response.json()
                            self.test_results["tests"][f"{agent}_status"] = {
                                "status": "passed",
                                "status_code": response.status_code,
                                "data_keys": list(data.keys()) if isinstance(data, dict) else []
                            }
                            print(f"✅ {agent} status endpoint working")
                        else:
                            self.test_results["tests"][f"{agent}_status"] = {
                                "status": "failed",
                                "status_code": response.status_code
                            }
                            print(f"❌ {agent} status endpoint failed - {response.status_code}")
                            
            except Exception as e:
                self.test_results["tests"][f"{agent}_status"] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"❌ {agent} status endpoint error: {str(e)}")
    
    async def test_proposal_endpoints(self):
        """Test proposal endpoints"""
        print("🔍 Testing proposal endpoints...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test proposal listing endpoint
                async with session.get(f"{self.base_url}/api/proposals/", timeout=10) as response:
                    if response.status_code == 200:
                        data = await response.json()
                        proposal_count = len(data) if isinstance(data, list) else 0
                        
                        self.test_results["tests"]["proposals_endpoint"] = {
                            "status": "passed",
                            "status_code": response.status_code,
                            "proposal_count": proposal_count
                        }
                        print(f"✅ Proposals endpoint working - {proposal_count} proposals")
                    else:
                        self.test_results["tests"]["proposals_endpoint"] = {
                            "status": "failed",
                            "status_code": response.status_code
                        }
                        print(f"❌ Proposals endpoint failed - {response.status_code}")
                        
        except Exception as e:
            self.test_results["tests"]["proposals_endpoint"] = {
                "status": "error",
                "error": str(e)
            }
            print(f"❌ Proposals endpoint error: {str(e)}")
    
    async def test_health_endpoints(self):
        """Test health endpoints"""
        print("🔍 Testing health endpoints...")
        
        health_endpoints = ["/health", "/api/health"]
        
        for endpoint in health_endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status_code == 200:
                            self.test_results["tests"][f"health{endpoint}"] = {
                                "status": "passed",
                                "status_code": response.status_code
                            }
                            print(f"✅ Health endpoint {endpoint} working")
                        else:
                            self.test_results["tests"][f"health{endpoint}"] = {
                                "status": "failed",
                                "status_code": response.status_code
                            }
                            print(f"❌ Health endpoint {endpoint} failed - {response.status_code}")
                            
            except Exception as e:
                self.test_results["tests"][f"health{endpoint}"] = {
                    "status": "error",
                    "error": str(e)
                }
                print(f"❌ Health endpoint {endpoint} error: {str(e)}")
    
    async def generate_summary(self):
        """Generate test summary"""
        tests = self.test_results["tests"]
        
        total_tests = len(tests)
        passed_tests = sum(1 for test in tests.values() if test.get("status") == "passed")
        failed_tests = sum(1 for test in tests.values() if test.get("status") == "failed")
        error_tests = sum(1 for test in tests.values() if test.get("status") == "error")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": round(success_rate, 2)
        }
        
        print("\n" + "=" * 60)
        print("🎯 FRONTEND-BACKEND INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"📊 Success Rate: {success_rate}%")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🚨 Errors: {error_tests}")
        print(f"📋 Total: {total_tests}")
        
        # Show specific results
        print("\n📋 DETAILED RESULTS:")
        for test_name, result in tests.items():
            status_icon = "✅" if result.get("status") == "passed" else "❌"
            print(f"  {status_icon} {test_name}: {result.get('status', 'unknown')}")
        
        print("=" * 60)
        
        # Save report
        with open("/home/ubuntu/ai-backend-python/frontend_backend_integration_test.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print("📁 Report saved: /home/ubuntu/ai-backend-python/frontend_backend_integration_test.json")
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Frontend-Backend Integration Tests")
        print("=" * 60)
        
        await self.test_custody_endpoint()
        await self.test_ai_agent_endpoints()
        await self.test_proposal_endpoints()
        await self.test_health_endpoints()
        await self.generate_summary()
        
        print("✅ Frontend-Backend Integration Tests Completed")

async def main():
    """Main function"""
    try:
        tester = FrontendBackendIntegrationTest()
        await tester.run_all_tests()
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 