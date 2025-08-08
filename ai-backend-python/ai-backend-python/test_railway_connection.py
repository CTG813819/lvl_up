#!/usr/bin/env python3
import requests
import json
import time

def test_railway_connection():
    """Test the Railway backend connection"""
    railway_url = "https://lvlup-production.up.railway.app"
    
    print("🔍 Testing Railway Backend Connection")
    print("=" * 50)
    print(f"Testing URL: {railway_url}")
    print()
    
    # Test endpoints
    endpoints = [
        "/health",
        "/api/learning/data",
        "/api/imperium/status", 
        "/api/proposals",
        "/api/conquest/deployments",
        "/api/approval/pending",
        "/api/guardian/code-review/threat-detection",
        "/api/missions/statistics",
        "/api/growth/insights",
        "/"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            print(f"Testing {endpoint}...")
            response = requests.get(
                f"{railway_url}{endpoint}",
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            status = response.status_code
            if status == 200:
                print(f"   ✅ {endpoint} - Status: {status}")
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        keys = list(data.keys())[:3]
                        print(f"      📊 Response keys: {', '.join(keys)}...")
                    else:
                        print(f"      📊 Response: {str(data)[:100]}...")
                except:
                    print(f"      📊 Response: {response.text[:100]}...")
            elif status == 404:
                print(f"   ⚠️  {endpoint} - Status: {status} (Not Found)")
            else:
                print(f"   ❌ {endpoint} - Status: {status}")
                
            results[endpoint] = status
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {endpoint} - Error: {e}")
            results[endpoint] = "ERROR"
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CONNECTION TEST SUMMARY")
    print("=" * 50)
    print(f"Railway URL: {railway_url}")
    
    successful = sum(1 for status in results.values() if status == 200)
    total = len(results)
    
    print(f"Successful endpoints: {successful}/{total}")
    print(f"Success rate: {(successful/total)*100:.1f}%")
    
    if successful > 0:
        print("\n✅ Railway backend is accessible!")
        print("✅ Frontend should be able to connect to Railway backend")
    else:
        print("\n❌ Railway backend is not accessible")
        print("❌ Frontend connection to Railway backend will fail")
    
    # Check specific endpoints that the frontend uses
    frontend_endpoints = [
        "/api/learning/data",
        "/api/imperium/status",
        "/api/proposals"
    ]
    
    print("\n🔍 Frontend-Specific Endpoints:")
    for endpoint in frontend_endpoints:
        status = results.get(endpoint, "NOT TESTED")
        icon = "✅" if status == 200 else "❌" if status == "ERROR" else "⚠️"
        print(f"   {icon} {endpoint}: {status}")
    
    return successful > 0

def test_frontend_network_config():
    """Test the frontend network configuration compatibility"""
    print("\n🔍 Testing Frontend Network Configuration")
    print("=" * 50)
    
    # Test URLs that the frontend uses
    test_urls = [
        "https://lvlup-production.up.railway.app",
        "http://10.0.2.2:8000",  # Android emulator
        "http://localhost:8000",   # Local development
        "http://127.0.0.1:8000",  # Local development fallback
    ]
    
    working_endpoint = "/api/learning/data"
    
    for url in test_urls:
        try:
            response = requests.get(
                f"{url}{working_endpoint}",
                timeout=5,
                headers={"Content-Type": "application/json"}
            )
            
            if response.statusCode == 200:
                print(f"   ✅ Compatible URL found: {url}")
                return True
        except:
            continue
    
    print("   ❌ No compatible URLs found")
    return False

if __name__ == "__main__":
    # Test Railway connection
    railway_accessible = test_railway_connection()
    
    # Test frontend network config
    frontend_compatible = test_frontend_network_config()
    
    # Final summary
    print("\n" + "=" * 50)
    print("🎯 FINAL VERDICT")
    print("=" * 50)
    
    if railway_accessible and frontend_compatible:
        print("✅ Frontend is properly connected to Railway backend!")
        print("✅ All systems are operational")
    elif railway_accessible:
        print("⚠️  Railway backend is accessible but frontend config may need updates")
        print("⚠️  Check frontend network configuration")
    else:
        print("❌ Railway backend is not accessible")
        print("❌ Frontend connection to Railway backend will fail")
        print("❌ Check Railway deployment status") 