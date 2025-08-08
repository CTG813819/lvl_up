#!/usr/bin/env python3
import requests
import json
import time

def test_ai_response_debug():
    """Test AI response generation with detailed debugging"""
    
    url = "http://34.202.215.209:8001/generate-and-execute"
    
    payload = {
        "ai_types": ["imperium", "guardian"],
        "target_domain": "system_level",
        "complexity": "basic",
        "reward_level": "standard",
        "adaptive": False
    }
    
    print("🧪 Testing AI response generation...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=60)
        end_time = time.time()
        
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Response structure:")
            print(json.dumps(result, indent=2))
            
            # Check if results are present
            if 'result' in result:
                scenario_result = result['result']
                if 'results' in scenario_result:
                    ai_results = scenario_result['results']
                    print(f"\n📊 AI Results found: {len(ai_results)} entries")
                    for ai_type, ai_result in ai_results.items():
                        print(f"  {ai_type}: {ai_result.get('response_text', 'No response text')}")
                else:
                    print("❌ No 'results' in scenario result")
            else:
                print("❌ No 'result' in response")
                
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout after 60 seconds")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ai_response_debug() 