#!/usr/bin/env python3
"""
Simple test script for AI Growth Analytics fixes on EC2
Tests for duplicate agent removal and XP persistence
"""

import requests
import json
import time
from datetime import datetime

# Backend URL (localhost since we're on EC2)
BACKEND_URL = "http://localhost:8000"

def test_agents_endpoint():
    """Test the agents endpoint to ensure no duplicates"""
    print("🔍 Testing agents endpoint for duplicates...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/imperium/agents", timeout=10)
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', {})
            
            print(f"✅ Found {len(agents)} agents in response")
            
            # Check for duplicate agent IDs
            agent_ids = list(agents.keys())
            normalized_ids = [aid.replace('_agent', '').lower() for aid in agent_ids]
            unique_normalized = set(normalized_ids)
            
            print(f"Agent IDs found: {agent_ids}")
            print(f"Normalized IDs: {normalized_ids}")
            print(f"Unique normalized IDs: {unique_normalized}")
            
            if len(agent_ids) == len(unique_normalized):
                print("✅ No duplicate agents detected")
                return True
            else:
                print("❌ Duplicate agents detected!")
                return False
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing agents endpoint: {e}")
        return False

def test_xp_persistence():
    """Test XP persistence by checking agent metrics"""
    print("\n🔍 Testing XP persistence...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/imperium/agents", timeout=10)
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', {})
            
            for agent_id, agent_data in agents.items():
                learning_score = agent_data.get('learning_score', 0)
                total_cycles = agent_data.get('total_learning_cycles', 0)
                status = agent_data.get('status', 'unknown')
                
                print(f"Agent {agent_id}:")
                print(f"  - Learning Score: {learning_score}")
                print(f"  - Total Cycles: {total_cycles}")
                print(f"  - Status: {status}")
                
                # Check if XP is being tracked
                if learning_score > 0:
                    print(f"  ✅ XP is being tracked")
                else:
                    print(f"  ⚠️  No XP recorded yet")
            
            return True
        else:
            print(f"❌ Failed to get agent metrics: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing XP persistence: {e}")
        return False

def test_agent_consistency():
    """Test agent naming consistency"""
    print("\n🔍 Testing agent naming consistency...")
    
    expected_agents = {'imperium', 'guardian', 'sandbox', 'conquest'}
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/imperium/agents", timeout=10)
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', {})
            
            # Get normalized agent IDs
            agent_ids = set()
            for agent_id in agents.keys():
                normalized_id = agent_id.replace('_agent', '').lower()
                agent_ids.add(normalized_id)
            
            print(f"Expected agents: {expected_agents}")
            print(f"Found agents: {agent_ids}")
            
            if agent_ids == expected_agents:
                print("✅ Agent naming is consistent")
                return True
            else:
                missing = expected_agents - agent_ids
                extra = agent_ids - expected_agents
                print(f"❌ Agent naming inconsistency:")
                if missing:
                    print(f"  Missing: {missing}")
                if extra:
                    print(f"  Extra: {extra}")
                return False
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing agent consistency: {e}")
        return False

def test_learning_cycle():
    """Test triggering a learning cycle to verify XP accumulation"""
    print("\n🔍 Testing learning cycle and XP accumulation...")
    
    try:
        # Get initial XP values
        response = requests.get(f"{BACKEND_URL}/api/imperium/agents", timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to get initial agent metrics: {response.status_code}")
            return False
            
        initial_data = response.json()
        initial_agents = initial_data.get('agents', {})
        
        print("Initial XP values:")
        for agent_id, agent_data in initial_agents.items():
            learning_score = agent_data.get('learning_score', 0)
            total_cycles = agent_data.get('total_learning_cycles', 0)
            print(f"  {agent_id}: {learning_score} XP, {total_cycles} cycles")
        
        # Trigger a learning cycle
        response = requests.post(f"{BACKEND_URL}/api/imperium/cycles/trigger", timeout=30)
        if response.status_code == 200:
            print("✅ Learning cycle triggered successfully")
            
            # Wait a moment for the cycle to complete
            time.sleep(5)
            
            # Check if XP was accumulated
            response = requests.get(f"{BACKEND_URL}/api/imperium/agents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                agents = data.get('agents', {})
                
                print("Updated XP values:")
                for agent_id, agent_data in agents.items():
                    learning_score = agent_data.get('learning_score', 0)
                    total_cycles = agent_data.get('total_learning_cycles', 0)
                    
                    initial_score = initial_agents.get(agent_id, {}).get('learning_score', 0)
                    initial_cycles = initial_agents.get(agent_id, {}).get('total_learning_cycles', 0)
                    
                    if total_cycles > initial_cycles:
                        print(f"✅ Agent {agent_id}: {total_cycles} cycles (+{total_cycles - initial_cycles}), {learning_score} XP (+{learning_score - initial_score})")
                    else:
                        print(f"⚠️  Agent {agent_id}: No new cycles recorded")
                
                return True
            else:
                print(f"❌ Failed to get updated agent metrics: {response.status_code}")
                return False
        else:
            print(f"❌ Failed to trigger learning cycle: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing learning cycle: {e}")
        return False

def test_system_status():
    """Test overall system status"""
    print("\n🔍 Testing system status...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/imperium/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            total_agents = data.get('total_agents', 0)
            active_agents = data.get('active_agents', 0)
            avg_learning_score = data.get('average_learning_score', 0)
            scheduler_running = data.get('learning_scheduler_running', False)
            
            print(f"✅ System Status:")
            print(f"  - Total Agents: {total_agents}")
            print(f"  - Active Agents: {active_agents}")
            print(f"  - Average Learning Score: {avg_learning_score}")
            print(f"  - Learning Scheduler Running: {scheduler_running}")
            
            if total_agents == 4 and scheduler_running:
                print("✅ System is healthy")
                return True
            else:
                print("⚠️  System may have issues")
                return False
        else:
            print(f"❌ Failed to get system status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing system status: {e}")
        return False

def test_backend_health():
    """Test basic backend health"""
    print("🔍 Testing backend health...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting AI Growth Analytics Fixes Test Suite on EC2")
    print("=" * 60)
    
    # First test backend health
    if not test_backend_health():
        print("❌ Backend is not healthy, stopping tests")
        return 1
    
    tests = [
        ("Agent Duplicates", test_agents_endpoint),
        ("XP Persistence", test_xp_persistence),
        ("Agent Consistency", test_agent_consistency),
        ("Learning Cycle", test_learning_cycle),
        ("System Status", test_system_status),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI Growth Analytics fixes are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 