import requests
import time

def test_service_startup():
    """Test if the enhanced adversarial service can start and respond"""
    
    # Test 1: Check if service is running
    print("1. Testing if service is running...")
    try:
        response = requests.get("http://34.202.215.209:8001/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Service is running")
        else:
            print(f"   ❌ Service not running: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Service not accessible: {e}")
        return False
    
    # Test 2: Test basic functionality
    print("2. Testing basic functionality...")
    try:
        test_request = {
            "ai_types": ["imperium"],
            "target_domain": "system_level",
            "complexity": "basic",
            "reward_level": "standard",
            "adaptive": False
        }
        
        response = requests.post(
            "http://34.202.215.209:8001/generate-and-execute",
            json=test_request,
            timeout=30
        )
        
        if response.status_code == 200:
            print("   ✅ Service is functional")
            result = response.json()
            print(f"   📊 Response: {result.get('status', 'unknown')}")
            return True
        else:
            print(f"   ❌ Service error: {response.status_code}")
            print(f"   📄 Error details: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ Service timed out")
        return False
    except Exception as e:
        print(f"   ❌ Service error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Enhanced Adversarial Service...")
    success = test_service_startup()
    
    if success:
        print("🎉 Service is working correctly!")
    else:
        print("❌ Service has issues that need to be fixed") 