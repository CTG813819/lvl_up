import requests
import json
import time

def test_enhanced_service():
    url = "http://34.202.215.209:8001/generate-and-execute"
    
    payload = {
        "ai_types": ["imperium", "guardian"],
        "target_domain": "system_level",
        "complexity": "advanced",
        "reward_level": "standard",
        "adaptive": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Testing enhanced adversarial service...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        end_time = time.time()
        
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout after 30 seconds")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_enhanced_service() 