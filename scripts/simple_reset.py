#!/usr/bin/env python3
"""
Simple Reset Script
Directly resets custody metrics in the running system
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def reset_custody_metrics():
    """Reset custody metrics by directly modifying the metrics file"""
    print("🔄 Starting simple custody level reset...")
    
    try:
        # Path to custody metrics file
        metrics_file = "/home/ubuntu/ai-backend-python/custody_metrics.json"
        
        # Default metrics for all AIs
        default_metrics = {
            "guardian": {
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
            },
            "imperium": {
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
            },
            "sandbox": {
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
            },
            "conquest": {
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
            },
            "sandbox_agent": {
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
            },
            "imperium_agent": {
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
            },
            "guardian_agent": {
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
        }
        
        # Write the reset metrics to file
        with open(metrics_file, 'w') as f:
            json.dump(default_metrics, f, indent=2, default=str)
        
        print(f"✅ Successfully reset custody metrics to file: {metrics_file}")
        print("\n📋 Reset Summary:")
        print("- All AIs set to Level 1")
        print("- All XP reset to 0")
        print("- All test counts reset to 0")
        print("- All learning cycles reset to 0")
        print("- All consecutive counts reset to 0")
        
        # Display current state
        print("\n📊 Current State:")
        for ai_type, metrics in default_metrics.items():
            print(f"  {ai_type}: Level {metrics['custody_level']}, XP {metrics['custody_xp']}, Tests {metrics['total_tests_passed']}/{metrics['total_tests_given']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting custody levels: {str(e)}")
        return False

async def main():
    """Main function"""
    await reset_custody_metrics()

if __name__ == "__main__":
    asyncio.run(main()) 