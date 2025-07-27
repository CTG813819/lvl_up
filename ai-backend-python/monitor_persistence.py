#!/usr/bin/env python3
"""
Simple Data Persistence Monitoring Script
========================================

This script monitors and maintains data persistence to prevent metrics resetting.
Run this script periodically to ensure data integrity.
"""

import asyncio
import sys
import os
from datetime import datetime
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg

async def check_metrics_persistence():
    """Check if agent metrics are properly persisted"""
    try:
        print("Checking metrics persistence...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check all AI types
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            # Check if metrics exist for this AI type
            metrics = await conn.fetchrow("""
                SELECT agent_id, learning_score, level, xp, total_learning_cycles
                FROM agent_metrics 
                WHERE agent_id = $1 OR agent_type = $1
            """, ai_type)
            
            if metrics:
                print(f"{ai_type}: Level {metrics['level']}, Score {metrics['learning_score']:.2f}, XP {metrics['xp']}, Cycles {metrics['total_learning_cycles']}")
            else:
                print(f"{ai_type}: No metrics found - creating default")
                # Create default metrics
                await conn.execute("""
                    INSERT INTO agent_metrics (
                        id, agent_id, agent_type, learning_score, success_rate, 
                        failure_rate, total_learning_cycles, xp, level, prestige,
                        status, is_active, priority, created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), $1, $1, 0.0, 0.0, 0.0, 0, 0, 1, 0, 
                        'idle', true, 'medium', NOW(), NOW()
                    )
                """, ai_type)
                print(f"Created default metrics for {ai_type}")
        
        await conn.close()
        print("Metrics persistence check completed")
        
    except Exception as e:
        print(f"Error checking metrics persistence: {str(e)}")

async def backup_metrics_data():
    """Create backup of metrics data"""
    try:
        print("Creating metrics backup...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Get all metrics
        metrics = await conn.fetch("SELECT * FROM agent_metrics")
        
        backup_data = []
        for metric in metrics:
            backup_data.append({
                "agent_id": metric['agent_id'],
                "agent_type": metric['agent_type'],
                "learning_score": float(metric['learning_score']),
                "success_rate": float(metric['success_rate']),
                "failure_rate": float(metric['failure_rate']),
                "total_learning_cycles": metric['total_learning_cycles'],
                "xp": metric['xp'],
                "level": metric['level'],
                "prestige": metric['prestige'],
                "status": metric['status'],
                "is_active": metric['is_active'],
                "priority": metric['priority'],
                "created_at": metric['created_at'].isoformat() if metric['created_at'] else None,
                "updated_at": metric['updated_at'].isoformat() if metric['updated_at'] else None
            })
        
        await conn.close()
        
        # Save backup to file
        backup_filename = f"metrics_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_filename, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"Metrics backup created: {backup_filename}")
        
    except Exception as e:
        print(f"Error creating metrics backup: {str(e)}")

async def main():
    """Main function"""
    print("Starting data persistence monitoring...")
    
    # Check metrics persistence
    await check_metrics_persistence()
    
    # Create backup
    await backup_metrics_data()
    
    print("Data persistence monitoring completed")

if __name__ == "__main__":
    asyncio.run(main())
