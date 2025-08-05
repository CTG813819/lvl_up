#!/usr/bin/env python3
"""
Populate Sample XP Data for AIs
Adds realistic XP values to the agent_metrics table for better leaderboard display
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_session
from app.models.sql_models import AgentMetrics
from app.services.agent_metrics_service import AgentMetricsService
from sqlalchemy import select, update
import structlog

logger = structlog.get_logger()

class SampleXPDataPopulator:
    """Populate sample XP data for AIs"""
    
    def __init__(self):
        self.agent_metrics_service = AgentMetricsService()
        
    async def populate_sample_xp_data(self):
        """Populate realistic XP data for all AIs"""
        print("🎯 Populating Sample XP Data for AIs...")
        
        # Sample XP data for each AI type
        sample_data = {
            "imperium": {
                "custody_xp": 1250,
                "learning_score": 29.0,
                "total_tests_given": 15,
                "total_tests_passed": 12,
                "adversarial_wins": 8,
                "consecutive_successes": 5
            },
            "guardian": {
                "custody_xp": 2100,
                "learning_score": 1445.0,
                "total_tests_given": 22,
                "total_tests_passed": 18,
                "adversarial_wins": 12,
                "consecutive_successes": 7
            },
            "sandbox": {
                "custody_xp": 850,
                "learning_score": 979.0,
                "total_tests_given": 12,
                "total_tests_passed": 9,
                "adversarial_wins": 6,
                "consecutive_successes": 3
            },
            "conquest": {
                "custody_xp": 3200,
                "learning_score": 3105.0,
                "total_tests_given": 28,
                "total_tests_passed": 24,
                "adversarial_wins": 16,
                "consecutive_successes": 9
            }
        }
        
        try:
            # Initialize the service
            await self.agent_metrics_service.initialize()
            
            for ai_type, data in sample_data.items():
                print(f"📊 Updating {ai_type.upper()} with XP data...")
                
                # Calculate derived values
                custody_level = (data["custody_xp"] // 100) + 1
                pass_rate = (data["total_tests_passed"] / data["total_tests_given"]) if data["total_tests_given"] > 0 else 0.0
                win_rate = (data["adversarial_wins"] / data["total_tests_given"]) if data["total_tests_given"] > 0 else 0.0
                
                # Update the agent metrics
                success = await self.agent_metrics_service.update_specific_metrics(ai_type, {
                    "custody_xp": data["custody_xp"],
                    "custody_level": custody_level,
                    "learning_score": data["learning_score"],
                    "total_tests_given": data["total_tests_given"],
                    "total_tests_passed": data["total_tests_passed"],
                    "total_tests_failed": data["total_tests_given"] - data["total_tests_passed"],
                    "adversarial_wins": data["adversarial_wins"],
                    "consecutive_successes": data["consecutive_successes"],
                    "pass_rate": pass_rate,
                    "win_rate": win_rate,
                    "xp": data["custody_xp"],  # Sync with custody_xp
                    "level": custody_level,  # Sync with custody_level
                    "last_test_date": datetime.utcnow() - timedelta(hours=random.randint(1, 24))
                })
                
                if success:
                    print(f"✅ {ai_type.upper()}: XP={data['custody_xp']}, Level={custody_level}, Tests={data['total_tests_passed']}/{data['total_tests_given']}")
                else:
                    print(f"❌ Failed to update {ai_type.upper()}")
            
            print("\n🎉 Sample XP data populated successfully!")
            
            # Verify the data
            await self.verify_xp_data()
            
        except Exception as e:
            logger.error(f"Error populating sample XP data: {str(e)}")
            print(f"❌ Error: {str(e)}")
    
    async def verify_xp_data(self):
        """Verify that the XP data was populated correctly"""
        print("\n🔍 Verifying XP data...")
        
        try:
            all_metrics = await self.agent_metrics_service.get_all_agent_metrics()
            
            for ai_type, metrics in all_metrics.items():
                custody_xp = metrics.get('custody_xp', 0)
                custody_level = metrics.get('custody_level', 1)
                total_tests = metrics.get('total_tests_given', 0)
                total_passed = metrics.get('total_tests_passed', 0)
                adversarial_wins = metrics.get('adversarial_wins', 0)
                
                print(f"  {ai_type.upper()}:")
                print(f"    Custody XP: {custody_xp}")
                print(f"    Custody Level: {custody_level}")
                print(f"    Tests: {total_passed}/{total_tests} passed")
                print(f"    Adversarial Wins: {adversarial_wins}")
                print()
            
            print("✅ XP data verification complete!")
            
        except Exception as e:
            logger.error(f"Error verifying XP data: {str(e)}")
            print(f"❌ Verification error: {str(e)}")

async def main():
    """Main function"""
    print("🚀 Starting Sample XP Data Population...")
    
    populator = SampleXPDataPopulator()
    await populator.populate_sample_xp_data()
    
    print("\n🎯 Sample XP data population completed!")

if __name__ == "__main__":
    asyncio.run(main()) 