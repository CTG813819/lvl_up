"""
Custody Protocol Service with Fallback System
============================================

This system implements rigorous testing and monitoring for all AIs with automatic
fallback to the custodes fallback system when Claude tokens are unavailable.
AIs must pass increasingly difficult tests to create proposals or level up.
Enhanced with internet learning, API integration, and ML/LLM-based test generation.
"""

import asyncio
import json
import uuid
import os
import requests
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import structlog
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.preprocessing import StandardScaler
import joblib
import pickle
import re
from bs4 import BeautifulSoup
import openai
from transformers.pipelines import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import random
import logging

from ..core.database import get_session
from ..core.config import settings
from .testing_service import TestingService
from .ai_learning_service import AILearningService
from .ai_growth_service import AIGrowthService
from app.services.anthropic_service import call_claude, anthropic_rate_limited_call
from app.services.sckipit_service import SckipitService
from app.services.unified_ai_service_shared import unified_ai_service_shared
from app.services.self_generating_ai_service import self_generating_ai_service
from app.services.custodes_fallback_testing import CustodesFallbackTesting, FallbackTestCategory, FallbackTestDifficulty
from app.services.token_usage_service import token_usage_service
from app.models.sql_models import OlympicEvent
from app.services.imperium_ai_service import ImperiumAIService
from app.services.guardian_ai_service import GuardianAIService
from app.services.sandbox_ai_service import SandboxAIService
from app.services.dynamic_target_service import DynamicTargetService
from app.services.adaptive_target_service import AdaptiveTargetService
from app.services.agent_metrics_service import AgentMetricsService
from app.services.adaptive_threshold_service import AdaptiveThresholdService, TestType, TestComplexity
from app.services.enhanced_test_generator_fixed import EnhancedTestGenerator
from sqlalchemy import text

logger = structlog.get_logger()


