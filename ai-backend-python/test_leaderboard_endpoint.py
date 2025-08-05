#!/usr/bin/env python3
import requests
import json

def test_leaderboard_endpoint():
    """Test the leaderboard endpoint to verify it returns the correct data structure"""
    
    print("🧪 Testing Leaderboard Endpoint")
    print("=" * 50)
    
    url = "http://34.202.215.209:8000/custody/leaderboard"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response structure:")
            print(json.dumps(data, indent=2))
            
            # Check if leaderboard data is present
            if 'leaderboard' in data:
                leaderboard = data['leaderboard']
                print(f"\n📊 Leaderboard entries: {len(leaderboard)}")
                
                if leaderboard:
                    print("\n📋 Sample entry structure:")
                    sample_entry = leaderboard[0]
                    print(json.dumps(sample_entry, indent=2))
                    
                    # Check for required fields
                    required_fields = ['ai_type', 'learning_score', 'custody_xp', 'win_rate', 'recent_score']
                    missing_fields = []
                    
                    for field in required_fields:
                        if field not in sample_entry:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        print(f"❌ Missing fields: {missing_fields}")
                    else:
                        print("✅ All required fields present")
                else:
                    print("⚠️ Leaderboard is empty")
            else:
                print("❌ No 'leaderboard' key in response")
                
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_leaderboard_endpoint() 