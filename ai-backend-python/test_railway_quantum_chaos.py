#!/usr/bin/env python3
"""
Test script to verify quantum chaos endpoints are working on Railway
"""

import requests
import json
import time

# Railway URL
RAILWAY_URL = "https://compassionate-truth-production-2fcd.up.railway.app"

def test_quantum_chaos_endpoints():
    """Test all quantum chaos endpoints"""
    print("🧪 Testing Quantum Chaos endpoints on Railway...")
    print(f"📍 URL: {RAILWAY_URL}")
    print("=" * 60)
    
    # Test endpoints
    endpoints = [
        ("/api/quantum-chaos/generate", "GET", "Quantum Chaos Generation"),
        ("/api/quantum-chaos/status", "GET", "Quantum Chaos Status"),
        ("/api/stealth-hub/assimilate", "POST", "Stealth Assimilation"),
        ("/api/rolling-password/initialize", "POST", "Rolling Password"),
        ("/api/project-horus-v2/status", "GET", "Project Horus Enhanced"),
        ("/health", "GET", "Health Check"),
        ("/api/health", "GET", "API Health"),
    ]
    
    results = []
    
    for endpoint, method, description in endpoints:
        try:
            url = f"{RAILWAY_URL}{endpoint}"
            print(f"\n🔍 Testing: {description}")
            print(f"   URL: {url}")
            print(f"   Method: {method}")
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                # For POST endpoints, send minimal data
                data = {"test": True}
                response = requests.post(url, json=data, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS")
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            elif response.status_code == 404:
                print("   ⚠️  NOT FOUND (endpoint not implemented)")
            elif response.status_code == 405:
                print("   ⚠️  METHOD NOT ALLOWED")
            else:
                print(f"   ❌ ERROR: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
            results.append({
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status_code": response.status_code,
                "success": response.status_code == 200
            })
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ CONNECTION ERROR: {e}")
            results.append({
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status_code": "ERROR",
                "success": False,
                "error": str(e)
            })
        
        time.sleep(1)  # Small delay between requests
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    for result in results:
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} {result['description']}: {result['status_code']}")
    
    return results

if __name__ == "__main__":
    test_quantum_chaos_endpoints() 