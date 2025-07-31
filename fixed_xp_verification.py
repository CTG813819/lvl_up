#!/usr/bin/env python3
"""
XP Verification Script
====================

This script verifies that XP values are being read correctly by the custody service.
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog

logger = structlog.get_logger()

async def verify_xp_values():
    """Verify that XP values are being read correctly"""
    try:
        print("🔍 Verifying XP values...")
        
        # Import the services
        from app.services.agent_metrics_service import AgentMetricsService
        
        # Create agent metrics service
        agent_metrics_service = AgentMetricsService()
        
        # Test AI types
        ai_types = ['imperium', 'guardian', 'sandbox', 'conquest']
        
        print("📊 Testing XP value retrieval:")
        for ai_type in ai_types:
            # Get custody metrics
            custody_metrics = await agent_metrics_service.get_custody_metrics(ai_type)
            
            if custody_metrics:
                xp = custody_metrics.get('xp', 0)
                custody_xp = custody_metrics.get('custody_xp', 0)
                level = custody_metrics.get('level', 1)
                
                print(f"   {ai_type}: XP={xp}, Custody_XP={custody_xp}, Level={level}")
                
                # Check if XP values are correct
                if xp > 0:
                    print(f"   ✅ {ai_type} has correct XP: {xp}")
                else:
                    print(f"   ❌ {ai_type} has zero XP: {xp}")
            else:
                print(f"   ❌ {ai_type}: No custody metrics found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying XP values: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function"""
    print("🚀 XP Verification")
    print("=" * 40)
    
    await verify_xp_values()
    
    print("\n✅ XP verification completed!")

if __name__ == "__main__":
    asyncio.run(main()) 