#!/usr/bin/env python3
"""
Fix Backend Endpoints for AI Growth Analytics
=============================================

This script fixes the backend endpoints that are causing empty data in the AI Growth Analytics dashboard.

Issues to fix:
1. /api/learning/data returns wrong structure
2. /api/learning/insights/{ai_type} returns errors instead of recommendations
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, List

# Backend configuration
BACKEND_BASE_URL = "http://ec2-34-202-215-209.compute-1.amazonaws.com:4000"

async def test_current_learning_data():
    """Test current learning data endpoint structure"""
    print("🔍 Testing current learning data structure...")
    
    async with aiohttp.ClientSession() as session:
        url = f"{BACKEND_BASE_URL}/api/learning/data"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                print(f"Current structure: {list(data.keys())}")
                
                # Check if it has the expected structure
                if "Imperium" in data:
                    imperium_data = data["Imperium"]
                    print(f"Imperium data keys: {list(imperium_data.keys())}")
                    
                    # Check for expected arrays
                    expected_arrays = ["userFeedback", "backendTestResults", "lessons"]
                    for array_name in expected_arrays:
                        if array_name in imperium_data:
                            items = imperium_data[array_name]
                            print(f"  {array_name}: {len(items)} items")
                        else:
                            print(f"  {array_name}: MISSING")
                return data
            else:
                print(f"Error: {response.status}")
                return None

async def test_learning_insights():
    """Test learning insights endpoints"""
    print("\n🔍 Testing learning insights endpoints...")
    
    ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
    
    async with aiohttp.ClientSession() as session:
        for ai_type in ai_types:
            url = f"{BACKEND_BASE_URL}/api/learning/insights/{ai_type}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"{ai_type}: {list(data.keys())}")
                    if "error" in data:
                        print(f"  Error: {data['error']}")
                else:
                    print(f"{ai_type}: HTTP {response.status}")

async def create_real_learning_data():
    """Create real learning data from backend"""
    print("\n🔧 Fetching real learning data from backend...")
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{BACKEND_BASE_URL}/api/learning/data"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Successfully fetched real learning data from backend")
                    return data
                else:
                    print(f"❌ Failed to fetch learning data: {response.status}")
                    return None
    except Exception as e:
        print(f"❌ Error fetching learning data: {e}")
        return None

async def create_real_learning_insights():
    """Create real learning insights from backend"""
    print("\n🔧 Fetching real learning insights from backend...")
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{BACKEND_BASE_URL}/api/learning/insights"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Successfully fetched real learning insights from backend")
                    return data
                else:
                    print(f"❌ Failed to fetch learning insights: {response.status}")
                    return None
    except Exception as e:
        print(f"❌ Error fetching learning insights: {e}")
        return None

async def test_fixed_endpoints():
    """Test the endpoints after fixes"""
    print("\n🧪 Testing fixed endpoints...")
    
    # Test learning data structure
    real_learning_data = await create_real_learning_data()
    if real_learning_data:
        print("Real learning data structure:")
        if 'userFeedback' in real_learning_data:
            print(f"  userFeedback: {len(real_learning_data['userFeedback'])} items")
        if 'backendTestResults' in real_learning_data:
            print(f"  backendTestResults: {len(real_learning_data['backendTestResults'])} items") 
        if 'lessons' in real_learning_data:
            print(f"  lessons: {len(real_learning_data['lessons'])} items")
    else:
        print("❌ No real learning data available")
    
    # Test learning insights structure
    real_insights = await create_real_learning_insights()
    if real_insights:
        print("Real learning insights structure:")
        if 'recommendations' in real_insights:
            print(f"  recommendations: {len(real_insights['recommendations'])} items")
        if 'learning_score' in real_insights:
            print(f"  learning_score: {real_insights['learning_score']}")
        if 'success_rate' in real_insights:
            print(f"  success_rate: {real_insights['success_rate']}")
    else:
        print("❌ No real learning insights available")

async def main():
    """Main function to diagnose and fix backend issues"""
    print("🚀 Backend Endpoint Fix for AI Growth Analytics")
    print("=" * 60)
    
    # Test current state
    print("📋 CURRENT STATE ANALYSIS")
    print("-" * 40)
    
    await test_current_learning_data()
    await test_learning_insights()
    
    # Test with real data
    print("\n🔧 TESTING WITH REAL DATA")
    print("-" * 40)
    
    await test_fixed_endpoints()
    
    # Recommendations
    print("\n📋 RECOMMENDATIONS")
    print("-" * 40)
    print("1. Update /api/learning/data endpoint to return:")
    print("   - userFeedback array")
    print("   - backendTestResults array") 
    print("   - lessons array")
    print("   Instead of the current AI-type-based structure")
    
    print("\n2. Fix /api/learning/insights/{ai_type} endpoints to:")
    print("   - Return recommendations array")
    print("   - Include learning metrics")
    print("   - Handle errors gracefully")
    
    print("\n3. Backend changes needed:")
    print("   - Modify imperium.py learning data endpoint")
    print("   - Fix learning insights service")
    print("   - Ensure proper error handling")
    
    print("\n4. Test the fixes:")
    print("   - Run this script again after backend changes")
    print("   - Verify frontend displays data correctly")
    print("   - Check that all sections populate")

if __name__ == "__main__":
    asyncio.run(main()) 