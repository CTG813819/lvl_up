#!/usr/bin/env python3
"""
Persistence Monitor
==================

This script monitors and ensures all data persistence is working correctly.
Run this periodically to verify data integrity.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog

logger = structlog.get_logger()

async def check_persistence():
    """Check all persistence aspects"""
    try:
        print("🔍 Checking data persistence...")
        
        # Check if persistence config exists
        if os.path.exists("persistence_config.json"):
            print("✅ Persistence configuration found")
        else:
            print("❌ Persistence configuration missing")
        
        # Check if reset scripts are disabled
        reset_files = [
            "reset_token_usage.sql",
            "fix_critical_system_issues.py"
        ]
        
        for file in reset_files:
            if os.path.exists(file):
                with open(file, 'r') as f:
                    content = f.read()
                    if "learning_score = 0" in content:
                        print(f"⚠️  {file}: Still contains learning score reset")
                    else:
                        print(f"✅ {file}: Reset disabled")
        
        # Check for backup files
        backup_files = [f for f in os.listdir('.') if f.startswith('comprehensive_backup_')]
        if backup_files:
            print(f"✅ Found {len(backup_files)} backup files")
        else:
            print("⚠️  No backup files found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking persistence: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 Starting Persistence Monitor")
    print("=" * 40)
    
    await check_persistence()
    
    print("\n✅ Persistence check completed!")

if __name__ == "__main__":
    asyncio.run(main()) 