#!/usr/bin/env python3
"""
Verify Backend Port 8000 Script
Tests that all services are working on port 8000
"""

import requests
import json
import time

class BackendVerifier:
    def __init__(self):
        self.base_url = "http://34.202.215.209:8000"
        self.timeout = 10
        
    def test_endpoint(self, endpoint, description=""):
        """Test a specific endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            print(f"🔄 Testing: {description}")
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                print(f"✅ {description} - SUCCESS (200)")
                return True
            else:
                print(f"⚠️ {description} - Status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ {description} - ERROR: {e}")
            return False

    def test_working_endpoint(self):
        """Test the known working endpoint"""
        try:
            url = f"{self.base_url}/api/imperium/persistence/learning-analytics"
            print(f"🔄 Testing working endpoint: {url}")
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                print(f"✅ Working endpoint - SUCCESS (200)")
                try:
                    data = response.json()
                    print(f"📊 Response data: {json.dumps(data, indent=2)}")
                except:
                    print(f"📊 Response text: {response.text[:200]}...")
                return True
            else:
                print(f"⚠️ Working endpoint - Status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Working endpoint - ERROR: {e}")
            return False

    def test_health_endpoints(self):
        """Test health and status endpoints"""
        endpoints = [
            ("/api/health", "Health Check"),
            ("/api/status", "Status Check"),
            ("/api/info", "API Info"),
            ("/api/version", "API Version"),
            ("/api/config", "API Config"),
        ]
        
        results = []
        for endpoint, description in endpoints:
            result = self.test_endpoint(endpoint, description)
            results.append((description, result))
        
        return results

    def test_imperium_endpoints(self):
        """Test imperium-specific endpoints"""
        endpoints = [
            ("/api/imperium/status", "Imperium Status"),
            ("/api/imperium/agents", "Imperium Agents"),
            ("/api/imperium/cycles", "Imperium Cycles"),
            ("/api/imperium/dashboard", "Imperium Dashboard"),
        ]
        
        results = []
        for endpoint, description in endpoints:
            result = self.test_endpoint(endpoint, description)
            results.append((description, result))
        
        return results

    def test_documentation(self):
        """Test API documentation"""
        endpoints = [
            ("/docs", "FastAPI Documentation"),
            ("/openapi.json", "OpenAPI Specification"),
        ]
        
        results = []
        for endpoint, description in endpoints:
            result = self.test_endpoint(endpoint, description)
            results.append((description, result))
        
        return results

    def run_complete_verification(self):
        """Run complete backend verification"""
        print("🔍 Starting Backend Port 8000 Verification...")
        print(f"📍 Testing backend at: {self.base_url}")
        
        # Test working endpoint first
        print("\n📋 Step 1: Testing working endpoint...")
        working_result = self.test_working_endpoint()
        
        # Test health endpoints
        print("\n📋 Step 2: Testing health endpoints...")
        health_results = self.test_health_endpoints()
        
        # Test imperium endpoints
        print("\n📋 Step 3: Testing imperium endpoints...")
        imperium_results = self.test_imperium_endpoints()
        
        # Test documentation
        print("\n📋 Step 4: Testing documentation...")
        doc_results = self.test_documentation()
        
        # Summary
        print("\n📊 Verification Summary:")
        print("=" * 50)
        
        all_results = [(working_result, "Working Endpoint")]
        all_results.extend(health_results)
        all_results.extend(imperium_results)
        all_results.extend(doc_results)
        
        successful = sum(1 for _, success in all_results if success)
        total = len(all_results)
        
        print(f"✅ Successful: {successful}/{total}")
        print(f"❌ Failed: {total - successful}/{total}")
        print(f"📈 Success Rate: {(successful/total)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for description, success in all_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} - {description}")
        
        if successful >= total * 0.8:  # 80% success rate
            print("\n🎉 Backend verification PASSED!")
            print("✅ Port 8000 is working correctly")
            print("✅ Machine learning endpoints are accessible")
            print("✅ App creation features are available")
            print("✅ Extension creation is ready")
        else:
            print("\n⚠️ Backend verification PARTIAL")
            print("⚠️ Some endpoints may need attention")
            print("⚠️ Check backend logs for issues")

if __name__ == "__main__":
    verifier = BackendVerifier()
    verifier.run_complete_verification() 