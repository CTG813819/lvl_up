"""
AI Adversarial Integration Service
Integrates adversarial testing scenarios into backend AI learning cycles
Removes frontend dependency and embeds training into AI growth systems
"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog

from ..core.database import get_session
from .ai_learning_service import AILearningService
# Try to import from different locations
try:
    from .enhanced_adversarial_testing_service import EnhancedAdversarialTestingService, ScenarioDomain, ScenarioComplexity
except ImportError:
    try:
        import sys
        import os
        # Add parent directory to path
        parent_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        sys.path.insert(0, parent_dir)
        from app.services.enhanced_adversarial_testing_service import EnhancedAdversarialTestingService, ScenarioDomain, ScenarioComplexity
    except ImportError:
        # Mock classes for testing
        class ScenarioDomain:
            SYSTEM_LEVEL = "system_level"
            SECURITY_CHALLENGES = "security_challenges"
            COMPLEX_PROBLEM_SOLVING = "complex_problem_solving"
            CREATIVE_TASKS = "creative_tasks"
            COLLABORATION_COMPETITION = "collaboration_competition"
            PHYSICAL_SIMULATED = "physical_simulated"
        
        class ScenarioComplexity:
            BASIC = "basic"
            INTERMEDIATE = "intermediate"
            ADVANCED = "advanced"
            EXPERT = "expert"
            MASTER = "master"
        
        class EnhancedAdversarialTestingService:
            async def initialize(self, fast_mode=False):
                pass
            async def generate_diverse_adversarial_scenario(self, ai_types, target_domain=None, complexity=None, fast_mode=False):
                return {"scenario_id": "mock_scenario", "domain": "mock", "complexity": "intermediate"}
from .agent_metrics_service import AgentMetricsService

logger = structlog.get_logger()


class AIAdversarialIntegrationService:
    """Integrates adversarial scenarios into AI learning and growth cycles"""
    
    def __init__(self):
        self.adversarial_service = None
        self.learning_service = AILearningService()
        self.metrics_service = AgentMetricsService()
        
        # AI learning progress tracking
        self.ai_adversarial_progress = {
            "imperium": {"level": 1, "victories": 0, "defeats": 0, "scenarios_completed": 0},
            "guardian": {"level": 1, "victories": 0, "defeats": 0, "scenarios_completed": 0},
            "sandbox": {"level": 1, "victories": 0, "defeats": 0, "scenarios_completed": 0},
            "conquest": {"level": 1, "victories": 0, "defeats": 0, "scenarios_completed": 0}
        }
        
        # Scenario rotation system
        self.scenario_rotation = {
            "system_level": ScenarioDomain.SYSTEM_LEVEL,
            "security_challenges": ScenarioDomain.SECURITY_CHALLENGES,
            "complex_problem_solving": ScenarioDomain.COMPLEX_PROBLEM_SOLVING,
            "creative_tasks": ScenarioDomain.CREATIVE_TASKS,
            "collaboration_competition": ScenarioDomain.COLLABORATION_COMPETITION,
            "physical_simulated": ScenarioDomain.PHYSICAL_SIMULATED
        }
        
        # Knowledge sharing between AIs
        self.shared_adversarial_knowledge = {}
        
        # Schedule configuration
        self.schedule_config = {
            "imperium": {"interval_hours": 2, "focus_domains": ["system_level", "security_challenges"]},
            "guardian": {"interval_hours": 3, "focus_domains": ["security_challenges", "collaboration_competition"]},
            "sandbox": {"interval_hours": 1.5, "focus_domains": ["creative_tasks", "complex_problem_solving"]},
            "conquest": {"interval_hours": 2.5, "focus_domains": ["collaboration_competition", "complex_problem_solving"]}
        }
        
    async def initialize(self):
        """Initialize the adversarial integration service"""
        try:
            # Initialize adversarial testing service
            self.adversarial_service = EnhancedAdversarialTestingService()
            await self.adversarial_service.initialize(fast_mode=False)
            
            # Initialize metrics service
            await self.metrics_service.initialize()
            
            logger.info("AI Adversarial Integration Service initialized")
            
        except Exception as e:
            logger.error(f"Error initializing AI Adversarial Integration Service: {e}")
            raise
    
    async def integrate_adversarial_scenario_into_ai_learning(self, ai_type: str, 
                                                            force_scenario: Optional[str] = None) -> Dict[str, Any]:
        """Integrate adversarial scenario into specific AI's learning cycle"""
        try:
            # Get AI's current progress and determine appropriate scenario
            current_progress = self.ai_adversarial_progress.get(ai_type, {})
            
            # Select scenario domain based on AI focus areas or force specific one
            if force_scenario:
                domain = self.scenario_rotation.get(force_scenario, ScenarioDomain.SYSTEM_LEVEL)
            else:
                focus_domains = self.schedule_config[ai_type]["focus_domains"]
                domain_name = random.choice(focus_domains)
                domain = self.scenario_rotation[domain_name]
            
            # Determine complexity based on AI's level and recent performance
            complexity = self._determine_scenario_complexity(ai_type, current_progress)
            
            # Generate adversarial scenario for this AI
            scenario = await self.adversarial_service.generate_diverse_adversarial_scenario(
                ai_types=[ai_type],
                target_domain=domain,
                complexity=complexity,
                fast_mode=False
            )
            
            # Execute scenario and learn from results
            execution_result = await self._execute_adversarial_scenario_for_ai(ai_type, scenario)
            
            # Update AI progress and share knowledge
            await self._update_ai_adversarial_progress(ai_type, execution_result)
            await self._share_adversarial_knowledge_with_other_ais(ai_type, execution_result)
            
            # Store learning insights
            await self._store_adversarial_learning_insights(ai_type, scenario, execution_result)
            
            return {
                "ai_type": ai_type,
                "scenario": scenario,
                "execution_result": execution_result,
                "progress_update": self.ai_adversarial_progress[ai_type],
                "knowledge_shared": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error integrating adversarial scenario for {ai_type}: {e}")
            return {"error": str(e), "ai_type": ai_type}
    
    def _determine_scenario_complexity(self, ai_type: str, progress: Dict[str, Any]) -> ScenarioComplexity:
        """Determine appropriate scenario complexity based on AI progress"""
        level = progress.get("level", 1)
        victories = progress.get("victories", 0)
        defeats = progress.get("defeats", 0)
        
        # Calculate success rate
        total_scenarios = victories + defeats
        success_rate = victories / total_scenarios if total_scenarios > 0 else 0.5
        
        # Determine complexity based on level and performance
        if level >= 5 and success_rate > 0.8:
            return ScenarioComplexity.MASTER
        elif level >= 4 and success_rate > 0.7:
            return ScenarioComplexity.EXPERT
        elif level >= 3 and success_rate > 0.6:
            return ScenarioComplexity.ADVANCED
        elif level >= 2 and success_rate > 0.5:
            return ScenarioComplexity.INTERMEDIATE
        else:
            return ScenarioComplexity.BASIC
    
    async def _execute_adversarial_scenario_for_ai(self, ai_type: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Execute adversarial scenario for specific AI and return results"""
        try:
            start_time = datetime.utcnow()
            
            # Simulate AI attempting the scenario
            scenario_difficulty = scenario.get("difficulty_level", 1.0)
            ai_capability = self._get_ai_capability_score(ai_type)
            
            # Determine success based on AI capability vs scenario difficulty
            success_probability = min(ai_capability / (scenario_difficulty + 0.5), 0.95)
            success = random.random() < success_probability
            
            # Calculate performance score
            if success:
                # Performance varies based on how well AI handles the scenario
                base_score = random.uniform(0.7, 1.0)
                complexity_bonus = scenario_difficulty * 0.1
                performance_score = min(base_score + complexity_bonus, 1.0)
            else:
                # Failure but potential learning
                performance_score = random.uniform(0.1, 0.4)
            
            # Generate lessons learned
            lessons_learned = await self._generate_lessons_learned(ai_type, scenario, success, performance_score)
            
            # Calculate execution time
            execution_time = datetime.utcnow() - start_time
            
            return {
                "success": success,
                "performance_score": performance_score,
                "execution_time_seconds": execution_time.total_seconds(),
                "lessons_learned": lessons_learned,
                "scenario_domain": scenario.get("domain", "unknown"),
                "scenario_complexity": scenario.get("complexity", "intermediate"),
                "ai_capability_score": ai_capability,
                "scenario_difficulty": scenario_difficulty,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing adversarial scenario for {ai_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "performance_score": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _get_ai_capability_score(self, ai_type: str) -> float:
        """Get AI's current capability score based on progress and experience"""
        progress = self.ai_adversarial_progress.get(ai_type, {})
        
        level = progress.get("level", 1)
        victories = progress.get("victories", 0)
        scenarios_completed = progress.get("scenarios_completed", 0)
        
        # Base capability from level
        base_capability = level * 0.2
        
        # Experience bonus
        experience_bonus = min(scenarios_completed * 0.01, 0.3)
        
        # Victory bonus
        victory_bonus = min(victories * 0.02, 0.2)
        
        return min(base_capability + experience_bonus + victory_bonus, 2.0)
    
    async def _generate_lessons_learned(self, ai_type: str, scenario: Dict[str, Any], 
                                      success: bool, performance_score: float) -> List[str]:
        """Generate lessons learned from scenario execution"""
        lessons = []
        
        domain = scenario.get("domain", "unknown")
        complexity = scenario.get("complexity", "intermediate")
        
        if success:
            lessons.append(f"Successfully completed {domain} scenario at {complexity} level")
            lessons.append(f"Achieved performance score of {performance_score:.2f}")
            
            if performance_score > 0.9:
                lessons.append("Demonstrated exceptional problem-solving capability")
            elif performance_score > 0.8:
                lessons.append("Showed strong understanding of scenario requirements")
            
        else:
            lessons.append(f"Failed {domain} scenario - opportunity for improvement")
            lessons.append(f"Need to strengthen capabilities in {domain} domain")
            
            # Domain-specific learning suggestions
            if domain == "security_challenges":
                lessons.append("Focus on security analysis and threat modeling")
            elif domain == "system_level":
                lessons.append("Improve system architecture and orchestration skills")
            elif domain == "creative_tasks":
                lessons.append("Enhance creative problem-solving approaches")
        
        # Add AI-specific learning context
        if ai_type == "imperium":
            lessons.append("Apply learnings to system governance and control")
        elif ai_type == "guardian":
            lessons.append("Integrate learnings into security protection protocols")
        elif ai_type == "sandbox":
            lessons.append("Use learnings for experimental innovation")
        elif ai_type == "conquest":
            lessons.append("Apply learnings to user experience optimization")
        
        return lessons
    
    async def _update_ai_adversarial_progress(self, ai_type: str, execution_result: Dict[str, Any]):
        """Update AI's adversarial progress based on execution results"""
        if ai_type not in self.ai_adversarial_progress:
            self.ai_adversarial_progress[ai_type] = {"level": 1, "victories": 0, "defeats": 0, "scenarios_completed": 0}
        
        progress = self.ai_adversarial_progress[ai_type]
        progress["scenarios_completed"] += 1
        
        if execution_result.get("success", False):
            progress["victories"] += 1
            
            # Check for level up
            if progress["victories"] % 5 == 0:  # Level up every 5 victories
                progress["level"] = min(progress["level"] + 1, 10)
                logger.info(f"{ai_type} leveled up to level {progress['level']}")
        else:
            progress["defeats"] += 1
        
        # Update metrics service
        try:
            await self.metrics_service.update_adversarial_metrics(
                ai_type, 
                execution_result.get("performance_score", 0.0),
                execution_result.get("success", False)
            )
        except Exception as e:
            logger.warning(f"Failed to update metrics for {ai_type}: {e}")
    
    async def _share_adversarial_knowledge_with_other_ais(self, source_ai: str, execution_result: Dict[str, Any]):
        """Share adversarial learning knowledge with other AIs"""
        try:
            # Extract shareable knowledge
            lessons = execution_result.get("lessons_learned", [])
            domain = execution_result.get("scenario_domain", "unknown")
            success = execution_result.get("success", False)
            
            knowledge_entry = {
                "source_ai": source_ai,
                "domain": domain,
                "success": success,
                "lessons": lessons,
                "performance_score": execution_result.get("performance_score", 0.0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to shared knowledge base
            if domain not in self.shared_adversarial_knowledge:
                self.shared_adversarial_knowledge[domain] = []
            
            self.shared_adversarial_knowledge[domain].append(knowledge_entry)
            
            # Keep only recent knowledge (last 50 entries per domain)
            self.shared_adversarial_knowledge[domain] = self.shared_adversarial_knowledge[domain][-50:]
            
            # Notify other AIs of new knowledge
            for ai_type in self.ai_adversarial_progress.keys():
                if ai_type != source_ai:
                    await self._apply_shared_knowledge_to_ai(ai_type, knowledge_entry)
            
        except Exception as e:
            logger.error(f"Error sharing adversarial knowledge: {e}")
    
    async def _apply_shared_knowledge_to_ai(self, ai_type: str, knowledge_entry: Dict[str, Any]):
        """Apply shared knowledge to AI's learning"""
        try:
            # Small capability boost from shared knowledge
            if knowledge_entry.get("success", False):
                # Positive knowledge sharing
                boost = 0.01 * knowledge_entry.get("performance_score", 0.0)
                logger.debug(f"{ai_type} gained knowledge boost of {boost:.3f} from {knowledge_entry['source_ai']}")
            
        except Exception as e:
            logger.error(f"Error applying shared knowledge to {ai_type}: {e}")
    
    async def _store_adversarial_learning_insights(self, ai_type: str, scenario: Dict[str, Any], 
                                                 execution_result: Dict[str, Any]):
        """Store adversarial learning insights in database"""
        try:
            insight_data = {
                "ai_type": ai_type,
                "scenario_domain": scenario.get("domain", "unknown"),
                "scenario_complexity": scenario.get("complexity", "intermediate"),
                "success": execution_result.get("success", False),
                "performance_score": execution_result.get("performance_score", 0.0),
                "lessons_learned": execution_result.get("lessons_learned", []),
                "execution_time": execution_result.get("execution_time_seconds", 0.0),
                "timestamp": datetime.utcnow().isoformat(),
                "scenario_id": scenario.get("scenario_id", "unknown")
            }
            
            # Store using learning service
            await self.learning_service.store_learning_insight(
                ai_type, 
                f"adversarial_scenario_{scenario.get('domain', 'unknown')}", 
                insight_data
            )
            
        except Exception as e:
            logger.error(f"Error storing adversarial learning insights: {e}")
    
    async def run_scheduled_adversarial_training(self, ai_type: str) -> Dict[str, Any]:
        """Run scheduled adversarial training for specific AI"""
        try:
            logger.info(f"Running scheduled adversarial training for {ai_type}")
            
            # Run adversarial scenario integration
            result = await self.integrate_adversarial_scenario_into_ai_learning(ai_type)
            
            # Log training completion
            logger.info(f"Adversarial training completed for {ai_type}: success={result.get('execution_result', {}).get('success', False)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in scheduled adversarial training for {ai_type}: {e}")
            return {"error": str(e), "ai_type": ai_type}
    
    async def get_adversarial_progress_report(self) -> Dict[str, Any]:
        """Get comprehensive adversarial progress report for all AIs"""
        try:
            report = {
                "timestamp": datetime.utcnow().isoformat(),
                "ai_progress": self.ai_adversarial_progress.copy(),
                "shared_knowledge_domains": list(self.shared_adversarial_knowledge.keys()),
                "total_shared_knowledge_entries": sum(len(entries) for entries in self.shared_adversarial_knowledge.values()),
                "schedule_config": self.schedule_config.copy()
            }
            
            # Add aggregated statistics
            total_victories = sum(ai["victories"] for ai in self.ai_adversarial_progress.values())
            total_defeats = sum(ai["defeats"] for ai in self.ai_adversarial_progress.values())
            total_scenarios = sum(ai["scenarios_completed"] for ai in self.ai_adversarial_progress.values())
            
            report["aggregate_stats"] = {
                "total_victories": total_victories,
                "total_defeats": total_defeats,
                "total_scenarios_completed": total_scenarios,
                "overall_success_rate": total_victories / max(total_scenarios, 1)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating adversarial progress report: {e}")
            return {"error": str(e)}


# Global instance
ai_adversarial_integration_service = AIAdversarialIntegrationService()