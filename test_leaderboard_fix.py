#!/usr/bin/env python3
"""
Test script to diagnose the leaderboard 500 error
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.core.database import get_session, init_database
from app.models.sql_models import AgentMetrics
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def test_database_connection():
    """Test database connection and table existence"""
    print("🔍 Testing database connection...")
    
    try:
        # Initialize database
        await init_database()
        print("✅ Database initialized successfully")
        
        # Test session creation
        async with get_session() as session:
            print("✅ Database session created successfully")
            
            # Check if agent_metrics table exists and has data
            result = await session.execute(select(AgentMetrics))
            metrics = result.scalars().all()
            
            print(f"📊 Found {len(metrics)} agent metrics records")
            
            if metrics:
                for metric in metrics[:3]:  # Show first 3
                    print(f"  - {metric.agent_type}: Level {metric.level}, XP {metric.xp}")
            else:
                print("⚠️ No agent metrics found - this might be the issue")
                
                # Create some sample data
                print("🔄 Creating sample agent metrics...")
                sample_metrics = [
                    AgentMetrics(
                        agent_id="imperium_001",
                        agent_type="imperium",
                        learning_score=1000.0,
                        xp=500,
                        level=2,
                        custody_xp=200,
                        status="active"
                    ),
                    AgentMetrics(
                        agent_id="guardian_001", 
                        agent_type="guardian",
                        learning_score=800.0,
                        xp=300,
                        level=1,
                        custody_xp=150,
                        status="active"
                    ),
                    AgentMetrics(
                        agent_id="sandbox_001",
                        agent_type="sandbox", 
                        learning_score=1200.0,
                        xp=700,
                        level=3,
                        custody_xp=300,
                        status="active"
                    ),
                    AgentMetrics(
                        agent_id="conquest_001",
                        agent_type="conquest",
                        learning_score=900.0,
                        xp=400,
                        level=2,
                        custody_xp=250,
                        status="active"
                    )
                ]
                
                for metric in sample_metrics:
                    session.add(metric)
                
                await session.commit()
                print("✅ Sample agent metrics created")
                
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_agent_metrics_service():
    """Test the agent metrics service directly"""
    print("\n🔍 Testing Agent Metrics Service...")
    
    try:
        from app.services.agent_metrics_service import AgentMetricsService
        
        service = await AgentMetricsService.initialize()
        print("✅ Agent Metrics Service initialized")
        
        # Test getting all metrics
        all_metrics = await service.get_all_agent_metrics()
        print(f"📊 Retrieved {len(all_metrics)} agent metrics")
        
        for ai_type, metrics in all_metrics.items():
            print(f"  - {ai_type}: Level {metrics.get('level', 1)}, XP {metrics.get('xp', 0)}")
            
    except Exception as e:
        print(f"❌ Agent Metrics Service test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_leaderboard_endpoint():
    """Test the leaderboard endpoint directly"""
    print("\n🔍 Testing Leaderboard Endpoint...")
    
    try:
        from app.routers.agent_metrics import get_leaderboard
        
        result = await get_leaderboard()
        print("✅ Leaderboard endpoint executed successfully")
        print(f"📊 Leaderboard contains {len(result.get('leaderboard', []))} entries")
        
        for entry in result.get('leaderboard', [])[:3]:
            print(f"  - {entry.get('ai_type')}: Level {entry.get('level')}, Score {entry.get('learning_score')}")
            
    except Exception as e:
        print(f"❌ Leaderboard endpoint test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    print("🧪 Testing Leaderboard Fix...\n")
    
    await test_database_connection()
    await test_agent_metrics_service()
    await test_leaderboard_endpoint()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 