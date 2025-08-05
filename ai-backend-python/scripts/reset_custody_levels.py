#!/usr/bin/env python3
"""
Reset Custody Levels Script
Resets all AI custody levels and metrics to initial state
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import get_session
from app.models.sql_models import AgentMetrics
from app.services.custody_protocol_service import CustodyProtocolService
from sqlalchemy import select, update, delete

async def reset_custody_levels():
    """Reset all custody levels and metrics to initial state"""
    print("🔄 Starting custody level reset...")
    
    try:
        # Initialize custody service
        custody_service = CustodyProtocolService()
        await custody_service.initialize()
        
        # Reset custody metrics in memory
        print("📊 Resetting in-memory custody metrics...")
        for ai_type in custody_service.custody_metrics:
            custody_service.custody_metrics[ai_type] = {
                "total_tests_given": 0,
                "total_tests_passed": 0,
                "total_tests_failed": 0,
                "pass_rate": 0,
                "current_difficulty": "basic",
                "custody_level": 1,
                "custody_xp": 0,
                "consecutive_successes": 0,
                "consecutive_failures": 0,
                "last_test_date": None,
                "last_level_up": None,
                "learning_cycles_completed": 0
            }
        
        # Reset database metrics
        print("🗄️ Resetting database metrics...")
        session = get_session()
        async with session as s:
            # Reset AgentMetrics table
            await s.execute(delete(AgentMetrics))
            
            # Create fresh entries for each AI type
            ai_types = ["guardian", "imperium", "sandbox", "conquest", "sandbox_agent", "imperium_agent", "guardian_agent"]
            
            for ai_type in ai_types:
                new_metrics = AgentMetrics(
                    agent_type=ai_type,
                    learning_score=0.0,
                    level=1,
                    total_learning_cycles=0,
                    successful_cycles=0,
                    failed_cycles=0,
                    last_learning_cycle=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                s.add(new_metrics)
            
            await s.commit()
            print(f"✅ Reset {len(ai_types)} AI metrics in database")
        
        # Persist reset metrics to database
        print("💾 Persisting reset metrics...")
        for ai_type in custody_service.custody_metrics:
            await custody_service._persist_custody_metrics_to_database(ai_type, custody_service.custody_metrics[ai_type])
        
        print("🎉 Custody levels reset successfully!")
        print("\n📋 Reset Summary:")
        print("- All AIs set to Level 1")
        print("- All XP reset to 0")
        print("- All test counts reset to 0")
        print("- All learning cycles reset to 0")
        print("- All consecutive counts reset to 0")
        
        # Display current state
        print("\n📊 Current State:")
        for ai_type, metrics in custody_service.custody_metrics.items():
            print(f"  {ai_type}: Level {metrics['custody_level']}, XP {metrics['custody_xp']}, Tests {metrics['total_tests_passed']}/{metrics['total_tests_given']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting custody levels: {str(e)}")
        return False

async def reset_specific_ai(ai_type: str):
    """Reset custody levels for a specific AI"""
    print(f"🔄 Resetting custody levels for {ai_type}...")
    
    try:
        custody_service = CustodyProtocolService()
        await custody_service.initialize()
        
        # Reset specific AI metrics
        custody_service.custody_metrics[ai_type] = {
            "total_tests_given": 0,
            "total_tests_passed": 0,
            "total_tests_failed": 0,
            "pass_rate": 0,
            "current_difficulty": "basic",
            "custody_level": 1,
            "custody_xp": 0,
            "consecutive_successes": 0,
            "consecutive_failures": 0,
            "last_test_date": None,
            "last_level_up": None,
            "learning_cycles_completed": 0
        }
        
        # Reset database entry
        session = get_session()
        async with session as s:
            await s.execute(
                delete(AgentMetrics).where(AgentMetrics.agent_type == ai_type)
            )
            
            new_metrics = AgentMetrics(
                agent_type=ai_type,
                learning_score=0.0,
                level=1,
                total_learning_cycles=0,
                successful_cycles=0,
                failed_cycles=0,
                last_learning_cycle=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            s.add(new_metrics)
            await s.commit()
        
        # Persist to database
        await custody_service._persist_custody_metrics_to_database(ai_type, custody_service.custody_metrics[ai_type])
        
        print(f"✅ Successfully reset {ai_type}")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting {ai_type}: {str(e)}")
        return False

async def main():
    """Main function"""
    if len(sys.argv) > 1:
        ai_type = sys.argv[1]
        if ai_type == "--all":
            await reset_custody_levels()
        else:
            await reset_specific_ai(ai_type)
    else:
        print("Usage:")
        print("  python reset_custody_levels.py --all          # Reset all AIs")
        print("  python reset_custody_levels.py guardian       # Reset specific AI")
        print("  python reset_custody_levels.py imperium       # Reset specific AI")
        print("  python reset_custody_levels.py sandbox        # Reset specific AI")
        print("  python reset_custody_levels.py conquest       # Reset specific AI")

if __name__ == "__main__":
    asyncio.run(main()) 