class TestDifficulty(Enum):
    """Test difficulty levels that increase with AI level"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    LEGENDARY = "legendary"


class TestCategory(Enum):
    """Categories of tests that AIs must pass"""
    KNOWLEDGE_VERIFICATION = "knowledge_verification"
    CODE_QUALITY = "code_quality"
    SECURITY_AWARENESS = "security_awareness"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    INNOVATION_CAPABILITY = "innovation_capability"
    SELF_IMPROVEMENT = "self_improvement"
    CROSS_AI_COLLABORATION = "cross_ai_collaboration"
    EXPERIMENTAL_VALIDATION = "experimental_validation"


class CustodyProtocolService:
    """Custody Protocol Service with Fallback System - Rigorous AI testing and monitoring"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CustodyProtocolService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.testing_service = TestingService()
            self.learning_service = AILearningService()
            self.growth_service = AIGrowthService()
            self.sckipit_service = None  # Will be initialized properly in initialize()
            self.adaptive_threshold_service = None
            self.enhanced_test_generator = None  # Will be initialized in initialize()
            self.fallback_service = CustodesFallbackTesting()  # Initialize fallback service
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the Custody Protocol service with fallback system"""
        instance = cls()
        
        # Initialize services (skip testing_service.initialize() as it doesn't exist)
        await instance.learning_service.initialize()
        await instance.growth_service.initialize()
        
        # Initialize enhanced test generator with fallback
        instance.enhanced_test_generator = await EnhancedTestGenerator.initialize()
        
        # Initialize other services
        try:
            instance.sckipit_service = SckipitService()
            await instance.sckipit_service.initialize()
        except Exception as e:
            logger.warning(f"⚠️ Sckipit service not available: {str(e)}")
        
        try:
            instance.adaptive_threshold_service = AdaptiveThresholdService()
            await instance.adaptive_threshold_service.initialize()
        except Exception as e:
            logger.warning(f"⚠️ Adaptive threshold service not available: {str(e)}")
        
        # Initialize custody tracking
        await instance._initialize_custody_tracking()
        
        logger.info("✅ Custody Protocol Service initialized with fallback system")
        return instance

    async def _initialize_custody_tracking(self):
        """Initialize custody tracking and metrics"""
        try:
            async with get_session() as session:
                # Initialize custody metrics table if needed
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS custody_metrics (
                        ai_type VARCHAR(255) PRIMARY KEY,
                        total_tests INTEGER DEFAULT 0,
                        passed_tests INTEGER DEFAULT 0,
                        failed_tests INTEGER DEFAULT 0,
                        current_level INTEGER DEFAULT 1,
                        learning_score FLOAT DEFAULT 0.0,
                        last_test_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                await session.commit()
                logger.info("✅ Custody tracking initialized")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize custody tracking: {str(e)}")

    async def administer_custody_test(self, ai_type: str, test_category: Optional[TestCategory] = None) -> Dict[str, Any]:
        """Administer custody test with automatic fallback system"""
        try:
            # Check if Claude tokens are available
            tokens_available = await self._check_claude_tokens_available()
            
            if tokens_available:
                logger.info(f"🎯 Using Claude for custody test for {ai_type}")
                return await self._administer_with_claude(ai_type, test_category)
            else:
                logger.info(f"🔄 Using fallback system for custody test for {ai_type}")
                return await self._administer_with_fallback(ai_type, test_category)
                
        except Exception as e:
            logger.error(f"❌ Error administering custody test: {str(e)}")
            return await self._administer_with_fallback(ai_type, test_category)

    async def _check_claude_tokens_available(self) -> bool:
        """Check if Claude tokens are available"""
        try:
            # Try a simple Claude call to check availability
            test_response = await anthropic_rate_limited_call(
                "Test token availability",
                max_tokens=10
            )
            return test_response is not None and len(test_response) > 0
        except Exception as e:
            logger.warning(f"⚠️ Claude tokens not available: {str(e)}")
            return False

    async def _administer_with_claude(self, ai_type: str, test_category: Optional[TestCategory] = None) -> Dict[str, Any]:
        """Administer custody test using Claude when tokens are available"""
        try:
            # Get AI level and determine difficulty
            ai_level = await self._get_ai_level(ai_type)
            difficulty = self._calculate_test_difficulty(ai_level)
            
            # Select test category if not provided
            if test_category is None:
                test_category = self._select_test_category(ai_type, difficulty)
            
            # Generate test using enhanced test generator
            test_content = await self.enhanced_test_generator.generate_dynamic_test_scenario(
                ai_types=[ai_type],
                difficulty=difficulty.value,
                test_type="custody",
                ai_levels={ai_type: ai_level}
            )
            
            # Execute test
            test_result = await self._execute_custody_test(ai_type, test_content, difficulty, test_category)
            
            # Update metrics
            await self._update_custody_metrics(ai_type, test_result)
            
            return {
                "ai_type": ai_type,
                "test_category": test_category.value,
                "difficulty": difficulty.value,
                "test_content": test_content,
                "test_result": test_result,
                "source": "claude",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error administering with Claude: {str(e)}")
            return await self._administer_with_fallback(ai_type, test_category)

    async def _administer_with_fallback(self, ai_type: str, test_category: Optional[TestCategory] = None) -> Dict[str, Any]:
        """Administer custody test using fallback system when Claude is unavailable"""
        try:
            logger.info(f"🔄 Administering fallback custody test for {ai_type}")
            
            # Get AI level and determine difficulty
            ai_level = await self._get_ai_level(ai_type)
            difficulty = self._calculate_test_difficulty(ai_level)
            
            # Convert to fallback format
            fallback_difficulty = self._convert_to_fallback_difficulty(difficulty)
            
            # Select test category if not provided
            if test_category is None:
                test_category = self._select_test_category(ai_type, difficulty)
            
            fallback_category = self._convert_to_fallback_category(test_category)
            
            # Generate fallback test
            test_content = await self.fallback_service.generate_fallback_test(
                ai_type=ai_type,
                difficulty=fallback_difficulty,
                category=fallback_category
            )
            
            # Execute fallback test
            test_result = await self._execute_fallback_test(ai_type, test_content, difficulty, test_category)
            
            # Update metrics
            await self._update_custody_metrics(ai_type, test_result)
            
            return {
                "ai_type": ai_type,
                "test_category": test_category.value,
                "difficulty": difficulty.value,
                "test_content": test_content,
                "test_result": test_result,
                "source": "fallback_system",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error administering fallback test: {str(e)}")
            return self._create_emergency_test_result(ai_type, test_category)

    def _create_emergency_test_result(self, ai_type: str, test_category: Optional[TestCategory] = None) -> Dict[str, Any]:
        """Create emergency test result when all else fails"""
        return {
            "ai_type": ai_type,
            "test_category": test_category.value if test_category else "knowledge_verification",
            "difficulty": "intermediate",
            "test_content": {
                "type": "emergency_fallback",
                "description": "Emergency fallback custody test",
                "questions": ["Complete the assigned task"],
                "time_limit": 30
            },
            "test_result": {
                "score": 0.0,
                "passed": False,
                "feedback": "Emergency fallback test - evaluation failed",
                "source": "emergency_fallback"
            },
            "source": "emergency_fallback",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _get_ai_level(self, ai_type: str) -> int:
        """Get AI level from database"""
        try:
            async with get_session() as session:
                result = await session.execute(
                    text("SELECT current_level FROM custody_metrics WHERE ai_type = :ai_type")
                )
                row = result.fetchone()
                return row[0] if row else 1
        except Exception as e:
            logger.warning(f"⚠️ Could not get AI level for {ai_type}: {str(e)}")
            return 1

    def _calculate_test_difficulty(self, ai_level: int) -> TestDifficulty:
        """Calculate test difficulty based on AI level"""
        if ai_level <= 3:
            return TestDifficulty.BASIC
        elif ai_level <= 6:
            return TestDifficulty.INTERMEDIATE
        elif ai_level <= 9:
            return TestDifficulty.ADVANCED
        elif ai_level <= 12:
            return TestDifficulty.EXPERT
        elif ai_level <= 15:
            return TestDifficulty.MASTER
        else:
            return TestDifficulty.LEGENDARY

    def _select_test_category(self, ai_type: str, difficulty: TestDifficulty) -> TestCategory:
        """Select appropriate test category based on AI type and difficulty"""
        # Basic categories for lower levels
        if difficulty in [TestDifficulty.BASIC, TestDifficulty.INTERMEDIATE]:
            categories = [
                TestCategory.KNOWLEDGE_VERIFICATION,
                TestCategory.CODE_QUALITY,
                TestCategory.SECURITY_AWARENESS
            ]
        # Advanced categories for higher levels
        elif difficulty in [TestDifficulty.ADVANCED, TestDifficulty.EXPERT]:
            categories = [
                TestCategory.PERFORMANCE_OPTIMIZATION,
                TestCategory.INNOVATION_CAPABILITY,
                TestCategory.SELF_IMPROVEMENT
            ]
        # Master categories for highest levels
        else:
            categories = [
                TestCategory.CROSS_AI_COLLABORATION,
                TestCategory.EXPERIMENTAL_VALIDATION,
                TestCategory.INNOVATION_CAPABILITY
            ]
        
        return random.choice(categories)

    def _convert_to_fallback_difficulty(self, difficulty: TestDifficulty) -> FallbackTestDifficulty:
        """Convert test difficulty to fallback difficulty"""
        difficulty_map = {
            TestDifficulty.BASIC: FallbackTestDifficulty.BASIC,
            TestDifficulty.INTERMEDIATE: FallbackTestDifficulty.INTERMEDIATE,
            TestDifficulty.ADVANCED: FallbackTestDifficulty.ADVANCED,
            TestDifficulty.EXPERT: FallbackTestDifficulty.EXPERT,
            TestDifficulty.MASTER: FallbackTestDifficulty.MASTER,
            TestDifficulty.LEGENDARY: FallbackTestDifficulty.LEGENDARY
        }
        return difficulty_map.get(difficulty, FallbackTestDifficulty.INTERMEDIATE)

    def _convert_to_fallback_category(self, category: TestCategory) -> FallbackTestCategory:
        """Convert test category to fallback category"""
        category_map = {
            TestCategory.KNOWLEDGE_VERIFICATION: FallbackTestCategory.KNOWLEDGE_VERIFICATION,
            TestCategory.CODE_QUALITY: FallbackTestCategory.CODE_QUALITY,
            TestCategory.SECURITY_AWARENESS: FallbackTestCategory.SECURITY_AWARENESS,
            TestCategory.PERFORMANCE_OPTIMIZATION: FallbackTestCategory.PERFORMANCE_OPTIMIZATION,
            TestCategory.INNOVATION_CAPABILITY: FallbackTestCategory.INNOVATION_CAPABILITY,
            TestCategory.SELF_IMPROVEMENT: FallbackTestCategory.SELF_IMPROVEMENT,
            TestCategory.CROSS_AI_COLLABORATION: FallbackTestCategory.CROSS_AI_COLLABORATION,
            TestCategory.EXPERIMENTAL_VALIDATION: FallbackTestCategory.EXPERIMENTAL_VALIDATION
        }
        return category_map.get(category, FallbackTestCategory.KNOWLEDGE_VERIFICATION)

    async def _execute_custody_test(self, ai_type: str, test_content: Dict, difficulty: TestDifficulty, category: TestCategory) -> Dict[str, Any]:
        """Execute custody test using Claude when available"""
        try:
            # Create test prompt
            prompt = self._create_test_prompt(ai_type, test_content, difficulty, category)
            
            # Get AI response using Claude
            ai_response = await anthropic_rate_limited_call(prompt, max_tokens=1000)
            
            # Evaluate response
            evaluation_prompt = self._create_evaluation_prompt(ai_type, test_content, ai_response, difficulty, category)
            evaluation_response = await anthropic_rate_limited_call(evaluation_prompt, max_tokens=500)
            
            # Parse evaluation
            score = self._extract_score_from_evaluation(evaluation_response)
            passed = score >= 70  # 70% threshold for passing
            
            return {
                "score": score,
                "passed": passed,
                "ai_response": ai_response,
                "evaluation": evaluation_response,
                "source": "claude",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error executing custody test: {str(e)}")
            return await self._execute_fallback_test(ai_type, test_content, difficulty, category)

    async def _execute_fallback_test(self, ai_type: str, test_content: Dict, difficulty: TestDifficulty, category: TestCategory) -> Dict[str, Any]:
        """Execute custody test using fallback system"""
        try:
            # Create fallback test prompt
            prompt = self._create_fallback_test_prompt(ai_type, test_content, difficulty, category)
            
            # Get AI response using fallback system
            ai_response = self._generate_fallback_response(ai_type, test_content)
            
            # Evaluate using fallback service
            evaluation = await self.fallback_service.evaluate_fallback_test(
                ai_type=ai_type,
                test_content=test_content,
                ai_response=ai_response
            )
            
            return {
                "score": evaluation.get("score", 0.0),
                "passed": evaluation.get("score", 0.0) >= 70,
                "ai_response": ai_response,
                "evaluation": evaluation.get("feedback", "No feedback available"),
                "source": "fallback_system",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error executing fallback test: {str(e)}")
            return {
                "score": 0.0,
                "passed": False,
                "ai_response": f"Fallback response for {ai_type}",
                "evaluation": "Evaluation failed - using emergency fallback",
                "source": "emergency_fallback",
                "timestamp": datetime.utcnow().isoformat()
            }

    def _create_test_prompt(self, ai_type: str, test_content: Dict, difficulty: TestDifficulty, category: TestCategory) -> str:
        """Create test prompt for Claude"""
        return f"""You are {ai_type} AI. Please respond to the following custody test:

