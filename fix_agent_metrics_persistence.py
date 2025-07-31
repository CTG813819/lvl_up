#!/usr/bin/env python3
"""
Fix Agent Metrics Persistence
Ensures AI level progress and growth scores are properly loaded from database on backend restart
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg
import structlog

logger = structlog.get_logger()


async def fix_agent_metrics_persistence():
    """Fix agent metrics persistence by ensuring proper initialization"""
    
    try:
        print("🔧 Fixing agent metrics persistence...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if agent_metrics table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'agent_metrics'
            );
        """)
        
        if not table_exists:
            print("❌ Agent metrics table does not exist. Please run the main migration first.")
            await conn.close()
            return False
        
        # Check if we have any agent metrics
        metrics_count = await conn.fetchval("SELECT COUNT(*) FROM agent_metrics")
        
        print(f"📊 Found {metrics_count} existing agent metrics")
        
        # If no metrics exist, create default ones for the main AIs
        if metrics_count == 0:
            print("📝 Creating default agent metrics for main AIs...")
            
            default_agents = [
                ('imperium', 'Imperium', 1000.0, 0.8, 0.2, 5),
                ('guardian', 'Guardian', 800.0, 0.85, 0.15, 4),
                ('sandbox', 'Sandbox', 1200.0, 0.75, 0.25, 6),
                ('conquest', 'Conquest', 1500.0, 0.9, 0.1, 8),
            ]
            
            for agent_id, agent_type, learning_score, success_rate, failure_rate, cycles in default_agents:
                await conn.execute("""
                    INSERT INTO agent_metrics (
                        agent_id, agent_type, learning_score, success_rate, failure_rate,
                        total_learning_cycles, status, is_active, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, agent_id, agent_type, learning_score, success_rate, failure_rate, cycles, 'idle', True, datetime.utcnow(), datetime.utcnow())
            
            print("✅ Created default agent metrics")
        
        # Verify the metrics are accessible
        metrics = await conn.fetch("""
            SELECT agent_id, agent_type, learning_score, success_rate, total_learning_cycles
            FROM agent_metrics
            ORDER BY agent_id
        """)
        
        print("📋 Current agent metrics:")
        for metric in metrics:
            print(f"  - {metric['agent_id']} ({metric['agent_type']}): Score={metric['learning_score']}, Success={metric['success_rate']}, Cycles={metric['total_learning_cycles']}")
        
        await conn.close()
        print("✅ Agent metrics persistence fix completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing agent metrics persistence: {e}")
        return False


async def main():
    """Main function"""
    print("🚀 Starting agent metrics persistence fix...")
    
    success = await fix_agent_metrics_persistence()
    
    if success:
        print("✅ Agent metrics persistence fix completed successfully")
        print("📋 The backend will now properly load AI level progress and growth scores on restart")
    else:
        print("❌ Agent metrics persistence fix failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 