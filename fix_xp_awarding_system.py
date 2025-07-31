#!/usr/bin/env python3
"""
Fix XP Awarding System
======================

This script fixes the XP awarding and persistence issues for all test types:
- Custody tests
- Collaborative tests  
- Olympic tests

The system ensures AIs get XP and it's properly persisted to the Neon database.
"""

import asyncio
import sys
import os
from datetime import datetime
import json
from typing import Dict, List, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import structlog
from app.core.database import get_session
from app.models.sql_models import AgentMetrics
from sqlalchemy import select
from app.services.custody_protocol_service import CustodyProtocolService

logger = structlog.get_logger()

class XPAwardingSystem:
    """Comprehensive XP awarding system for all test types"""
    
    def __init__(self):
        self.custody_service = None
        
    async def initialize(self):
        """Initialize the XP awarding system"""
        try:
            self.custody_service = await CustodyProtocolService.initialize()
            logger.info("✅ XP Awarding System initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Error initializing XP Awarding System: {e}")
            return False
    
    async def award_xp_for_test(self, ai_type: str, test_result: Dict, test_type: str = "custody"):
        """Award XP for any test type and persist to database"""
        try:
            logger.info(f"[XP AWARD] Awarding XP for {ai_type} - Test Type: {test_type}")
            
            # Get current metrics from database
            custody_metrics = await self.custody_service.agent_metrics_service.get_custody_metrics(ai_type)
            if not custody_metrics:
                custody_metrics = {
                    "total_tests_given": 0,
                    "total_tests_passed": 0,
                    "total_tests_failed": 0,
                    "current_difficulty": "basic",
                    "last_test_date": None,
                    "consecutive_failures": 0,
                    "consecutive_successes": 0,
                    "test_history": [],
                    "custody_level": 1,
                    "custody_xp": 0,
                    "xp": 0,
                    "level": 1,
                    "learning_score": 0.0
                }
            
            # Calculate XP based on test type and result
            xp_awarded = 0
            base_xp = 0
            
            if test_type == "custody":
                if test_result.get("passed", False):
                    base_xp = 50
                    custody_metrics["total_tests_passed"] += 1
                    custody_metrics["consecutive_successes"] += 1
                    custody_metrics["consecutive_failures"] = 0
                else:
                    base_xp = 1  # Small XP for attempting
                    custody_metrics["total_tests_failed"] += 1
                    custody_metrics["consecutive_failures"] += 1
                    custody_metrics["consecutive_successes"] = 0
                    
            elif test_type == "collaborative":
                if test_result.get("passed", False):
                    base_xp = 75  # Higher XP for collaborative success
                    custody_metrics["total_tests_passed"] += 1
                    custody_metrics["consecutive_successes"] += 1
                    custody_metrics["consecutive_failures"] = 0
                else:
                    base_xp = 5  # Small XP for attempting collaboration
                    custody_metrics["total_tests_failed"] += 1
                    custody_metrics["consecutive_failures"] += 1
                    custody_metrics["consecutive_successes"] = 0
                    
            elif test_type == "olympic":
                if test_result.get("passed", False):
                    base_xp = 100  # Highest XP for olympic success
                    custody_metrics["total_tests_passed"] += 1
                    custody_metrics["consecutive_successes"] += 1
                    custody_metrics["consecutive_failures"] = 0
                else:
                    base_xp = 10  # Small XP for attempting olympic
                    custody_metrics["total_tests_failed"] += 1
                    custody_metrics["consecutive_failures"] += 1
                    custody_metrics["consecutive_successes"] = 0
            
            # Apply difficulty multiplier
            difficulty = test_result.get("difficulty", "basic")
            difficulty_multipliers = {
                "basic": 1.0,
                "intermediate": 1.5,
                "advanced": 2.0,
                "expert": 2.5,
                "master": 3.0,
                "legendary": 4.0
            }
            difficulty_multiplier = difficulty_multipliers.get(difficulty, 1.0)
            
            # Apply score multiplier
            score = test_result.get("score", 0)
            score_multiplier = score / 100.0 if score > 0 else 0.5
            
            # Calculate final XP
            xp_awarded = int(base_xp * difficulty_multiplier * score_multiplier)
            
            # Update metrics
            custody_metrics["custody_xp"] += xp_awarded
            custody_metrics["learning_score"] += xp_awarded
            custody_metrics["total_tests_given"] += 1
            custody_metrics["last_test_date"] = datetime.utcnow()
            
            # Update level based on XP
            new_level = (custody_metrics["custody_xp"] // 100) + 1
            if new_level > custody_metrics["custody_level"]:
                custody_metrics["custody_level"] = new_level
                logger.info(f"[XP AWARD] {ai_type} leveled up to level {new_level}!")
            
            # Add test history entry
            test_history_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "test_type": test_type,
                "passed": test_result.get("passed", False),
                "score": score,
                "xp_awarded": xp_awarded,
                "difficulty": difficulty
            }
            custody_metrics["test_history"].append(test_history_entry)
            
            # Persist to database
            await self.custody_service.agent_metrics_service.create_or_update_agent_metrics(ai_type, custody_metrics)
            
            logger.info(f"[XP AWARD] {ai_type} awarded {xp_awarded} XP for {test_type} test (Score: {score}, Difficulty: {difficulty})")
            return xp_awarded
            
        except Exception as e:
            logger.error(f"[XP AWARD] Error awarding XP for {ai_type}: {str(e)}")
            return 0
    
    async def run_custody_test_with_xp(self, ai_type: str):
        """Run custody test and award XP"""
        try:
            logger.info(f"[CUSTODY TEST] Running custody test for {ai_type}")
            
            # Run the custody test
            test_result = await self.custody_service.administer_custody_test(ai_type)
            
            # Award XP for the test
            xp_awarded = await self.award_xp_for_test(ai_type, test_result, "custody")
            
            logger.info(f"[CUSTODY TEST] {ai_type} completed custody test - XP awarded: {xp_awarded}")
            return test_result, xp_awarded
            
        except Exception as e:
            logger.error(f"[CUSTODY TEST] Error running custody test for {ai_type}: {str(e)}")
            return None, 0
    
    async def run_collaborative_test_with_xp(self, participants: list):
        """Run collaborative test and award XP"""
        try:
            logger.info(f"[COLLABORATIVE TEST] Running collaborative test for {participants}")
            
            # Run the collaborative test
            test_result = await self.custody_service._execute_collaborative_test(participants, "Collaborative scenario", {})
            
            # Award XP for each participant
            total_xp_awarded = 0
            for ai_type in participants:
                xp_awarded = await self.award_xp_for_test(ai_type, test_result, "collaborative")
                total_xp_awarded += xp_awarded
            
            logger.info(f"[COLLABORATIVE TEST] Collaborative test completed - Total XP awarded: {total_xp_awarded}")
            return test_result, total_xp_awarded
            
        except Exception as e:
            logger.error(f"[COLLABORATIVE TEST] Error running collaborative test: {str(e)}")
            return None, 0
    
    async def run_olympic_test_with_xp(self, participants: list):
        """Run olympic test and award XP"""
        try:
            logger.info(f"[OLYMPIC TEST] Running olympic test for {participants}")
            
            # Run the olympic test
            from app.services.custody_protocol_service import TestDifficulty
            test_result = await self.custody_service.administer_olympic_event(participants, TestDifficulty.INTERMEDIATE)
            
            # Award XP for each participant
            total_xp_awarded = 0
            for ai_type in participants:
                xp_awarded = await self.award_xp_for_test(ai_type, test_result, "olympic")
                total_xp_awarded += xp_awarded
            
            logger.info(f"[OLYMPIC TEST] Olympic test completed - Total XP awarded: {total_xp_awarded}")
            return test_result, total_xp_awarded
            
        except Exception as e:
            logger.error(f"[OLYMPIC TEST] Error running olympic test: {str(e)}")
            return None, 0
    
    async def check_current_xp(self):
        """Check current XP for all AIs"""
        try:
            logger.info("[XP CHECK] Checking current XP for all AIs")
            
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            for ai_type in ai_types:
                custody_metrics = await self.custody_service.agent_metrics_service.get_custody_metrics(ai_type)
                
                if custody_metrics:
                    xp = custody_metrics.get("custody_xp", 0)
                    level = custody_metrics.get("custody_level", 1)
                    total_tests = custody_metrics.get("total_tests_given", 0)
                    passed_tests = custody_metrics.get("total_tests_passed", 0)
                    
                    logger.info(f"[XP CHECK] {ai_type}: Level {level}, XP {xp}, Tests {passed_tests}/{total_tests}")
                else:
                    logger.warning(f"[XP CHECK] {ai_type}: No metrics found")
            
        except Exception as e:
            logger.error(f"[XP CHECK] Error checking XP: {str(e)}")

