#!/usr/bin/env python3
"""
Comprehensive Backend Endpoint Testing Script
Tests all API endpoints and identifies issues
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://34.202.215.209:4000"
TIMEOUT = 30

class BackendTester:
    def __init__(self):
        self.results = []
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TIMEOUT))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, method, endpoint, data=None, expected_status=200):
        """Test a single endpoint"""
        url = f"{BASE_URL}{endpoint}"
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    status = response.status
                    try:
                        content = await response.json()
                    except:
                        content = await response.text()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    status = response.status
                    try:
                        content = await response.json()
                    except:
                        content = await response.text()
            else:
                return {"endpoint": endpoint, "status": "error", "message": f"Unsupported method: {method}"}
            
            success = status == expected_status
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": status,
                "expected_status": expected_status,
                "success": success,
                "content": content if isinstance(content, dict) else str(content)[:200],
                "timestamp": datetime.now().isoformat()
            }
            
            if not success:
                result["error"] = f"Expected {expected_status}, got {status}"
                
        except Exception as e:
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": "ERROR",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        self.results.append(result)
        return result
    
    async def run_all_tests(self):
        """Run comprehensive endpoint tests"""
        print("🚀 Starting comprehensive backend endpoint tests...")
        print(f"📍 Testing server: {BASE_URL}")
        print("=" * 60)
        
        # Core health and status endpoints
        await self.test_endpoint("GET", "/health")
        await self.test_endpoint("GET", "/api/github/status")
        await self.test_endpoint("GET", "/api/agents/status")
        await self.test_endpoint("GET", "/api/learning/status")
        
        # Oath Papers endpoints
        await self.test_endpoint("GET", "/api/oath-papers/")
        await self.test_endpoint("GET", "/api/oath-papers/ai-insights")
        await self.test_endpoint("POST", "/api/oath-papers/learn", {"paper_id": "test"})
        
        # Proposals endpoints
        await self.test_endpoint("GET", "/api/proposals/")
        await self.test_endpoint("GET", "/api/proposals/ai-status")
        
        # Learning endpoints
        await self.test_endpoint("GET", "/api/learning/data")
        await self.test_endpoint("GET", "/api/learning/metrics")
        await self.test_endpoint("GET", "/api/learning/insights/Imperium")
        await self.test_endpoint("GET", "/api/learning/insights/Guardian")
        await self.test_endpoint("GET", "/api/learning/insights/Sandbox")
        await self.test_endpoint("GET", "/api/learning/insights/Conquest")
        
        # Growth endpoints
        await self.test_endpoint("GET", "/api/growth/status")
        await self.test_endpoint("GET", "/api/growth/insights")
        
        # Agent control endpoints
        await self.test_endpoint("POST", "/api/agents/run-all")
        
        # Conquest endpoints (these might be 404)
        await self.test_endpoint("GET", "/api/conquest/status", expected_status=404)
        await self.test_endpoint("POST", "/api/conquest/analyze-suggestion", {"suggestion": "test"}, expected_status=404)
        
        # Notification endpoints (these might be 404)
        await self.test_endpoint("GET", "/api/notifications/", expected_status=404)
        await self.test_endpoint("GET", "/api/notifications/stats", expected_status=404)
        await self.test_endpoint("POST", "/api/notifications/create", {"message": "test"}, expected_status=404)
        
        # WebSocket endpoints (test connection)
        await self.test_websocket("/ws")
        await self.test_websocket("/socket.io/")
        
        print("\n" + "=" * 60)
        print("📊 Test Results Summary:")
        print("=" * 60)
        
        successful = [r for r in self.results if r.get("success", False)]
        failed = [r for r in self.results if not r.get("success", False)]
        
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"📈 Success Rate: {len(successful)/(len(successful)+len(failed))*100:.1f}%")
        
        if failed:
            print("\n❌ Failed Endpoints:")
            for result in failed:
                error_msg = result.get('error', f"Status {result.get('status_code', 'ERROR')}")
                print(f"  • {result['method']} {result['endpoint']} - {error_msg}")
        
        # Save detailed results
        with open("backend_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: backend_test_results.json")
        return self.results
    
    async def test_websocket(self, endpoint):
        """Test WebSocket connection"""
        url = f"ws://34.202.215.209:4000{endpoint}"
        try:
            async with self.session.ws_connect(url) as ws:
                result = {
                    "endpoint": f"WS {endpoint}",
                    "method": "WEBSOCKET",
                    "status_code": "CONNECTED",
                    "success": True,
                    "content": "WebSocket connection successful",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            result = {
                "endpoint": f"WS {endpoint}",
                "method": "WEBSOCKET",
                "status_code": "ERROR",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        self.results.append(result)
        return result

async def main():
    async with BackendTester() as tester:
        results = await tester.run_all_tests()
        
        # Provide actionable recommendations
        print("\n🔧 Actionable Recommendations:")
        print("=" * 60)
        
        failed_endpoints = [r for r in results if not r.get("success", False)]
        
        if any("oath_papers" in r["endpoint"] for r in failed_endpoints):
            print("• Oath Papers issues detected - database table may be missing")
            
        if any("proposals" in r["endpoint"] for r in failed_endpoints):
            print("• Proposals validation errors - missing required fields (improvement_type, confidence)")
            
        if any("notifications" in r["endpoint"] for r in failed_endpoints):
            print("• Notification endpoints missing - router not registered")
            
        if any("conquest" in r["endpoint"] for r in failed_endpoints):
            print("• Conquest endpoints missing - router not registered")
            
        if any("WEBSOCKET" in r["method"] for r in failed_endpoints):
            print("• WebSocket connections failing - CORS or authentication issues")
        
        print("\n🎯 Next Steps:")
        print("1. Check backend logs for specific error messages")
        print("2. Verify all routers are properly registered in main.py")
        print("3. Run database migration scripts if tables are missing")
        print("4. Check WebSocket configuration and CORS settings")

if __name__ == "__main__":
    asyncio.run(main()) 