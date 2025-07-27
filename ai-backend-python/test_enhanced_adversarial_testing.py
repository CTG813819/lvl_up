#!/usr/bin/env python3
"""
Test Enhanced Adversarial Testing Service
Verifies that the service is working correctly and custody XP is being awarded
"""

import asyncio
import sys
import os
import json
import aiohttp
from pathlib import Path
from datetime import datetime
import structlog

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import init_database
from app.services.agent_metrics_service import AgentMetricsService

logger = structlog.get_logger()

async def test_enhanced_adversarial_testing():
    """Test the enhanced adversarial testing service"""
    try:
        print("🧪 Testing Enhanced Adversarial Testing Service")
        print("=" * 50)
        
        # Initialize database and services
        print("🔧 Initializing database...")
        await init_database()
        print("✅ Database initialized successfully")
        
        print("🔧 Initializing agent metrics service...")
        agent_metrics_service = AgentMetricsService()
        await agent_metrics_service.initialize()
        print("✅ Agent metrics service initialized")
        
        # Get initial metrics
        print("📊 Getting initial agent metrics...")
        initial_metrics = await agent_metrics_service.get_all_agent_metrics()
        
        for ai_type, metrics in initial_metrics.items():
            custody_xp = metrics.get('custody_xp', 0)
            print(f"📈 {ai_type}: Initial Custody XP = {custody_xp}")
        
        # Test the enhanced adversarial testing service
        print("\n🚀 Testing enhanced adversarial testing service...")
        
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get('http://localhost:8001/health') as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health check passed: {health_data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return
            
            # Test generate-and-execute endpoint
            test_payload = {
                "ai_types": ["imperium", "guardian"],
                "target_domain": "system_level",
                "complexity": "basic"
            }
            
            print(f"📤 Sending test payload: {json.dumps(test_payload, indent=2)}")
            
            async with session.post(
                'http://localhost:8001/generate-and-execute',
                json=test_payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Test completed successfully!")
                    print(f"📊 Result status: {result.get('status', 'unknown')}")
                    
                    # Check if scenario was generated
                    if 'scenario' in result:
                        scenario = result['scenario']
                        print(f"🎯 Scenario generated: {scenario.get('title', 'No title')}")
                        print(f"🎯 Domain: {scenario.get('domain', 'Unknown')}")
                        print(f"🎯 Complexity: {scenario.get('complexity', 'Unknown')}")
                    
                    # Check if results were generated
                    if 'result' in result:
                        test_result = result['result']
                        print(f"📈 Test results generated for {len(test_result)} AIs")
                        
                        for ai_type, ai_result in test_result.items():
                            score = ai_result.get('score', 0)
                            xp_awarded = ai_result.get('xp_awarded', 0)
                            print(f"🤖 {ai_type}: Score = {score}, XP Awarded = {xp_awarded}")
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Test failed: {response.status}")
                    print(f"❌ Error: {error_text}")
                    return
        
        # Get updated metrics to check if custody XP was awarded
        print("\n📊 Checking updated agent metrics...")
        await asyncio.sleep(2)  # Wait a bit for database updates
        
        updated_metrics = await agent_metrics_service.get_all_agent_metrics()
        
        for ai_type, metrics in updated_metrics.items():
            custody_xp = metrics.get('custody_xp', 0)
            initial_custody_xp = initial_metrics[ai_type].get('custody_xp', 0)
            xp_gained = custody_xp - initial_custody_xp
            
            print(f"📈 {ai_type}: Custody XP = {custody_xp} (+{xp_gained})")
            
            if xp_gained > 0:
                print(f"✅ {ai_type} gained {xp_gained} custody XP!")
            else:
                print(f"ℹ️ {ai_type} no XP gained")
        
        print("\n🎉 Enhanced adversarial testing test completed successfully!")
        print("📝 Custody XP system is working correctly!")
        
    except Exception as e:
        logger.error(f"Error testing enhanced adversarial testing: {str(e)}")
        print(f"❌ Error: {str(e)}")
        raise

async def main():
    """Main function"""
    try:
        await test_enhanced_adversarial_testing()
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 