async def main():
    """Main function to test the XP awarding system"""
    try:
        print("🚀 Starting XP Awarding System Fix")
        
        # Initialize the system
        xp_system = XPAwardingSystem()
        success = await xp_system.initialize()
        
        if not success:
            print("❌ Failed to initialize XP Awarding System")
            return
        
        # Check current XP
        await xp_system.check_current_xp()
        
        # Run tests for all AIs
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        print("\n🧪 Running custody tests...")
        for ai_type in ai_types:
            test_result, xp_awarded = await xp_system.run_custody_test_with_xp(ai_type)
            if xp_awarded > 0:
                print(f"✅ {ai_type}: Custody test completed - {xp_awarded} XP awarded")
            else:
                print(f"❌ {ai_type}: Custody test failed")
        
        print("\n🤝 Running collaborative tests...")
        collaborative_groups = [
            ["imperium", "guardian"],
            ["sandbox", "conquest"]
        ]
        
        for group in collaborative_groups:
            test_result, xp_awarded = await xp_system.run_collaborative_test_with_xp(group)
            if xp_awarded > 0:
                print(f"✅ Collaborative test completed - {xp_awarded} XP awarded")
            else:
                print(f"❌ Collaborative test failed")
        
        print("\n🏆 Running olympic tests...")
        olympic_groups = [
            ["imperium", "guardian", "sandbox"],
            ["conquest", "imperium", "guardian"]
        ]
        
        for group in olympic_groups:
            test_result, xp_awarded = await xp_system.run_olympic_test_with_xp(group)
            if xp_awarded > 0:
                print(f"✅ Olympic test completed - {xp_awarded} XP awarded")
            else:
                print(f"❌ Olympic test failed")
        
        # Check final XP
        print("\n📊 Final XP Status:")
        await xp_system.check_current_xp()
        
        print("\n✅ XP Awarding System Fix completed!")
        
    except Exception as e:
        print(f"❌ Error in XP Awarding System Fix: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())