#!/usr/bin/env python3
"""
Check AI XP values in the database
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.core.database import init_database, get_session
from app.models.sql_models import AgentMetrics
from sqlalchemy import select

async def check_ai_xp():
    """Check XP values for all AIs"""
    print("🔍 Checking AI XP Values")
    print("=" * 50)
    
    try:
        # Initialize database
        await init_database()
        
        # Query all agent metrics
        async with get_session() as session:
            result = await session.execute(select(AgentMetrics))
            agents = result.scalars().all()
            
            if not agents:
                print("❌ No agent metrics found in database")
                return
            
            print(f"📊 Found {len(agents)} AI agents:")
            print()
            
            for agent in agents:
                print(f"🤖 {agent.agent_type.upper()}:")
                print(f"   XP: {agent.xp}")
                print(f"   Level: {agent.level}")
                print(f"   Learning Score: {agent.learning_score}")
                print(f"   Total Learning Cycles: {agent.total_learning_cycles}")
                print(f"   Success Rate: {agent.success_rate}")
                print(f"   Last Learning Cycle: {agent.last_learning_cycle}")
                print()
            
            # Calculate totals
            total_xp = sum(agent.xp for agent in agents)
            total_learning_score = sum(agent.learning_score for agent in agents)
            total_cycles = sum(agent.total_learning_cycles for agent in agents)
            
            print("📈 TOTALS:")
            print(f"   Total XP across all AIs: {total_xp}")
            print(f"   Total Learning Score: {total_learning_score}")
            print(f"   Total Learning Cycles: {total_cycles}")
            print()
            
            # Check for issues
            low_xp_agents = [agent for agent in agents if agent.xp < 50]
            if low_xp_agents:
                print("⚠️ AIs with low XP (< 50):")
                for agent in low_xp_agents:
                    print(f"   - {agent.agent_type}: {agent.xp} XP")
                print()
            
            zero_xp_agents = [agent for agent in agents if agent.xp == 0]
            if zero_xp_agents:
                print("❌ AIs with zero XP:")
                for agent in zero_xp_agents:
                    print(f"   - {agent.agent_type}")
                print()
                
    except Exception as e:
        print(f"❌ Error checking XP: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_ai_xp()) 