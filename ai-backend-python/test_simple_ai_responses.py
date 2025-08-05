#!/usr/bin/env python3
import requests
import json
import time

def test_simple_ai_responses():
    """Test simple AI response generation"""
    
    print("🧪 Testing Simple AI Response Generation")
    print("=" * 50)
    
    url = "http://34.202.215.209:8001/generate-and-execute"
    
    payload = {
        "ai_types": ["imperium", "guardian"],
        "target_domain": "security_challenges",
        "complexity": "advanced",
        "reward_level": "standard",
        "adaptive": False
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
        end_time = time.time()
        
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Check scenario
            scenario = result.get('scenario', {})
            print(f"\n📋 Scenario:")
            print(f"   ID: {scenario.get('scenario_id', 'N/A')}")
            print(f"   Domain: {scenario.get('domain', 'N/A')}")
            print(f"   Description: {scenario.get('description', 'N/A')}")
            
            # Check results
            scenario_result = result.get('result', {})
            ai_results = scenario_result.get('results', {})
            
            print(f"\n🤖 AI Results: {len(ai_results)} AIs competed")
            
            if ai_results:
                for ai_type, ai_result in ai_results.items():
                    print(f"\n   {ai_type.upper()}:")
                    print(f"     Response: {ai_result.get('response_text', 'No response')[:150]}...")
                    print(f"     Score: {ai_result.get('score', 'N/A')}")
                    print(f"     XP Awarded: {ai_result.get('xp_awarded', 'N/A')}")
                    print(f"     Passed: {ai_result.get('passed', 'N/A')}")
            else:
                print("   ❌ No AI results found")
                
            # Check competition results
            competition_results = scenario_result.get('competition_results', {})
            winners = competition_results.get('winners', [])
            losers = competition_results.get('losers', [])
            
            print(f"\n🏆 Competition Results:")
            print(f"   Winners: {winners}")
            print(f"   Losers: {losers}")
            
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout after 30 seconds")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Complete!")

if __name__ == "__main__":
    test_simple_ai_responses() 