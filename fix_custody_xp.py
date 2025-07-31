#!/usr/bin/env python3
"""
Fix Custody XP Script
====================

This script fixes the custody XP issue by awarding initial custody XP to all AIs
based on their existing learning scores and ensuring the XP system is working properly.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import get_session, init_database
from app.models.sql_models import AgentMetrics
from app.services.agent_metrics_service import AgentMetricsService
from sqlalchemy import select
import structlog

logger = structlog.get_logger()

async def fix_custody_xp():
    """Fix custody XP for all AIs"""
    try:
        print("🔧 Fixing custody XP system...")
        
        # Initialize database
        await init_database()
        
        # Initialize agent metrics service
        agent_metrics_service = await AgentMetricsService.initialize()
        
        # Get all AI types
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            print(f"\n📊 Processing {ai_type}...")
            
            # Get current metrics
            metrics = await agent_metrics_service.get_agent_metrics(ai_type)
            
            if metrics:
                current_learning_score = metrics.get("learning_score", 0.0)
                current_custody_xp = metrics.get("custody_xp", 0)
                current_level = metrics.get("level", 1)
                
                print(f"  Current learning score: {current_learning_score}")
                print(f"  Current custody XP: {current_custody_xp}")
                print(f"  Current level: {current_level}")
                
                # Calculate appropriate custody XP based on learning score
                # Convert learning score to custody XP (1:1 ratio for now)
                target_custody_xp = int(current_learning_score)
                
                if current_custody_xp == 0 and target_custody_xp > 0:
                    # Award custody XP
                    xp_to_award = target_custody_xp
                    success = await agent_metrics_service.update_custody_xp(ai_type, xp_to_award)
                    
                    if success:
                        print(f"  ✅ Awarded {xp_to_award} custody XP to {ai_type}")
                        
                        # Verify the update
                        updated_metrics = await agent_metrics_service.get_agent_metrics(ai_type)
                        if updated_metrics:
                            new_custody_xp = updated_metrics.get("custody_xp", 0)
                            new_custody_level = updated_metrics.get("custody_level", 1)
                            print(f"  📈 New custody XP: {new_custody_xp}")
                            print(f"  📈 New custody level: {new_custody_level}")
                    else:
                        print(f"  ❌ Failed to award custody XP to {ai_type}")
                else:
                    print(f"  ℹ️  {ai_type} already has custody XP: {current_custody_xp}")
            else:
                print(f"  ⚠️  No metrics found for {ai_type} - creating default")
                
                # Create default metrics with some custody XP
                default_metrics = {
                    "total_tests_given": 0,
                    "total_tests_passed": 0,
                    "total_tests_failed": 0,
                    "current_difficulty": "basic",
                    "last_test_date": None,
                    "consecutive_failures": 0,
                    "consecutive_successes": 0,
                    "test_history": [],
                    "custody_level": 1,
                    "custody_xp": 50,  # Start with 50 custody XP
                    "level": 1,
                    "xp": 0,
                    "learning_score": 0.0,
                    "pass_rate": 0.0,
                    "failure_rate": 0.0
                }
                
                success = await agent_metrics_service.create_or_update_agent_metrics(ai_type, default_metrics)
                if success:
                    print(f"  ✅ Created default metrics for {ai_type} with 50 custody XP")
                else:
                    print(f"  ❌ Failed to create default metrics for {ai_type}")
        
        print("\n🔍 Verifying custody XP system...")
        
        # Verify all AIs have custody XP
        for ai_type in ai_types:
            metrics = await agent_metrics_service.get_agent_metrics(ai_type)
            if metrics:
                custody_xp = metrics.get("custody_xp", 0)
                custody_level = metrics.get("custody_level", 1)
                learning_score = metrics.get("learning_score", 0.0)
                
                print(f"  {ai_type}: Custody XP {custody_xp}, Level {custody_level}, Learning Score {learning_score}")
                
                if custody_xp == 0:
                    print(f"    ⚠️  {ai_type} still has 0 custody XP!")
                else:
                    print(f"    ✅ {ai_type} has proper custody XP")
            else:
                print(f"  ❌ {ai_type}: No metrics found")
        
        print("\n✅ Custody XP fix completed!")
        
    except Exception as e:
        print(f"❌ Error fixing custody XP: {str(e)}")
        logger.error(f"Error fixing custody XP: {str(e)}")

async def test_custody_xp_award():
    """Test the custody XP award system"""
    try:
        print("\n🧪 Testing custody XP award system...")
        
        # Initialize services
        await init_database()
        agent_metrics_service = await AgentMetricsService.initialize()
        
        # Test awarding XP to guardian
        test_ai = "guardian"
        test_xp = 25
        
        print(f"Awarding {test_xp} custody XP to {test_ai}...")
        
        # Get current metrics
        before_metrics = await agent_metrics_service.get_agent_metrics(test_ai)
        before_xp = before_metrics.get("custody_xp", 0) if before_metrics else 0
        
        # Award XP
        success = await agent_metrics_service.update_custody_xp(test_ai, test_xp)
        
        if success:
            # Get updated metrics
            after_metrics = await agent_metrics_service.get_agent_metrics(test_ai)
            after_xp = after_metrics.get("custody_xp", 0) if after_metrics else 0
            
            print(f"✅ XP award test successful!")
            print(f"  Before: {before_xp} custody XP")
            print(f"  After: {after_xp} custody XP")
            print(f"  Awarded: {after_xp - before_xp} XP")
            
            if after_xp > before_xp:
                print("  ✅ XP award system is working correctly!")
            else:
                print("  ❌ XP award system may have issues")
        else:
            print("❌ XP award test failed")
            
    except Exception as e:
        print(f"❌ Error testing custody XP award: {str(e)}")

async def main():
    """Main function"""
    print("🚀 Starting custody XP fix...")
    
    # Fix custody XP for all AIs
    await fix_custody_xp()
    
    # Test the XP award system
    await test_custody_xp_award()
    
    print("\n🎉 Custody XP fix and test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 