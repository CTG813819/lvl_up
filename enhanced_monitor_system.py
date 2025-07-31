#!/usr/bin/env python3
"""
Enhanced Data Persistence and Custodes Testing Monitoring Script
==============================================================

This script monitors the enhanced system including:
- Metrics persistence
- Custodes testing schedule
- Dynamic test categories
- Unified leveling system
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg

async def check_enhanced_metrics_persistence():
    """Check enhanced metrics persistence"""
    try:
        print("Checking enhanced metrics persistence...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check all AI types with enhanced persistence
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            # Check if metrics exist with enhanced persistence
            metrics = await conn.fetchrow("""
                SELECT agent_id, learning_score, level, xp, total_learning_cycles, prestige,
                       last_persistence_check, persistence_version, backup_created
                FROM agent_metrics 
                WHERE agent_id = $1 OR agent_type = $1
            """, ai_type)
            
            if metrics:
                print(f"{ai_type}: Level {metrics['level']}, Score {metrics['learning_score']:.2f}, XP {metrics['xp']}, Cycles {metrics['total_learning_cycles']}")
                print(f"  Persistence: v{metrics['persistence_version']}, Last check: {metrics['last_persistence_check']}")
            else:
                print(f"{ai_type}: No metrics found - creating enhanced default")
                # Create enhanced metrics
                await conn.execute("""
                    INSERT INTO agent_metrics (
                        id, agent_id, agent_type, learning_score, success_rate, 
                        failure_rate, total_learning_cycles, xp, level, prestige,
                        status, is_active, priority, created_at, updated_at,
                        last_persistence_check, persistence_version, backup_created
                    ) VALUES (
                        gen_random_uuid(), $1, $1, 0.0, 0.0, 0.0, 0, 0, 1, 0, 
                        'idle', true, 'medium', NOW(), NOW(), NOW(), '2.0', true
                    )
                """, ai_type)
                print(f"Created enhanced metrics for {ai_type}")
        
        # Check backup table
        backup_count = await conn.fetchval("SELECT COUNT(*) FROM agent_metrics_backup")
        print(f"Backup records: {backup_count}")
        
        await conn.close()
        print("Enhanced metrics persistence check completed")
        
    except Exception as e:
        print(f"Error checking enhanced metrics persistence: {str(e)}")

async def check_custodes_testing_schedule():
    """Check Custodes testing schedule configuration"""
    try:
        print("Checking Custodes testing schedule...")
        
        # Load schedule configuration
        if os.path.exists('enhanced_custodes_schedule.json'):
            with open('enhanced_custodes_schedule.json', 'r') as f:
                schedule = json.load(f)
            
            print("Custodes testing schedule:")
            print(f"  Main testing: {schedule['custodes_testing_schedule']['main_testing']['interval']}")
            print(f"  Comprehensive testing: {schedule['custodes_testing_schedule']['comprehensive_testing']['schedule']}")
            print(f"  Dynamic testing: {schedule['custodes_testing_schedule']['dynamic_testing']['trigger']}")
            print(f"  Proposal gate: {schedule['custodes_testing_schedule']['proposal_gate']['requirement']}")
        else:
            print("Enhanced Custodes schedule not found")
        
    except Exception as e:
        print(f"Error checking Custodes testing schedule: {str(e)}")

async def check_dynamic_test_categories():
    """Check dynamic test category system"""
    try:
        print("Checking dynamic test category system...")
        
        # Load dynamic categories configuration
        if os.path.exists('dynamic_test_categories.json'):
            with open('dynamic_test_categories.json', 'r') as f:
                categories = json.load(f)
            
            print("Dynamic test categories:")
            for category, details in categories['category_generation']['base_categories'].items():
                print(f"  {category}: {details['growth_pattern']}")
        else:
            print("Dynamic test categories not found")
        
    except Exception as e:
        print(f"Error checking dynamic test categories: {str(e)}")

async def check_unified_leveling_system():
    """Check unified leveling system"""
    try:
        print("Checking unified leveling system...")
        
        # Load unified leveling configuration
        if os.path.exists('unified_leveling_system.json'):
            with open('unified_leveling_system.json', 'r') as f:
                leveling = json.load(f)
            
            print("Unified leveling system:")
            print(f"  Base thresholds: {len(leveling['leveling_system']['base_thresholds'])} levels")
            print(f"  Custodes integration: {leveling['leveling_system']['custodes_integration']['level_up_requirement']}")
            print(f"  Black Library integration: {len(leveling['leveling_system']['black_library_integration'])} components")
        else:
            print("Unified leveling system not found")
        
    except Exception as e:
        print(f"Error checking unified leveling system: {str(e)}")

async def create_comprehensive_backup():
    """Create comprehensive backup of all system data"""
    try:
        print("Creating comprehensive backup...")
        
        # Database connection details
        DATABASE_URL = "postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require"
        
        # Connect directly to the database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Get all metrics
        metrics = await conn.fetch("SELECT * FROM agent_metrics")
        
        # Get all backups
        backups = await conn.fetch("SELECT * FROM agent_metrics_backup")
        
        await conn.close()
        
        # Prepare comprehensive backup data
        comprehensive_backup = {
            "timestamp": datetime.now().isoformat(),
            "metrics": [],
            "backups": [],
            "configuration_files": {}
        }
        
        for metric in metrics:
            comprehensive_backup["metrics"].append({
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
                "updated_at": metric['updated_at'].isoformat() if metric['updated_at'] else None,
                "last_persistence_check": metric['last_persistence_check'].isoformat() if metric['last_persistence_check'] else None,
                "persistence_version": metric['persistence_version'],
                "backup_created": metric['backup_created']
            })
        
        for backup in backups:
            comprehensive_backup["backups"].append({
                "agent_id": backup['agent_id'],
                "learning_score": float(backup['learning_score']),
                "level": backup['level'],
                "xp": backup['xp'],
                "prestige": backup['prestige'],
                "total_learning_cycles": backup['total_learning_cycles'],
                "backup_timestamp": backup['backup_timestamp'].isoformat() if backup['backup_timestamp'] else None,
                "backup_reason": backup['backup_reason']
            })
        
        # Include configuration files
        config_files = [
            'enhanced_custodes_schedule.json',
            'dynamic_test_categories.json',
            'unified_leveling_system.json'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    comprehensive_backup["configuration_files"][config_file] = json.load(f)
        
        # Save comprehensive backup
        backup_filename = f"comprehensive_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_filename, 'w') as f:
            json.dump(comprehensive_backup, f, indent=2)
        
        print(f"Comprehensive backup created: {backup_filename}")
        
    except Exception as e:
        print(f"Error creating comprehensive backup: {str(e)}")

async def main():
    """Main function"""
    print("Starting enhanced system monitoring...")
    
    # Check all components
    await check_enhanced_metrics_persistence()
    await check_custodes_testing_schedule()
    await check_dynamic_test_categories()
    await check_unified_leveling_system()
    
    # Create comprehensive backup
    await create_comprehensive_backup()
    
    print("Enhanced system monitoring completed")

if __name__ == "__main__":
    asyncio.run(main())
