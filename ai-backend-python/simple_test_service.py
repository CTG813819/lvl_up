#!/usr/bin/env python3
"""
Simple test for Enhanced Adversarial Testing Service
Test the service methods directly to identify the issue
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import init_database
from app.services.agent_metrics_service import AgentMetricsService
from app.services.enhanced_adversarial_testing_service import EnhancedAdversarialTestingService

async def test_service_directly():
    """Test the enhanced adversarial testing service directly"""
    print("🔍 Testing Enhanced Adversarial Testing Service Directly")
    print("=" * 60)
    
    try:
        # Initialize database
        print("🔧 Initializing database...")
        await init_database()
        print("✅ Database initialized successfully")
        
        # Initialize agent metrics service
        print("🔧 Initializing agent metrics service...")
        agent_metrics_service = AgentMetricsService()
        await agent_metrics_service.initialize()
        print("✅ Agent metrics service initialized")
        
        # Initialize enhanced adversarial testing service
        print("🔧 Initializing enhanced adversarial testing service...")
        enhanced_testing_service = EnhancedAdversarialTestingService()
        await enhanced_testing_service.initialize()
        print("✅ Enhanced adversarial testing service initialized")
        
        # Test 1: Generate a simple scenario
        print("\n1. Testing scenario generation...")
        try:
            scenario = await enhanced_testing_service.generate_diverse_adversarial_scenario(
                ai_types=["imperium", "guardian"],
                target_domain="system_level",
                complexity="basic"
            )
            print(f"✅ Scenario generated successfully!")
            print(f"📊 Scenario keys: {list(scenario.keys())}")
            print(f"📊 Scenario domain: {scenario.get('domain', 'N/A')}")
            print(f"📊 Scenario complexity: {scenario.get('complexity', 'N/A')}")
        except Exception as e:
            print(f"❌ Scenario generation failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 2: Execute the scenario
        print("\n2. Testing scenario execution...")
        try:
            result = await enhanced_testing_service.execute_diverse_adversarial_test(scenario)
            print(f"✅ Scenario executed successfully!")
            print(f"📊 Result keys: {list(result.keys())}")
            print(f"📊 Number of AI results: {len(result.get('results', {}))}")
        except Exception as e:
            print(f"❌ Scenario execution failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 3: Check if custody XP was awarded
        print("\n3. Checking custody XP...")
        try:
            imperium_metrics = await agent_metrics_service.get_agent_metrics("imperium")
            guardian_metrics = await agent_metrics_service.get_agent_metrics("guardian")
            
            print(f"📊 Imperium custody XP: {imperium_metrics.get('custody_xp', 0)}")
            print(f"📊 Guardian custody XP: {guardian_metrics.get('custody_xp', 0)}")
            
            if imperium_metrics.get('custody_xp', 0) > 0 or guardian_metrics.get('custody_xp', 0) > 0:
                print("✅ Custody XP was awarded!")
            else:
                print("ℹ️ No custody XP awarded yet")
                
        except Exception as e:
            print(f"❌ Error checking custody XP: {e}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main function"""
    try:
        await test_service_directly()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 