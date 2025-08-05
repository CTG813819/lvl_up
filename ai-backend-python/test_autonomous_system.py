#!/usr/bin/env python3
"""
Test script to verify autonomous test generation system
"""
import asyncio
import httpx
import json
import time
from datetime import datetime

async def test_autonomous_system():
    """Test the autonomous test generation system"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Autonomous Test Generation System")
    print("=" * 50)
    
    # Test 1: Check if service is running
    print("\n1. Checking service status...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print("✅ Service is running")
            else:
                print("❌ Service not responding")
                return
    except Exception as e:
        print(f"❌ Error connecting to service: {e}")
        return
    
    # Test 2: Trigger custody protocol test
    print("\n2. Triggering custody protocol test...")
    try:
        async with httpx.AsyncClient() as client:
            # Trigger a test for one of the AIs
            test_data = {
                "ai_type": "imperium",
                "test_type": "autonomous",
                "difficulty": "intermediate"
            }
            
            response = await client.post(
                f"{base_url}/api/custody-protocol/test",
                json=test_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Custody test triggered successfully")
                print(f"📊 Test result: {result}")
            else:
                print(f"❌ Custody test failed: {response.status_code}")
                print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error triggering custody test: {e}")
    
    # Test 3: Check agent metrics to see if tests are being recorded
    print("\n3. Checking agent metrics...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/agent-metrics/")
            if response.status_code == 200:
                metrics = response.json()
                print("✅ Agent metrics retrieved")
                for ai, data in metrics.items():
                    print(f"🤖 {ai}: Level {data.get('level', 'N/A')}, XP {data.get('xp', 'N/A')}, Tests: {data.get('total_tests_given', 'N/A')}")
            else:
                print(f"❌ Failed to get agent metrics: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting agent metrics: {e}")
    
    # Test 4: Check recent logs for autonomous scenarios
    print("\n4. Checking for autonomous scenario logs...")
    try:
        import subprocess
        result = subprocess.run([
            "sudo", "journalctl", "-u", "ai-backend-python.service", 
            "--since", "5 minutes ago", "-n", "50"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logs = result.stdout
            autonomous_indicators = [
                "🎯 Generated autonomous test scenario",
                "🤖 Generated autonomous response",
                "🏆 AUTONOMOUS TEST COMPLETED",
                "📝 AI RESPONSE for",
                "📊 TEST RESULT for"
            ]
            
            found_indicators = []
            for indicator in autonomous_indicators:
                if indicator in logs:
                    found_indicators.append(indicator)
            
            if found_indicators:
                print("✅ Found autonomous test indicators:")
                for indicator in found_indicators:
                    print(f"   - {indicator}")
            else:
                print("⚠️ No autonomous test indicators found in recent logs")
                print("   This might mean tests haven't run yet or autonomous generation isn't triggering")
        else:
            print("❌ Failed to check logs")
    except Exception as e:
        print(f"❌ Error checking logs: {e}")
    
    # Test 5: Manual test of autonomous generator
    print("\n5. Testing autonomous generator directly...")
    try:
        import sys
        import os
        sys.path.append('/home/ubuntu/ai-backend-python')
        
        from app.services.autonomous_test_generator import autonomous_test_generator
        
        # Test scenario generation
        scenario = await autonomous_test_generator.generate_autonomous_scenario(
            ai_types=["imperium"], 
            difficulty="intermediate"
        )
        
        print("✅ Autonomous scenario generated:")
        print(f"   Scenario: {scenario['scenario'][:100]}...")
        print(f"   Requirements: {len(scenario['requirements'])} items")
        print(f"   Evaluation criteria: {len(scenario['evaluation_criteria'])} categories")
        
        # Test AI response generation
        response = await autonomous_test_generator.generate_ai_response(
            ai_name="imperium",
            scenario=scenario['scenario'],
            requirements=scenario['requirements']
        )
        
        print("✅ Autonomous AI response generated:")
        print(f"   Response length: {len(response)} characters")
        print(f"   Response preview: {response[:200]}...")
        
    except Exception as e:
        print(f"❌ Error testing autonomous generator: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Autonomous Test Generation System Test Complete")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_autonomous_system())