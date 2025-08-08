"""
Adaptive Test System - Dynamic difficulty scaling based on AI performance
All data persisted to Neon DB, no in-house storage
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, List, Any, Tuple
import structlog

from ..core.database import get_session
from ..core.config import settings

logger = structlog.get_logger()


class AdaptiveTestSystem:
    """Adaptive test system with dynamic difficulty scaling"""
    
    def __init__(self):
        self.agent_metrics_service = None
        self.learning_service = None
    
    async def initialize(self, agent_metrics_service, learning_service):
        """Initialize the adaptive test system"""
        self.agent_metrics_service = agent_metrics_service
        self.learning_service = learning_service
        logger.info("✅ Adaptive Test System initialized")
    
    async def calculate_adaptive_difficulty(self, ai_type: str) -> Tuple[float, float, float]:
        """Calculate adaptive difficulty based on AI performance and growth analytics"""
        try:
            # Get AI's current level and performance metrics from Neon DB
            current_level = await self._get_ai_level(ai_type)
            custody_metrics = await self.agent_metrics_service.get_custody_metrics(ai_type)
            
            # Get recent test performance (last 5 tests)
            recent_tests = custody_metrics.get('recent_test_results', [])
            if len(recent_tests) >= 5:
                recent_performance = recent_tests[-5:]  # Last 5 tests
                pass_rate = sum(1 for test in recent_performance if test.get('passed', False)) / len(recent_performance)
                
                # Calculate adaptive difficulty
                base_difficulty = self._get_base_difficulty_for_level(current_level)
                
                # Adjust difficulty based on performance
                if pass_rate >= 0.8:  # 80%+ pass rate
                    difficulty_adjustment = 0.5  # Increase difficulty
                    complexity_multiplier = 1.2
                elif pass_rate >= 0.6:  # 60-80% pass rate
                    difficulty_adjustment = 0.2  # Slight increase
                    complexity_multiplier = 1.1
                elif pass_rate <= 0.2:  # 20% or less pass rate
                    difficulty_adjustment = -0.3  # Decrease difficulty
                    complexity_multiplier = 0.9
                else:
                    difficulty_adjustment = 0.0  # No change
                    complexity_multiplier = 1.0
                
                adaptive_difficulty = base_difficulty + difficulty_adjustment
                adaptive_difficulty = max(0.1, min(10.0, adaptive_difficulty))  # Clamp between 0.1 and 10.0
                
                # Persist adaptive difficulty to Neon DB
                await self._persist_adaptive_difficulty(ai_type, adaptive_difficulty, complexity_multiplier, pass_rate)
                
                return adaptive_difficulty, complexity_multiplier, pass_rate
            else:
                # Not enough data, use base difficulty
                base_difficulty = self._get_base_difficulty_for_level(current_level)
                return base_difficulty, 1.0, 0.0
                
        except Exception as e:
            logger.error(f"Error calculating adaptive difficulty for {ai_type}: {str(e)}")
            return 1.0, 1.0, 0.0

    def _get_base_difficulty_for_level(self, ai_level: int) -> float:
        """Get base difficulty for AI level"""
        if ai_level < 5:
            return 1.0
        elif ai_level < 10:
            return 2.0
        elif ai_level < 15:
            return 3.0
        elif ai_level < 20:
            return 4.0
        elif ai_level < 25:
            return 5.0
        elif ai_level < 30:
            return 6.0
        elif ai_level < 35:
            return 7.0
        elif ai_level < 40:
            return 8.0
        elif ai_level < 45:
            return 9.0
        else:
            return 10.0

    async def _persist_adaptive_difficulty(self, ai_type: str, difficulty: float, complexity_multiplier: float, pass_rate: float):
        """Persist adaptive difficulty data to Neon DB"""
        try:
            session = get_session()
            async with session as s:
                from ..models.sql_models import AdaptiveDifficulty
                
                adaptive_difficulty = AdaptiveDifficulty(
                    ai_type=ai_type,
                    difficulty=difficulty,
                    complexity_multiplier=complexity_multiplier,
                    pass_rate=pass_rate,
                    timestamp=datetime.now()
                )
                
                s.add(adaptive_difficulty)
                await s.commit()
                
                logger.info(f"✅ Persisted adaptive difficulty for {ai_type}: {difficulty} (complexity: {complexity_multiplier})")
                
        except Exception as e:
            logger.error(f"Error persisting adaptive difficulty: {str(e)}")

    async def generate_adaptive_test_scenario(self, ai_types: list, test_type: str) -> dict:
        """Generate test scenario with adaptive difficulty based on AI performance"""
        try:
            # Calculate adaptive difficulty for each AI
            ai_adaptive_data = {}
            for ai in ai_types:
                difficulty, complexity_multiplier, pass_rate = await self.calculate_adaptive_difficulty(ai)
                ai_adaptive_data[ai] = {
                    'difficulty': difficulty,
                    'complexity_multiplier': complexity_multiplier,
                    'pass_rate': pass_rate
                }
            
            # Use highest difficulty and complexity for collaborative tests
            if len(ai_types) > 1:
                max_difficulty = max(data['difficulty'] for data in ai_adaptive_data.values())
                max_complexity = max(data['complexity_multiplier'] for data in ai_adaptive_data.values())
                avg_pass_rate = sum(data['pass_rate'] for data in ai_adaptive_data.values()) / len(ai_adaptive_data)
            else:
                ai_data = ai_adaptive_data[ai_types[0]]
                max_difficulty = ai_data['difficulty']
                max_complexity = ai_data['complexity_multiplier']
                avg_pass_rate = ai_data['pass_rate']
            
            # Generate scenario based on adaptive difficulty
            scenario = await self._generate_scenario_for_adaptive_difficulty(ai_types, max_difficulty, max_complexity, avg_pass_rate)
            
            # Add adaptive difficulty context
            scenario['adaptive_difficulty'] = max_difficulty
            scenario['complexity_multiplier'] = max_complexity
            scenario['ai_performance_data'] = ai_adaptive_data
            
            return scenario
            
        except Exception as e:
            logger.error(f"Error generating adaptive test scenario: {str(e)}")
            return await self._generate_emergency_test(ai_types)

    async def _generate_scenario_for_adaptive_difficulty(self, ai_types: list, difficulty: float, complexity_multiplier: float, pass_rate: float) -> dict:
        """Generate scenario based on adaptive difficulty and complexity"""
        
        # Determine scenario type based on difficulty
        if difficulty < 2.0:
            base_scenarios = [
                "Create a simple REST API with basic CRUD operations and user authentication",
                "Build a basic web application with user registration, login, and dashboard",
                "Implement a simple data processing pipeline with error handling"
            ]
        elif difficulty < 4.0:
            base_scenarios = [
                "Design a microservices architecture with 3 services and message queues",
                "Build a real-time chat application with WebSocket support and user presence",
                "Create a machine learning pipeline for sentiment analysis with API endpoints"
            ]
        elif difficulty < 6.0:
            base_scenarios = [
                "Implement a distributed caching system with Redis cluster and load balancing",
                "Design a serverless architecture using cloud services with event-driven processing",
                "Build a real-time analytics platform with streaming data and aggregations"
            ]
        elif difficulty < 8.0:
            base_scenarios = [
                "Create an AI-powered recommendation system with real-time learning and A/B testing",
                "Design a zero-trust security architecture with multi-factor authentication",
                "Architect a high-performance system handling 100K+ concurrent users with sub-100ms response times"
            ]
        else:
            base_scenarios = [
                "Create an autonomous AI system that can self-improve and handle edge cases",
                "Design a quantum-resistant cryptographic system with post-quantum algorithms",
                "Build a distributed AI training platform with federated learning and differential privacy"
            ]
        
        # Select base scenario
        base_scenario = random.choice(base_scenarios)
        
        # Add complexity based on complexity_multiplier
        if complexity_multiplier > 1.0:
            complexity_additions = [
                f" Scale this solution to handle {int(1000 * complexity_multiplier)}x more load",
                f" Implement advanced monitoring, automated scaling, and disaster recovery",
                f" Add comprehensive security measures, performance optimization, and testing",
                f" Include multi-region deployment, load balancing, and fault tolerance"
            ]
            base_scenario += random.choice(complexity_additions)
        
        # Add collaborative elements for multiple AIs
        if len(ai_types) > 1:
            collaboration_roles = []
            for i, ai in enumerate(ai_types):
                if i == 0:
                    collaboration_roles.append(f"{ai} handles the core architecture and design")
                elif i == 1:
                    collaboration_roles.append(f"{ai} manages the implementation and deployment")
                else:
                    collaboration_roles.append(f"{ai} focuses on testing, monitoring, and optimization")
            
            base_scenario += f". {', '.join(collaboration_roles)}. Work together to ensure seamless integration and optimal performance."
        
        return {
            "type": "single" if len(ai_types) == 1 else "collaborative",
            "ai_types": ai_types,
            "scenario": base_scenario,
            "difficulty": difficulty,
            "complexity_multiplier": complexity_multiplier,
            "pass_rate": pass_rate,
            "requirements": ["coding", "architecture", "deployment", "testing", "scaling"],
            "success_criteria": ["Working implementation", "Clear documentation", "Security measures", "Performance optimization", "Scalability"]
        }

    async def _generate_emergency_test(self, ai_types: list) -> dict:
        """Emergency fallback test"""
        if len(ai_types) == 1:
            scenario = f"Emergency test for {ai_types[0]}: Create a complete application demonstrating your current capabilities."
        else:
            scenario = f"Emergency collaborative test for {', '.join(ai_types)}: Work together to build a system that showcases your combined capabilities."
        
        return {
            "type": "single" if len(ai_types) == 1 else "collaborative",
            "ai_types": ai_types,
            "scenario": scenario,
            "difficulty": 1.0
        }

    async def _get_ai_level(self, ai_type: str) -> int:
        """Get AI level from Neon DB"""
        try:
            # This should be implemented to get AI level from the database
            # For now, return a default level
            return 1
        except Exception as e:
            logger.error(f"Error getting AI level for {ai_type}: {str(e)}")
            return 1

    async def update_ai_growth_analytics(self, ai_type: str, test_result: dict):
        """Update AI growth analytics based on test results"""
        try:
            test_passed = test_result.get('passed', False)
            test_score = test_result.get('score', 0)
            
            # Update difficulty based on performance
            if test_passed and test_score >= 80:
                # AI performed well, increase difficulty
                current_difficulty = test_result.get('adaptive_difficulty', 1.0)
                new_difficulty = min(10.0, current_difficulty + 0.5)
                
                # Update in database
                await self._update_ai_difficulty(ai_type, new_difficulty)
                
                logger.info(f"✅ Increased difficulty for {ai_type} from {current_difficulty} to {new_difficulty}")
            
            elif not test_passed and test_score < 50:
                # AI struggled, decrease difficulty
                current_difficulty = test_result.get('adaptive_difficulty', 1.0)
                new_difficulty = max(0.5, current_difficulty - 0.3)
                
                # Update in database
                await self._update_ai_difficulty(ai_type, new_difficulty)
                
                logger.info(f"⚠️ Decreased difficulty for {ai_type} from {current_difficulty} to {new_difficulty}")
            
            # Store growth analytics in Neon DB
            await self._persist_growth_analytics(ai_type, test_result)
            
        except Exception as e:
            logger.error(f"Error updating AI growth analytics: {str(e)}")

    async def _update_ai_difficulty(self, ai_type: str, new_difficulty: float):
        """Update AI difficulty in Neon DB"""
        try:
            session = get_session()
            async with session as s:
                from ..models.sql_models import AIGrowthAnalytics
                
                # Update or create growth analytics record
                existing = await s.execute(
                    select(AIGrowthAnalytics).where(AIGrowthAnalytics.ai_type == ai_type)
                )
                existing_record = existing.scalar_one_or_none()
                
                if existing_record:
                    existing_record.current_difficulty = new_difficulty
                    existing_record.last_updated = datetime.now()
                else:
                    new_record = AIGrowthAnalytics(
                        ai_type=ai_type,
                        current_difficulty=new_difficulty,
                        total_tests=0,
                        passed_tests=0,
                        average_score=0.0,
                        last_updated=datetime.now()
                    )
                    s.add(new_record)
                
                await s.commit()
                
        except Exception as e:
            logger.error(f"Error updating AI difficulty: {str(e)}")

    async def _persist_growth_analytics(self, ai_type: str, test_result: dict):
        """Persist growth analytics to Neon DB"""
        try:
            session = get_session()
            async with session as s:
                from ..models.sql_models import GrowthAnalyticsLog
                
                growth_log = GrowthAnalyticsLog(
                    ai_type=ai_type,
                    test_result=test_result,
                    timestamp=datetime.now()
                )
                
                s.add(growth_log)
                await s.commit()
                
        except Exception as e:
            logger.error(f"Error persisting growth analytics: {str(e)}")