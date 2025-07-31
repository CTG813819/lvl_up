#!/usr/bin/env python3
"""
Comprehensive EC2 Backend Test Script
Tests all endpoints, WebSocket connections, and services
"""

import asyncio
import aiohttp
import websockets
import json
import sys
import time
from datetime import datetime

class EC2BackendTester:
    def __init__(self):
        self.base_url_8000 = "http://34.202.215.209:8000"
        self.base_url_4000 = "http://34.202.215.209:4000"
        self.dashboard_url = "http://34.202.215.209:8501"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }

    async def test_http_endpoints(self):
        """Test all HTTP endpoints"""
        print("\n🌐 Testing HTTP Endpoints...")
        
        endpoints_8000 = [
            "/api/imperium/persistence/learning-analytics",
            "/api/health",
            "/api/imperium/growth",
            "/api/imperium/proposals",
            "/api/imperium/monitoring",
            "/api/imperium/issues",
            "/api/proposals/ai-status",
            "/api/learning/data",
            "/api/oath-papers/ai-insights",
            "/api/oath-papers/learn",
            "/api/oath-papers/categories",
        ]
        
        endpoints_4000 = [
            "/api/imperium/persistence/learning-analytics",
            "/api/health",
            "/api/imperium/growth",
            "/api/imperium/proposals",
            "/api/imperium/monitoring",
            "/api/imperium/issues",
            "/api/proposals/ai-status",
            "/api/learning/data",
            "/api/oath-papers/ai-insights",
            "/api/oath-papers/learn",
            "/api/oath-papers/categories",
        ]
        
        async with aiohttp.ClientSession() as session:
            # Test port 8000 endpoints
            print(f"\n📡 Testing Port 8000 Endpoints:")
            for endpoint in endpoints_8000:
                url = f"{self.base_url_8000}{endpoint}"
                await self._test_endpoint(session, url, f"8000_{endpoint.replace('/', '_')}")
            
            # Test port 4000 endpoints
            print(f"\n📡 Testing Port 4000 Endpoints:")
            for endpoint in endpoints_4000:
                url = f"{self.base_url_4000}{endpoint}"
                await self._test_endpoint(session, url, f"4000_{endpoint.replace('/', '_')}")

    async def _test_endpoint(self, session, url, test_name):
        """Test a single HTTP endpoint"""
        try:
            async with session.get(url, timeout=10) as response:
                status = response.status
                content_type = response.headers.get('content-type', 'unknown')
                
                if status == 200:
                    try:
                        data = await response.text()
                        json_data = await response.json()
                        print(f"✅ {url} - Status: {status}, Type: {content_type}, Data: {len(data)} chars")
                        
                        # Special check for growth endpoint
                        if "growth" in url:
                            await self._analyze_growth_data(json_data, test_name)
                            
                    except Exception as e:
                        print(f"⚠️ {url} - Status: {status}, Type: {content_type}, JSON Error: {e}")
                else:
                    print(f"❌ {url} - Status: {status}, Type: {content_type}")
                
                self.results["tests"][test_name] = {
                    "url": url,
                    "status": status,
                    "content_type": content_type,
                    "success": status == 200
                }
                
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
            self.results["tests"][test_name] = {
                "url": url,
                "error": str(e),
                "success": False
            }

    async def _analyze_growth_data(self, data, test_name):
        """Analyze growth data structure"""
        print(f"🔍 Analyzing growth data for {test_name}:")
        
        if isinstance(data, dict):
            print(f"   📊 Data is a dictionary with keys: {list(data.keys())}")
            if 'data' in data and isinstance(data['data'], list):
                print(f"   📈 Found 'data' array with {len(data['data'])} items")
                if data['data']:
                    first_item = data['data'][0]
                    print(f"   📋 First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                    if isinstance(first_item, dict) and 'start_time' not in first_item:
                        print(f"   ⚠️ WARNING: Missing 'start_time' field in growth data!")
            else:
                print(f"   ⚠️ No 'data' array found in response")
        elif isinstance(data, list):
            print(f"   📈 Data is a list with {len(data)} items")
            if data:
                first_item = data[0]
                print(f"   📋 First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                if isinstance(first_item, dict) and 'start_time' not in first_item:
                    print(f"   ⚠️ WARNING: Missing 'start_time' field in growth data!")
        else:
            print(f"   ❓ Unexpected data type: {type(data)}")

    async def test_websocket_endpoints(self):
        """Test WebSocket endpoints"""
        print("\n🔌 Testing WebSocket Endpoints...")
        
        ws_endpoints = [
            "ws://34.202.215.209:8000/ws",
            "ws://34.202.215.209:8000/ws/imperium/learning-analytics",
            "ws://34.202.215.209:8000/api/notifications/ws",
            "ws://34.202.215.209:4000/ws",
            "ws://34.202.215.209:4000/api/notifications/ws",
        ]
        
        for url in ws_endpoints:
            await self._test_websocket(url)

    async def _test_websocket(self, url):
        """Test a single WebSocket endpoint"""
        test_name = f"ws_{url.replace('://', '_').replace('/', '_').replace(':', '_')}"
        
        try:
            async with websockets.connect(url, timeout=10) as websocket:
                print(f"✅ {url} - Connected successfully")
                
                # Send test message
                test_message = {
                    "type": "connection",
                    "client": "ec2_test_script",
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(test_message))
                print(f"📤 Sent test message to {url}")
                
                # Try to receive response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    print(f"📨 Received response from {url}: {response[:100]}...")
                except asyncio.TimeoutError:
                    print(f"⏰ No response received from {url} within 5 seconds")
                
                await websocket.close()
                self.results["tests"][test_name] = {
                    "url": url,
                    "success": True,
                    "connected": True
                }
                
        except websockets.exceptions.InvalidURI as e:
            print(f"❌ {url} - Invalid URI: {e}")
            self.results["tests"][test_name] = {
                "url": url,
                "error": f"Invalid URI: {e}",
                "success": False
            }
        except websockets.exceptions.ConnectionClosed as e:
            print(f"❌ {url} - Connection closed: {e}")
            self.results["tests"][test_name] = {
                "url": url,
                "error": f"Connection closed: {e}",
                "success": False
            }
        except websockets.exceptions.InvalidStatusCode as e:
            print(f"❌ {url} - Invalid status code: {e}")
            self.results["tests"][test_name] = {
                "url": url,
                "error": f"Invalid status code: {e}",
                "success": False
            }
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
            self.results["tests"][test_name] = {
                "url": url,
                "error": str(e),
                "success": False
            }

    async def test_dashboard(self):
        """Test Streamlit dashboard"""
        print("\n📊 Testing Streamlit Dashboard...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.dashboard_url, timeout=10) as response:
                    if response.status == 200:
                        print(f"✅ Dashboard accessible at {self.dashboard_url}")
                        self.results["tests"]["dashboard"] = {
                            "url": self.dashboard_url,
                            "status": response.status,
                            "success": True
                        }
                    else:
                        print(f"❌ Dashboard returned status {response.status}")
                        self.results["tests"]["dashboard"] = {
                            "url": self.dashboard_url,
                            "status": response.status,
                            "success": False
                        }
        except Exception as e:
            print(f"❌ Dashboard error: {e}")
            self.results["tests"]["dashboard"] = {
                "url": self.dashboard_url,
                "error": str(e),
                "success": False
            }

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results["tests"])
        successful_tests = sum(1 for test in self.results["tests"].values() if test.get("success", False))
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        print(f"\n📋 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {total_tests - successful_tests}")
        print(f"   Success Rate: {self.results['summary']['success_rate']:.1f}%")

    def save_results(self):
        """Save test results to file"""
        filename = f"ec2_backend_test_results_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")

    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive EC2 Backend Test...")
        print(f"⏰ Test started at: {datetime.now().isoformat()}")
        
        await self.test_http_endpoints()
        await self.test_websocket_endpoints()
        await self.test_dashboard()
        
        self.generate_summary()
        self.save_results()
        
        print(f"\n✅ Test completed at: {datetime.now().isoformat()}")

async def main():
    tester = EC2BackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 