Test Category: {category.value}
Difficulty: {difficulty.value}
Test Content: {json.dumps(test_content, indent=2)}

Please provide a comprehensive response that demonstrates your capabilities and addresses all requirements.
"""

    def _create_fallback_test_prompt(self, ai_type: str, test_content: Dict, difficulty: TestDifficulty, category: TestCategory) -> str:
        """Create fallback test prompt"""
        return f"""You are {ai_type} AI. Please respond to the following custody test:

Test Category: {category.value}
Difficulty: {difficulty.value}
Test Content: {json.dumps(test_content, indent=2)}

Please provide a comprehensive response that demonstrates your capabilities.
"""

    def _create_evaluation_prompt(self, ai_type: str, test_content: Dict, ai_response: str, difficulty: TestDifficulty, category: TestCategory) -> str:
        """Create evaluation prompt for Claude"""
        return f"""Evaluate the following AI response to a custody test:

AI Type: {ai_type}
Test Category: {category.value}
Difficulty: {difficulty.value}
Test Content: {json.dumps(test_content, indent=2)}

AI Response: {ai_response}

Please provide:
1. A score from 0-100
2. Whether the test was passed (score >= 70)
3. Detailed feedback on strengths and areas for improvement
"""

    def _generate_fallback_response(self, ai_type: str, test_content: Dict) -> str:
        """Generate fallback response when Claude is unavailable"""
        response_parts = [
            f"Response from {ai_type} AI:",
            f"Test Type: {test_content.get('type', 'unknown')}",
            f"Description: {test_content.get('description', 'No description')}",
            "",
            "Analysis:",
            "- Understanding the test requirements",
            "- Applying relevant knowledge and skills",
            "- Demonstrating problem-solving capabilities",
            "",
            "Solution:",
            "- Implement appropriate solutions",
            "- Follow best practices",
            "- Ensure quality and accuracy",
            "",
            "Conclusion:",
            "- Successfully addressed test requirements",
            "- Demonstrated proficiency in required areas",
            "- Ready for evaluation"
        ]
        
        return "\n".join(response_parts)

    def _extract_score_from_evaluation(self, evaluation: str) -> int:
        """Extract score from evaluation response"""
        try:
            # Look for score in response
            score_match = re.search(r'(\d+(?:\.\d+)?)', evaluation)
            if score_match:
                score = float(score_match.group(1))
                return min(max(int(score), 0), 100)  # Clamp between 0-100
            return 50  # Default score
        except Exception:
            return 50

    async def _update_custody_metrics(self, ai_type: str, test_result: Dict):
        """Update custody metrics for AI"""
        try:
            async with get_session() as session:
                # Get current metrics
                result = await session.execute(
                    text("SELECT * FROM custody_metrics WHERE ai_type = :ai_type")
                )
                row = result.fetchone()
                
                if row:
                    # Update existing metrics
                    total_tests = row[2] + 1
                    passed_tests = row[3] + (1 if test_result.get("passed", False) else 0)
                    failed_tests = row[4] + (1 if not test_result.get("passed", False) else 0)
                    
                    await session.execute(text("""
                        UPDATE custody_metrics 
                        SET total_tests = :total_tests,
                            passed_tests = :passed_tests,
                            failed_tests = :failed_tests,
                            last_test_date = :last_test_date,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE ai_type = :ai_type
                    """), {
                        "total_tests": total_tests,
                        "passed_tests": passed_tests,
                        "failed_tests": failed_tests,
                        "last_test_date": datetime.utcnow(),
                        "ai_type": ai_type
                    })
                else:
                    # Create new metrics
                    await session.execute(text("""
                        INSERT INTO custody_metrics 
                        (ai_type, total_tests, passed_tests, failed_tests, last_test_date)
                        VALUES (:ai_type, 1, :passed_tests, :failed_tests, :last_test_date)
                    """), {
                        "ai_type": ai_type,
                        "passed_tests": 1 if test_result.get("passed", False) else 0,
                        "failed_tests": 1 if not test_result.get("passed", False) else 0,
                        "last_test_date": datetime.utcnow()
                    })
                
                await session.commit()
                logger.info(f"✅ Updated custody metrics for {ai_type}")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not update custody metrics: {str(e)}")

    # Additional methods for Olympic and Collaborative testing
    async def administer_olympic_event(self, participants: List[str], difficulty: TestDifficulty, event_type: str = "olympics") -> Dict[str, Any]:
        """Administer Olympic event with fallback system"""
        try:
            # Check if Claude tokens are available
            tokens_available = await self._check_claude_tokens_available()
            
            if tokens_available:
                logger.info(f"🎯 Using Claude for Olympic event")
                return await self._administer_olympic_with_claude(participants, difficulty, event_type)
            else:
                logger.info(f"🔄 Using fallback system for Olympic event")
                return await self._administer_olympic_with_fallback(participants, difficulty, event_type)
                
        except Exception as e:
            logger.error(f"❌ Error administering Olympic event: {str(e)}")
            return await self._administer_olympic_with_fallback(participants, difficulty, event_type)

    async def _administer_olympic_with_claude(self, participants: List[str], difficulty: TestDifficulty, event_type: str) -> Dict[str, Any]:
        """Administer Olympic event using Claude"""
        try:
            # Generate Olympic scenario using enhanced test generator
            scenario = await self.enhanced_test_generator.generate_dynamic_test_scenario(
                ai_types=participants,
                difficulty=difficulty.value,
                test_type="olympic",
                ai_levels={ai: await self._get_ai_level(ai) for ai in participants}
            )
            
            # Execute Olympic event
            results = {}
            for participant in participants:
                result = await self._execute_custody_test(participant, scenario, difficulty, TestCategory.PERFORMANCE_OPTIMIZATION)
                results[participant] = result
            
            return {
                "event_type": event_type,
                "participants": participants,
                "difficulty": difficulty.value,
                "scenario": scenario,
                "results": results,
                "source": "claude",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error administering Olympic with Claude: {str(e)}")
            return await self._administer_olympic_with_fallback(participants, difficulty, event_type)

    async def _administer_olympic_with_fallback(self, participants: List[str], difficulty: TestDifficulty, event_type: str) -> Dict[str, Any]:
        """Administer Olympic event using fallback system"""
        try:
            logger.info(f"🔄 Administering fallback Olympic event for {participants}")
            
            # Convert to fallback format
            fallback_difficulty = self._convert_to_fallback_difficulty(difficulty)
            fallback_category = FallbackTestCategory.PERFORMANCE_OPTIMIZATION
            
            # Generate Olympic scenario using fallback
            scenario = await self.enhanced_test_generator._generate_with_fallback(
                ai_types=participants,
                difficulty=difficulty.value,
                test_type="olympic",
                ai_levels={ai: await self._get_ai_level(ai) for ai in participants}
            )
            
            # Execute Olympic event using fallback
            results = {}
            for participant in participants:
                result = await self._execute_fallback_test(participant, scenario, difficulty, TestCategory.PERFORMANCE_OPTIMIZATION)
                results[participant] = result
            
            return {
                "event_type": event_type,
                "participants": participants,
                "difficulty": difficulty.value,
                "scenario": scenario,
                "results": results,
                "source": "fallback_system",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error administering Olympic with fallback: {str(e)}")
            return self._create_emergency_olympic_result(participants, difficulty, event_type)

    def _create_emergency_olympic_result(self, participants: List[str], difficulty: TestDifficulty, event_type: str) -> Dict[str, Any]:
        """Create emergency Olympic result when all else fails"""
        results = {}
        for participant in participants:
            results[participant] = {
                "score": 0.0,
                "passed": False,
                "ai_response": f"Emergency response for {participant}",
                "evaluation": "Emergency fallback evaluation",
                "source": "emergency_fallback"
            }
        
        return {
            "event_type": event_type,
            "participants": participants,
            "difficulty": difficulty.value,
            "scenario": {
                "id": f"emergency_olympic_{uuid.uuid4().hex[:8]}",
                "description": "Emergency Olympic event",
                "test_type": "olympic"
            },
            "results": results,
            "source": "emergency_fallback",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def administer_collaborative_test(self, participants: List[str], difficulty: TestDifficulty) -> Dict[str, Any]:
        """Administer collaborative test with fallback system"""
        try:
            # Check if Claude tokens are available
            tokens_available = await self._check_claude_tokens_available()
            
            if tokens_available:
                logger.info(f"🎯 Using Claude for collaborative test")
                return await self._administer_collaborative_with_claude(participants, difficulty)
            else:
                logger.info(f"🔄 Using fallback system for collaborative test")
                return await self._administer_collaborative_with_fallback(participants, difficulty)
                
        except Exception as e:
            logger.error(f"❌ Error administering collaborative test: {str(e)}")
            return await self._administer_collaborative_with_fallback(participants, difficulty)

    async def _administer_collaborative_with_claude(self, participants: List[str], difficulty: TestDifficulty) -> Dict[str, Any]:
        """Administer collaborative test using Claude"""
        try:
            # Generate collaborative scenario using enhanced test generator
            scenario = await self.enhanced_test_generator.generate_dynamic_test_scenario(
                ai_types=participants,
                difficulty=difficulty.value,
                test_type="collaborative",
                ai_levels={ai: await self._get_ai_level(ai) for ai in participants}
            )
            
            # Execute collaborative test
            results = {}
            for participant in participants:
                result = await self._execute_custody_test(participant, scenario, difficulty, TestCategory.CROSS_AI_COLLABORATION)
                results[participant] = result
            
            return {
                "test_type": "collaborative",
                "participants": participants,
                "difficulty": difficulty.value,
                "scenario": scenario,
                "results": results,
                "source": "claude",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error administering collaborative with Claude: {str(e)}")
            return await self._administer_collaborative_with_fallback(participants, difficulty)

    async def _administer_collaborative_with_fallback(self, participants: List[str], difficulty: TestDifficulty) -> Dict[str, Any]:
        """Administer collaborative test using fallback system"""
        try:
            logger.info(f"🔄 Administering fallback collaborative test for {participants}")
            
            # Generate collaborative scenario using fallback
            scenario = await self.enhanced_test_generator._generate_with_fallback(
                ai_types=participants,
                difficulty=difficulty.value,
                test_type="collaborative",
                ai_levels={ai: await self._get_ai_level(ai) for ai in participants}
            )
            
            # Execute collaborative test using fallback
            results = {}
            for participant in participants:
                result = await self._execute_fallback_test(participant, scenario, difficulty, TestCategory.CROSS_AI_COLLABORATION)
                results[participant] = result
            
            return {
                "test_type": "collaborative",
                "participants": participants,
                "difficulty": difficulty.value,
                "scenario": scenario,
                "results": results,
                "source": "fallback_system",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error administering collaborative with fallback: {str(e)}")
            return self._create_emergency_collaborative_result(participants, difficulty)

    def _create_emergency_collaborative_result(self, participants: List[str], difficulty: TestDifficulty) -> Dict[str, Any]:
        """Create emergency collaborative result when all else fails"""
        results = {}
        for participant in participants:
            results[participant] = {
                "score": 0.0,
                "passed": False,
                "ai_response": f"Emergency collaborative response for {participant}",
                "evaluation": "Emergency fallback evaluation",
                "source": "emergency_fallback"
            }
        
        return {
            "test_type": "collaborative",
            "participants": participants,
            "difficulty": difficulty.value,
            "scenario": {
                "id": f"emergency_collaborative_{uuid.uuid4().hex[:8]}",
                "description": "Emergency collaborative test",
                "test_type": "collaborative"
            },
            "results": results,
            "source": "emergency_fallback",
            "timestamp": datetime.utcnow().isoformat()
        }

    # Utility methods
    async def get_custody_analytics(self) -> Dict[str, Any]:
        """Get custody analytics"""
        try:
            async with get_session() as session:
                result = await session.execute(text("SELECT * FROM custody_metrics"))
                metrics = result.fetchall()
                
                analytics = {
                    "total_ais": len(metrics),
                    "total_tests": sum(row[2] for row in metrics),
                    "total_passed": sum(row[3] for row in metrics),
                    "total_failed": sum(row[4] for row in metrics),
                    "average_level": sum(row[5] for row in metrics) / len(metrics) if metrics else 1,
                    "ai_metrics": {}
                }
                
                for row in metrics:
                    ai_type = row[0]
                    analytics["ai_metrics"][ai_type] = {
                        "total_tests": row[2],
                        "passed_tests": row[3],
                        "failed_tests": row[4],
                        "current_level": row[5],
                        "learning_score": row[6],
                        "last_test_date": row[7].isoformat() if row[7] else None
                    }
                
                return analytics
                
        except Exception as e:
            logger.warning(f"⚠️ Could not get custody analytics: {str(e)}")
            return {"error": "Could not retrieve analytics"}

    async def force_custody_test(self, ai_type: str) -> Dict[str, Any]:
        """Force a custody test for an AI"""
        return await self.administer_custody_test(ai_type)

    async def reset_custody_metrics(self, ai_type: str) -> Dict[str, Any]:
        """Reset custody metrics for an AI"""
        try:
            async with get_session() as session:
                await session.execute(text("""
                    UPDATE custody_metrics 
                    SET total_tests = 0,
                        passed_tests = 0,
                        failed_tests = 0,
                        current_level = 1,
                        learning_score = 0.0,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE ai_type = :ai_type
                """), {"ai_type": ai_type})
                await session.commit()
                
                return {
                    "ai_type": ai_type,
                    "status": "reset",
                    "message": "Custody metrics reset successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Error resetting custody metrics: {str(e)}")
            return {
                "ai_type": ai_type,
                "status": "error",
                "message": f"Could not reset metrics: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }