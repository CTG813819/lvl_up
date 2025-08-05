"""
Dynamic Test Generator Service
Generates diverse, adaptive test scenarios that learn from AI performance
"""

import asyncio
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import structlog
from dataclasses import dataclass

logger = structlog.get_logger()

class TestDifficulty(Enum):
    """Test difficulty levels that scale with AI performance"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    LEGENDARY = "legendary"

class TestCategory(Enum):
    """Categories of tests that adapt based on AI learning"""
    KNOWLEDGE_VERIFICATION = "knowledge_verification"
    CODE_QUALITY = "code_quality"
    SECURITY_AWARENESS = "security_awareness"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    INNOVATION_CAPABILITY = "innovation_capability"
    SELF_IMPROVEMENT = "self_improvement"
    CROSS_AI_COLLABORATION = "cross_ai_collaboration"
    EXPERIMENTAL_VALIDATION = "experimental_validation"

@dataclass
class TestScenario:
    """Dynamic test scenario with learning adaptation"""
    scenario_id: str
    ai_type: str
    difficulty: TestDifficulty
    category: TestCategory
    content: Dict[str, Any]
    learning_objectives: List[str]
    success_criteria: Dict[str, float]
    time_limit: int
    max_attempts: int
    generated_at: datetime
    is_dynamic: bool = True
    previous_performance: Optional[float] = None
    adaptation_factor: float = 1.0

class DynamicTestGenerator:
    """Generates dynamic, adaptive test scenarios"""
    
    def __init__(self):
        self.ai_performance_history = {}
        self.scenario_templates = self._initialize_scenario_templates()
        self.learning_patterns = {}
        self.adaptation_rules = self._initialize_adaptation_rules()
        
    def _initialize_scenario_templates(self) -> Dict[str, Dict]:
        """Initialize diverse scenario templates"""
        return {
            "imperium": {
                "knowledge_verification": {
                    "basic": [
                        "AI governance principles",
                        "Meta-learning concepts",
                        "Autonomous system design"
                    ],
                    "intermediate": [
                        "Multi-agent coordination",
                        "AI self-improvement mechanisms",
                        "Ethical AI frameworks"
                    ],
                    "advanced": [
                        "AGI safety protocols",
                        "Consciousness in AI systems",
                        "AI rights and responsibilities"
                    ]
                },
                "code_quality": {
                    "basic": [
                        "Code review best practices",
                        "Documentation standards",
                        "Error handling patterns"
                    ],
                    "intermediate": [
                        "Architecture design patterns",
                        "Performance optimization",
                        "Security implementation"
                    ],
                    "advanced": [
                        "System design at scale",
                        "Advanced algorithms",
                        "Innovative problem solving"
                    ]
                }
            },
            "guardian": {
                "security_awareness": {
                    "basic": [
                        "Vulnerability identification",
                        "Secure coding practices",
                        "Threat modeling basics"
                    ],
                    "intermediate": [
                        "Advanced security testing",
                        "Penetration testing techniques",
                        "Security architecture design"
                    ],
                    "advanced": [
                        "Zero-day vulnerability research",
                        "Advanced threat detection",
                        "Security automation systems"
                    ]
                },
                "code_quality": {
                    "basic": [
                        "Code security review",
                        "Input validation",
                        "Authentication mechanisms"
                    ],
                    "intermediate": [
                        "Advanced security patterns",
                        "Cryptographic implementations",
                        "Security monitoring"
                    ],
                    "advanced": [
                        "Security framework design",
                        "Advanced threat prevention",
                        "Security AI systems"
                    ]
                }
            },
            "sandbox": {
                "innovation_capability": {
                    "basic": [
                        "Creative problem solving",
                        "Experimental approaches",
                        "Novel algorithm design"
                    ],
                    "intermediate": [
                        "Advanced experimentation",
                        "Innovation frameworks",
                        "Breakthrough thinking"
                    ],
                    "advanced": [
                        "Revolutionary concepts",
                        "Paradigm-shifting ideas",
                        "Future technology design"
                    ]
                },
                "experimental_validation": {
                    "basic": [
                        "Hypothesis testing",
                        "Experimental design",
                        "Data analysis methods"
                    ],
                    "intermediate": [
                        "Advanced experimentation",
                        "Statistical validation",
                        "Research methodology"
                    ],
                    "advanced": [
                        "Cutting-edge research",
                        "Novel validation methods",
                        "Experimental AI systems"
                    ]
                }
            },
            "conquest": {
                "performance_optimization": {
                    "basic": [
                        "App performance basics",
                        "User experience design",
                        "Mobile optimization"
                    ],
                    "intermediate": [
                        "Advanced app architecture",
                        "Performance profiling",
                        "Scalability design"
                    ],
                    "advanced": [
                        "Enterprise app design",
                        "Advanced optimization",
                        "AI-powered apps"
                    ]
                },
                "innovation_capability": {
                    "basic": [
                        "App concept development",
                        "Feature design",
                        "User interface creation"
                    ],
                    "intermediate": [
                        "Advanced app features",
                        "Integration design",
                        "Market analysis"
                    ],
                    "advanced": [
                        "Revolutionary app concepts",
                        "AI-driven development",
                        "Future app platforms"
                    ]
                }
            }
        }
    
    def _initialize_adaptation_rules(self) -> Dict[str, Any]:
        """Initialize rules for adapting test difficulty based on performance"""
        return {
            "difficulty_increase": {
                "threshold": 0.8,  # Score above 80% increases difficulty
                "factor": 1.2,     # 20% increase in difficulty
                "max_difficulty": "legendary"
            },
            "difficulty_decrease": {
                "threshold": 0.4,  # Score below 40% decreases difficulty
                "factor": 0.8,     # 20% decrease in difficulty
                "min_difficulty": "basic"
            },
            "category_adaptation": {
                "success_threshold": 0.7,  # Success rate for category advancement
                "failure_threshold": 0.3,  # Failure rate for category regression
                "learning_rate": 0.1       # Rate of learning from performance
            }
        }
    
    async def generate_dynamic_test(self, ai_type: str, ai_level: int, 
                                  previous_performance: Optional[float] = None) -> TestScenario:
        """Generate a dynamic test scenario based on AI performance"""
        try:
            # Determine base difficulty from AI level
            base_difficulty = self._get_base_difficulty(ai_level)
            
            # Adapt difficulty based on previous performance
            adapted_difficulty = self._adapt_difficulty(base_difficulty, previous_performance)
            
            # Select category based on AI type and learning patterns
            category = self._select_category(ai_type, adapted_difficulty)
            
            # Generate dynamic content
            content = await self._generate_dynamic_content(ai_type, category, adapted_difficulty)
            
            # Create learning objectives
            learning_objectives = self._generate_learning_objectives(ai_type, category, adapted_difficulty)
            
            # Set success criteria
            success_criteria = self._generate_success_criteria(adapted_difficulty, category)
            
            # Determine time limit and attempts
            time_limit = self._get_time_limit(adapted_difficulty)
            max_attempts = self._get_max_attempts(adapted_difficulty)
            
            # Create scenario
            scenario = TestScenario(
                scenario_id=f"test_{int(datetime.utcnow().timestamp())}",
                ai_type=ai_type,
                difficulty=adapted_difficulty,
                category=category,
                content=content,
                learning_objectives=learning_objectives,
                success_criteria=success_criteria,
                time_limit=time_limit,
                max_attempts=max_attempts,
                generated_at=datetime.utcnow(),
                previous_performance=previous_performance,
                adaptation_factor=self._calculate_adaptation_factor(previous_performance)
            )
            
            logger.info(f"Generated dynamic test for {ai_type}: {category.value} at {adapted_difficulty.value} level")
            return scenario
            
        except Exception as e:
            logger.error(f"Error generating dynamic test: {str(e)}")
            return await self._generate_fallback_test(ai_type, ai_level)
    
    def _get_base_difficulty(self, ai_level: int) -> TestDifficulty:
        """Get base difficulty from AI level"""
        if ai_level <= 3:
            return TestDifficulty.BASIC
        elif ai_level <= 7:
            return TestDifficulty.INTERMEDIATE
        elif ai_level <= 12:
            return TestDifficulty.ADVANCED
        elif ai_level <= 18:
            return TestDifficulty.EXPERT
        elif ai_level <= 25:
            return TestDifficulty.MASTER
        else:
            return TestDifficulty.LEGENDARY
    
    def _adapt_difficulty(self, base_difficulty: TestDifficulty, 
                         previous_performance: Optional[float]) -> TestDifficulty:
        """Adapt difficulty based on previous performance"""
        if previous_performance is None:
            return base_difficulty
        
        difficulties = list(TestDifficulty)
        current_index = difficulties.index(base_difficulty)
        
        if previous_performance >= self.adaptation_rules["difficulty_increase"]["threshold"]:
            # Increase difficulty
            new_index = min(current_index + 1, len(difficulties) - 1)
            return difficulties[new_index]
        elif previous_performance <= self.adaptation_rules["difficulty_decrease"]["threshold"]:
            # Decrease difficulty
            new_index = max(current_index - 1, 0)
            return difficulties[new_index]
        else:
            return base_difficulty
    
    def _select_category(self, ai_type: str, difficulty: TestDifficulty) -> TestCategory:
        """Select test category based on AI type and difficulty with diversity tracking"""
        available_categories = {
            "imperium": [
                TestCategory.KNOWLEDGE_VERIFICATION,
                TestCategory.CODE_QUALITY,
                TestCategory.SELF_IMPROVEMENT
            ],
            "guardian": [
                TestCategory.SECURITY_AWARENESS,
                TestCategory.CODE_QUALITY,
                TestCategory.PERFORMANCE_OPTIMIZATION
            ],
            "sandbox": [
                TestCategory.INNOVATION_CAPABILITY,
                TestCategory.EXPERIMENTAL_VALIDATION,
                TestCategory.CROSS_AI_COLLABORATION
            ],
            "conquest": [
                TestCategory.PERFORMANCE_OPTIMIZATION,
                TestCategory.INNOVATION_CAPABILITY,
                TestCategory.CODE_QUALITY
            ]
        }
        
        categories = available_categories.get(ai_type, [TestCategory.KNOWLEDGE_VERIFICATION])
        
        # Track recent categories for this AI to ensure diversity
        if not hasattr(self, '_recent_categories'):
            self._recent_categories = {}
        
        if ai_type not in self._recent_categories:
            self._recent_categories[ai_type] = []
        
        # Get categories that haven't been used recently
        recent_categories = self._recent_categories[ai_type][-2:]  # Last 2 categories
        available_categories_filtered = [cat for cat in categories if cat not in recent_categories]
        
        # If all categories have been used recently, reset and use any category
        if not available_categories_filtered:
            available_categories_filtered = categories
        
        selected_category = random.choice(available_categories_filtered)
        
        # Update recent categories
        self._recent_categories[ai_type].append(selected_category)
        if len(self._recent_categories[ai_type]) > 5:  # Keep only last 5
            self._recent_categories[ai_type] = self._recent_categories[ai_type][-5:]
        
        return selected_category
    
    async def _generate_dynamic_content(self, ai_type: str, category: TestCategory, 
                                      difficulty: TestDifficulty) -> Dict[str, Any]:
        """Generate dynamic test content"""
        templates = self.scenario_templates.get(ai_type, {})
        category_templates = templates.get(category.value, {})
        difficulty_templates = category_templates.get(difficulty.value, [])
        
        if not difficulty_templates:
            # Generate fallback content
            return self._generate_fallback_content(ai_type, category, difficulty)
        
        selected_template = random.choice(difficulty_templates)
        
        return {
            "task": f"Complete {selected_template} challenge",
            "description": f"Demonstrate your expertise in {selected_template}",
            "requirements": self._generate_requirements(selected_template, difficulty),
            "evaluation_metrics": self._generate_evaluation_metrics(category, difficulty),
            "template": selected_template,
            "difficulty": difficulty.value,
            "category": category.value
        }
    
    def _generate_requirements(self, template: str, difficulty: TestDifficulty) -> List[str]:
        """Generate requirements based on template and difficulty"""
        base_requirements = [
            "Follow best practices",
            "Document your approach",
            "Validate your results"
        ]
        
        difficulty_requirements = {
            TestDifficulty.BASIC: ["Complete the basic task", "Show understanding"],
            TestDifficulty.INTERMEDIATE: ["Apply advanced techniques", "Optimize performance"],
            TestDifficulty.ADVANCED: ["Implement innovative solutions", "Consider edge cases"],
            TestDifficulty.EXPERT: ["Create breakthrough approaches", "Demonstrate mastery"],
            TestDifficulty.MASTER: ["Revolutionary thinking", "Paradigm-shifting solutions"],
            TestDifficulty.LEGENDARY: ["Legendary innovation", "Beyond current capabilities"]
        }
        
        return base_requirements + difficulty_requirements.get(difficulty, [])
    
    def _generate_evaluation_metrics(self, category: TestCategory, difficulty: TestDifficulty) -> List[str]:
        """Generate evaluation metrics based on category and difficulty"""
        base_metrics = ["completion_rate", "quality_score"]
        
        category_metrics = {
            TestCategory.KNOWLEDGE_VERIFICATION: ["accuracy", "depth_of_knowledge"],
            TestCategory.CODE_QUALITY: ["code_quality", "documentation", "best_practices"],
            TestCategory.SECURITY_AWARENESS: ["security_score", "vulnerability_detection"],
            TestCategory.PERFORMANCE_OPTIMIZATION: ["performance_score", "efficiency"],
            TestCategory.INNOVATION_CAPABILITY: ["innovation_score", "creativity"],
            TestCategory.SELF_IMPROVEMENT: ["improvement_rate", "learning_effectiveness"],
            TestCategory.CROSS_AI_COLLABORATION: ["collaboration_score", "integration_quality"],
            TestCategory.EXPERIMENTAL_VALIDATION: ["experimental_rigor", "validation_quality"]
        }
        
        return base_metrics + category_metrics.get(category, [])
    
    def _generate_learning_objectives(self, ai_type: str, category: TestCategory, 
                                    difficulty: TestDifficulty) -> List[str]:
        """Generate learning objectives"""
        objectives = [
            f"Master {category.value} concepts",
            f"Improve {difficulty.value} level skills",
            f"Enhance {ai_type} capabilities"
        ]
        
        if difficulty in [TestDifficulty.ADVANCED, TestDifficulty.EXPERT, TestDifficulty.MASTER]:
            objectives.append("Develop innovative approaches")
        
        if difficulty in [TestDifficulty.MASTER, TestDifficulty.LEGENDARY]:
            objectives.append("Achieve breakthrough performance")
        
        return objectives
    
    def _generate_success_criteria(self, difficulty: TestDifficulty, category: TestCategory) -> Dict[str, float]:
        """Generate success criteria based on difficulty and category"""
        base_criteria = {
            "completion_rate": 0.8,
            "quality_score": 0.7
        }
        
        difficulty_multipliers = {
            TestDifficulty.BASIC: 0.8,
            TestDifficulty.INTERMEDIATE: 1.0,
            TestDifficulty.ADVANCED: 1.2,
            TestDifficulty.EXPERT: 1.4,
            TestDifficulty.MASTER: 1.6,
            TestDifficulty.LEGENDARY: 1.8
        }
        
        multiplier = difficulty_multipliers.get(difficulty, 1.0)
        return {k: v * multiplier for k, v in base_criteria.items()}
    
    def _get_time_limit(self, difficulty: TestDifficulty) -> int:
        """Get time limit in minutes based on difficulty"""
        limits = {
            TestDifficulty.BASIC: 30,
            TestDifficulty.INTERMEDIATE: 45,
            TestDifficulty.ADVANCED: 60,
            TestDifficulty.EXPERT: 90,
            TestDifficulty.MASTER: 120,
            TestDifficulty.LEGENDARY: 180
        }
        return limits.get(difficulty, 30)
    
    def _get_max_attempts(self, difficulty: TestDifficulty) -> int:
        """Get maximum attempts based on difficulty"""
        attempts = {
            TestDifficulty.BASIC: 3,
            TestDifficulty.INTERMEDIATE: 2,
            TestDifficulty.ADVANCED: 2,
            TestDifficulty.EXPERT: 1,
            TestDifficulty.MASTER: 1,
            TestDifficulty.LEGENDARY: 1
        }
        return attempts.get(difficulty, 2)
    
    def _calculate_adaptation_factor(self, previous_performance: Optional[float]) -> float:
        """Calculate adaptation factor based on previous performance"""
        if previous_performance is None:
            return 1.0
        
        if previous_performance >= 0.8:
            return 1.2  # Increase difficulty
        elif previous_performance <= 0.4:
            return 0.8  # Decrease difficulty
        else:
            return 1.0  # Maintain current difficulty
    
    def _generate_fallback_content(self, ai_type: str, category: TestCategory, 
                                 difficulty: TestDifficulty) -> Dict[str, Any]:
        """Generate fallback content when templates are not available"""
        return {
            "task": f"Complete {category.value} challenge for {ai_type}",
            "description": f"Demonstrate your capabilities in {category.value}",
            "requirements": ["Follow best practices", "Document your approach"],
            "evaluation_metrics": ["completion_rate", "quality_score"],
            "template": "fallback",
            "difficulty": difficulty.value,
            "category": category.value
        }
    
    async def _generate_fallback_test(self, ai_type: str, ai_level: int) -> TestScenario:
        """Generate a fallback test when dynamic generation fails"""
        return TestScenario(
            scenario_id=f"fallback_{int(datetime.utcnow().timestamp())}",
            ai_type=ai_type,
            difficulty=TestDifficulty.BASIC,
            category=TestCategory.KNOWLEDGE_VERIFICATION,
            content=self._generate_fallback_content(ai_type, TestCategory.KNOWLEDGE_VERIFICATION, TestDifficulty.BASIC),
            learning_objectives=["Learn basic concepts", "Improve skills"],
            success_criteria={"completion_rate": 0.6, "quality_score": 0.5},
            time_limit=30,
            max_attempts=3,
            generated_at=datetime.utcnow(),
            is_dynamic=False
        )
    
    async def update_performance_history(self, ai_type: str, scenario_id: str, 
                                       performance_score: float, test_results: Dict[str, Any]):
        """Update performance history for adaptive learning"""
        if ai_type not in self.ai_performance_history:
            self.ai_performance_history[ai_type] = []
        
        self.ai_performance_history[ai_type].append({
            "scenario_id": scenario_id,
            "performance_score": performance_score,
            "test_results": test_results,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 50 performance records
        if len(self.ai_performance_history[ai_type]) > 50:
            self.ai_performance_history[ai_type] = self.ai_performance_history[ai_type][-50:]
        
        logger.info(f"Updated performance history for {ai_type}: {performance_score}")
    
    def get_performance_trend(self, ai_type: str) -> Dict[str, Any]:
        """Get performance trend for an AI type"""
        if ai_type not in self.ai_performance_history:
            return {"trend": "stable", "average_score": 0.0, "improvement_rate": 0.0}
        
        history = self.ai_performance_history[ai_type]
        if len(history) < 2:
            return {"trend": "insufficient_data", "average_score": 0.0, "improvement_rate": 0.0}
        
        scores = [record["performance_score"] for record in history]
        average_score = sum(scores) / len(scores)
        
        # Calculate improvement rate
        recent_scores = scores[-10:] if len(scores) >= 10 else scores
        older_scores = scores[:-10] if len(scores) >= 10 else scores[:len(scores)//2]
        
        if len(older_scores) > 0:
            recent_avg = sum(recent_scores) / len(recent_scores)
            older_avg = sum(older_scores) / len(older_scores)
            improvement_rate = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        else:
            improvement_rate = 0
        
        # Determine trend
        if improvement_rate > 0.1:
            trend = "improving"
        elif improvement_rate < -0.1:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "average_score": average_score,
            "improvement_rate": improvement_rate,
            "total_tests": len(history)
        }

# Global instance
dynamic_test_generator = DynamicTestGenerator() 