#!/usr/bin/env python3
"""
Check and Reset Database Script
Checks current AgentMetrics and resets them to level 1
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import get_session
from app.models.sql_models import AgentMetrics
from sqlalchemy import select, update

async def check_and_reset_database():
    """Check current database state and reset if needed"""
    print("🔍 Checking current database state...")
    
    try:
        session = get_session()
        async with session as s:
            # Check current state
            result = await s.execute(select(AgentMetrics))
            agents = result.scalars().all()
            
            print("\n📊 Current Database State:")
            for agent in agents:
                print(f"  {agent.agent_type}: Level {agent.level}, XP {agent.xp}, Score {agent.learning_score}")
            
            # Reset all agents to level 1
            print("\n🔄 Resetting all agents to level 1...")
            
            for agent in agents:
                agent.level = 1
                agent.xp = 0
                agent.learning_score = 0.0
                agent.total_learning_cycles = 0
                agent.successful_cycles = 0
                agent.failed_cycles = 0
                agent.last_learning_cycle = None
                agent.updated_at = datetime.utcnow()
            
            await s.commit()
            
            print("✅ Database reset completed!")
            
            # Verify reset
            result = await s.execute(select(AgentMetrics))
            agents = result.scalars().all()
            
            print("\n📊 New Database State:")
            for agent in agents:
                print(f"  {agent.agent_type}: Level {agent.level}, XP {agent.xp}, Score {agent.learning_score}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def main():
    """Main function"""
    await check_and_reset_database()

if __name__ == "__main__":
    asyncio.run(main()) 