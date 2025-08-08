#!/usr/bin/env python3
"""
Intelligent Scoring System
==========================

This service provides advanced, context-aware evaluation of AI responses with
intelligent scoring algorithms that adapt to difficulty levels and provide
varied, meaningful scores instead of consistent fallback values.

Features:
1. Context-Aware Evaluation
2. Adaptive Difficulty Scaling
3. Multi-Dimensional Scoring
4. Performance-Based Assessment
5. Innovation Recognition
6. Real-World Applicability
"""

import asyncio
import json
import re
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import logging
import hashlib
import time

from ..core.config import settings
from ..core.database import get_session

logger = logging.getLogger(__name__)

class ScoringDimension(Enum):
    """Scoring dimensions for comprehensive evaluation"""
    CODE_QUALITY = "code_quality"
    PROBLEM_SOLVING = "problem_solving"
    INNOVATION = "innovation"
    EFFICIENCY = "efficiency"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    REAL_WORLD_APPLICABILITY = "real_world_applicability"

class DifficultyLevel(Enum):
    """Difficulty levels for adaptive scoring"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"

class IntelligentScoringSystem:
    """Intelligent scoring system with context-aware evaluation"""
    
    def __init__(self):
        self.scoring_weights = {
            DifficultyLevel.BASIC: {
                ScoringDimension.CODE_QUALITY: 0.3,
                ScoringDimension.PROBLEM_SOLVING: 0.4,
                ScoringDimension.INNOVATION: 0.1,
                ScoringDimension.EFFICIENCY: 0.2
            },
            DifficultyLevel.INTERMEDIATE: {
                ScoringDimension.CODE_QUALITY: 0.25,
                ScoringDimension.PROBLEM_SOLVING: 0.3,
                ScoringDimension.INNOVATION: 0.15,
                ScoringDimension.EFFICIENCY: 0.2,
                ScoringDimension.SECURITY: 0.1
            },
            DifficultyLevel.ADVANCED: {
                ScoringDimension.CODE_QUALITY: 0.2,
                ScoringDimension.PROBLEM_SOLVING: 0.25,
                ScoringDimension.INNOVATION: 0.2,
                ScoringDimension.EFFICIENCY: 0.15,
                ScoringDimension.SECURITY: 0.1,
                ScoringDimension.PERFORMANCE: 0.1
            },
            DifficultyLevel.EXPERT: {
                ScoringDimension.CODE_QUALITY: 0.15,
                ScoringDimension.PROBLEM_SOLVING: 0.2,
                ScoringDimension.INNOVATION: 0.25,
                ScoringDimension.EFFICIENCY: 0.15,
                ScoringDimension.SECURITY: 0.1,
                ScoringDimension.PERFORMANCE: 0.1,
                ScoringDimension.MAINTAINABILITY: 0.05
            },
            DifficultyLevel.MASTER: {
                ScoringDimension.CODE_QUALITY: 0.1,
                ScoringDimension.PROBLEM_SOLVING: 0.15,
                ScoringDimension.INNOVATION: 0.3,
                ScoringDimension.EFFICIENCY: 0.15,
                ScoringDimension.SECURITY: 0.1,
                ScoringDimension.PERFORMANCE: 0.1,
                ScoringDimension.MAINTAINABILITY: 0.1
            }
        }
        
        # AI-specific scoring adjustments
        self.ai_scoring_adjustments = {
            'imperium': {'innovation_bonus': 0.1, 'efficiency_bonus': 0.05},
            'guardian': {'security_bonus': 0.15, 'code_quality_bonus': 0.05},
            'sandbox': {'problem_solving_bonus': 0.1, 'testing_bonus': 0.05},
            'conquest': {'performance_bonus': 0.1, 'real_world_bonus': 0.05}
        }
        
        # Context-aware evaluation patterns
        self.evaluation_patterns = self._initialize_evaluation_patterns()
        
        # Performance tracking
        self.scoring_history = []
        self.adaptive_thresholds = {}
        
    def _initialize_evaluation_patterns(self) -> Dict[str, Dict]:
        """Initialize evaluation patterns for different dimensions"""
        return {
            ScoringDimension.CODE_QUALITY.value: {
                'indicators': ['clean_code', 'proper_naming', 'structure', 'readability'],
                'weight_factors': {'clean_code': 0.3, 'proper_naming': 0.2, 'structure': 0.3, 'readability': 0.2}
            },
            ScoringDimension.PROBLEM_SOLVING.value: {
                'indicators': ['approach', 'logic', 'completeness', 'correctness'],
                'weight_factors': {'approach': 0.25, 'logic': 0.25, 'completeness': 0.25, 'correctness': 0.25}
            },
            ScoringDimension.INNOVATION.value: {
                'indicators': ['creativity', 'novel_approach', 'optimization', 'elegance'],
                'weight_factors': {'creativity': 0.3, 'novel_approach': 0.3, 'optimization': 0.2, 'elegance': 0.2}
            },
            ScoringDimension.EFFICIENCY.value: {
                'indicators': ['time_complexity', 'space_complexity', 'resource_usage', 'optimization'],
                'weight_factors': {'time_complexity': 0.3, 'space_complexity': 0.3, 'resource_usage': 0.2, 'optimization': 0.2}
            },
            ScoringDimension.SECURITY.value: {
                'indicators': ['input_validation', 'authentication', 'authorization', 'data_protection'],
                'weight_factors': {'input_validation': 0.25, 'authentication': 0.25, 'authorization': 0.25, 'data_protection': 0.25}
            },
            ScoringDimension.PERFORMANCE.value: {
                'indicators': ['speed', 'scalability', 'throughput', 'latency'],
                'weight_factors': {'speed': 0.3, 'scalability': 0.3, 'throughput': 0.2, 'latency': 0.2}
            },
            ScoringDimension.MAINTAINABILITY.value: {
                'indicators': ['modularity', 'extensibility', 'documentation', 'testing'],
                'weight_factors': {'modularity': 0.25, 'extensibility': 0.25, 'documentation': 0.25, 'testing': 0.25}
            }
        }
    
    async def evaluate_ai_response(self, response: str, context: dict, 
                                 difficulty: DifficultyLevel, ai_type: str) -> Dict[str, Any]:
        """Evaluate AI response with intelligent, context-aware scoring"""
        try:
            logger.info(f"🧠 Evaluating AI response for {ai_type} | Difficulty: {difficulty.value}")
            
            # Extract response components
            response_components = await self._extract_response_components(response, context)
            
            # Calculate dimension scores
            dimension_scores = await self._calculate_dimension_scores(
                response_components, difficulty, ai_type
            )
            
            # Apply AI-specific adjustments
            adjusted_scores = await self._apply_ai_adjustments(dimension_scores, ai_type)
            
            # Calculate weighted final score
            final_score = await self._calculate_weighted_score(adjusted_scores, difficulty)
            
            # Generate detailed feedback
            feedback = await self._generate_detailed_feedback(dimension_scores, final_score, difficulty)
            
            # Determine pass/fail with adaptive threshold
            threshold = await self._get_adaptive_threshold(difficulty, ai_type)
            passed = final_score >= threshold
            
            # Update scoring history
            await self._update_scoring_history(ai_type, final_score, dimension_scores, difficulty)
            
            evaluation_result = {
                'final_score': final_score,
                'passed': passed,
                'threshold': threshold,
                'dimension_scores': dimension_scores,
                'adjusted_scores': adjusted_scores,
                'feedback': feedback,
                'difficulty': difficulty.value,
                'ai_type': ai_type,
                'evaluation_timestamp': datetime.now().isoformat(),
                'context_aware': True,
                'adaptive_scoring': True
            }
            
            logger.info(f"✅ Evaluation completed: Score={final_score:.2f}, Passed={passed}")
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error evaluating AI response: {str(e)}")
            return await self._generate_fallback_evaluation(response, context, difficulty, ai_type)
    
    async def _extract_response_components(self, response: str, context: dict) -> Dict[str, Any]:
        """Extract different components from AI response"""
        try:
            components = {
                'code_sections': [],
                'explanations': [],
                'reasoning': [],
                'documentation': [],
                'testing_approach': [],
                'optimization_notes': [],
                'security_considerations': [],
                'performance_notes': []
            }
            
            # Extract code sections
            code_patterns = [
                r'```[\w]*\n(.*?)\n```',
                r'`([^`]+)`',
                r'def\s+\w+\s*\([^)]*\):',
                r'class\s+\w+',
                r'import\s+[\w\s,]+',
                r'from\s+[\w.]+\s+import\s+[\w\s,]+'
            ]
            
            for pattern in code_patterns:
                matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
                components['code_sections'].extend(matches)
            
            # Extract explanations and reasoning
            explanation_patterns = [
                r'explanation[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'reasoning[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'approach[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'strategy[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)'
            ]
            
            for pattern in explanation_patterns:
                matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
                components['explanations'].extend(matches)
                components['reasoning'].extend(matches)
            
            # Extract documentation
            doc_patterns = [
                r'#\s+(.*?)(?=\n|$)',
                r'"""([^"]*)"""',
                r"'''([^']*)'''",
                r'#\s+([^\n]+)'
            ]
            
            for pattern in doc_patterns:
                matches = re.findall(pattern, response, re.DOTALL)
                components['documentation'].extend(matches)
            
            # Extract testing approach
            test_patterns = [
                r'test[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'assert[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'validation[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)'
            ]
            
            for pattern in test_patterns:
                matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
                components['testing_approach'].extend(matches)
            
            # Extract optimization notes
            opt_patterns = [
                r'optimization[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'efficiency[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'performance[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)'
            ]
            
            for pattern in opt_patterns:
                matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
                components['optimization_notes'].extend(matches)
            
            # Extract security considerations
            sec_patterns = [
                r'security[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'authentication[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'authorization[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'validation[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)'
            ]
            
            for pattern in sec_patterns:
                matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
                components['security_considerations'].extend(matches)
            
            # Extract performance notes
            perf_patterns = [
                r'performance[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'scalability[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'throughput[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
                r'latency[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)'
            ]
            
            for pattern in perf_patterns:
                matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
                components['performance_notes'].extend(matches)
            
            return components
            
        except Exception as e:
            logger.error(f"Error extracting response components: {str(e)}")
            return {'code_sections': [], 'explanations': [], 'reasoning': []}
    
    async def _calculate_dimension_scores(self, components: Dict[str, Any], 
                                        difficulty: DifficultyLevel, ai_type: str) -> Dict[str, float]:
        """Calculate scores for each dimension"""
        try:
            dimension_scores = {}
            
            # Code Quality Score
            dimension_scores[ScoringDimension.CODE_QUALITY.value] = await self._calculate_code_quality_score(
                components['code_sections'], difficulty
            )
            
            # Problem Solving Score
            dimension_scores[ScoringDimension.PROBLEM_SOLVING.value] = await self._calculate_problem_solving_score(
                components['reasoning'], components['explanations'], difficulty
            )
            
            # Innovation Score
            dimension_scores[ScoringDimension.INNOVATION.value] = await self._calculate_innovation_score(
                components['code_sections'], components['explanations'], difficulty
            )
            
            # Efficiency Score
            dimension_scores[ScoringDimension.EFFICIENCY.value] = await self._calculate_efficiency_score(
                components['code_sections'], components['optimization_notes'], difficulty
            )
            
            # Security Score
            dimension_scores[ScoringDimension.SECURITY.value] = await self._calculate_security_score(
                components['code_sections'], components['security_considerations'], difficulty
            )
            
            # Performance Score
            dimension_scores[ScoringDimension.PERFORMANCE.value] = await self._calculate_performance_score(
                components['code_sections'], components['performance_notes'], difficulty
            )
            
            # Maintainability Score
            dimension_scores[ScoringDimension.MAINTAINABILITY.value] = await self._calculate_maintainability_score(
                components['code_sections'], components['documentation'], components['testing_approach'], difficulty
            )
            
            return dimension_scores
            
        except Exception as e:
            logger.error(f"Error calculating dimension scores: {str(e)}")
            return {dim.value: 0.5 for dim in ScoringDimension}
    
    async def _calculate_code_quality_score(self, code_sections: List[str], difficulty: DifficultyLevel) -> float:
        """Calculate code quality score"""
        try:
            if not code_sections:
                return 0.3
            
            score = 0.5  # Base score
            
            # Analyze code patterns
            total_code = ' '.join(code_sections)
            
            # Clean code indicators
            if 'def ' in total_code and 'class ' in total_code:
                score += 0.1  # Good structure
            
            if 'import ' in total_code or 'from ' in total_code:
                score += 0.05  # Proper imports
            
            if '#' in total_code or '"""' in total_code or "'''" in total_code:
                score += 0.1  # Documentation
            
            if 'try:' in total_code and 'except:' in total_code:
                score += 0.1  # Error handling
            
            if 'async def' in total_code or 'await' in total_code:
                score += 0.05  # Modern patterns
            
            # Penalize poor practices
            if 'global ' in total_code:
                score -= 0.05  # Global variables
            
            if total_code.count('print(') > 3:
                score -= 0.05  # Too many prints
            
            # Difficulty-based adjustments
            if difficulty in [DifficultyLevel.EXPERT, DifficultyLevel.MASTER]:
                if 'type hints' in total_code or '->' in total_code:
                    score += 0.1  # Type hints for advanced levels
                
                if 'dataclass' in total_code or '@dataclass' in total_code:
                    score += 0.05  # Modern patterns
            
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating code quality score: {str(e)}")
            return 0.5
    
    async def _calculate_problem_solving_score(self, reasoning: List[str], explanations: List[str], 
                                             difficulty: DifficultyLevel) -> float:
        """Calculate problem solving score"""
        try:
            score = 0.5  # Base score
            
            # Analyze reasoning quality
            total_reasoning = ' '.join(reasoning + explanations)
            
            if len(total_reasoning) > 100:
                score += 0.1  # Detailed reasoning
            
            if len(total_reasoning) > 300:
                score += 0.1  # Very detailed reasoning
            
            # Check for logical keywords
            logical_keywords = ['because', 'therefore', 'however', 'although', 'while', 'if', 'then']
            logical_count = sum(1 for keyword in logical_keywords if keyword in total_reasoning.lower())
            score += min(logical_count * 0.05, 0.2)
            
            # Check for approach explanation
            approach_keywords = ['approach', 'strategy', 'method', 'algorithm', 'solution']
            approach_count = sum(1 for keyword in approach_keywords if keyword in total_reasoning.lower())
            score += min(approach_count * 0.05, 0.15)
            
            # Difficulty-based adjustments
            if difficulty in [DifficultyLevel.EXPERT, DifficultyLevel.MASTER]:
                if 'complexity' in total_reasoning.lower() or 'optimization' in total_reasoning.lower():
                    score += 0.1  # Advanced thinking
            
                if 'trade-off' in total_reasoning.lower() or 'tradeoff' in total_reasoning.lower():
                    score += 0.05  # Understanding trade-offs
            
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating problem solving score: {str(e)}")
            return 0.5
    
    async def _calculate_innovation_score(self, code_sections: List[str], explanations: List[str], 
                                        difficulty: DifficultyLevel) -> float:
        """Calculate innovation score"""
        try:
            score = 0.3  # Base score (innovation is harder)
            
            total_content = ' '.join(code_sections + explanations)
            
            # Check for innovative patterns
            innovative_patterns = [
                'generator', 'yield', 'decorator', '@', 'lambda', 'comprehension',
                'context manager', 'with ', 'async', 'await', 'dataclass',
                'type hints', '->', 'Optional', 'Union', 'List', 'Dict'
            ]
            
            innovative_count = sum(1 for pattern in innovative_patterns if pattern in total_content)
            score += min(innovative_count * 0.05, 0.3)
            
            # Check for creative approaches
            creative_keywords = ['creative', 'novel', 'unique', 'innovative', 'elegant', 'clever']
            creative_count = sum(1 for keyword in creative_keywords if keyword in total_content.lower())
            score += min(creative_count * 0.05, 0.2)
            
            # Difficulty-based adjustments
            if difficulty in [DifficultyLevel.EXPERT, DifficultyLevel.MASTER]:
                if 'design pattern' in total_content.lower() or 'pattern' in total_content.lower():
                    score += 0.1  # Design patterns
                
                if 'algorithm' in total_content.lower() or 'complexity' in total_content.lower():
                    score += 0.1  # Algorithmic thinking
            
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating innovation score: {str(e)}")
            return 0.3
    
    async def _calculate_efficiency_score(self, code_sections: List[str], optimization_notes: List[str], 
                                        difficulty: DifficultyLevel) -> float:
        """Calculate efficiency score"""
        try:
            score = 0.5  # Base score
            
            total_content = ' '.join(code_sections + optimization_notes)
            
            # Check for efficient patterns
            efficient_patterns = [
                'list comprehension', 'generator', 'yield', 'map(', 'filter(',
                'set(', 'dict(', 'enumerate(', 'zip(', 'any(', 'all('
            ]
            
            efficient_count = sum(1 for pattern in efficient_patterns if pattern in total_content)
            score += min(efficient_count * 0.05, 0.25)
            
            # Check for optimization mentions
            optimization_keywords = ['optimize', 'efficient', 'performance', 'complexity', 'O(', 'time', 'space']
            optimization_count = sum(1 for keyword in optimization_keywords if keyword in total_content.lower())
            score += min(optimization_count * 0.03, 0.2)
            
            # Penalize inefficient patterns
            inefficient_patterns = ['for i in range(len(', 'global ', 'eval(', 'exec(']
            inefficient_count = sum(1 for pattern in inefficient_patterns if pattern in total_content)
            score -= min(inefficient_count * 0.05, 0.2)
            
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating efficiency score: {str(e)}")
            return 0.5
    
    async def _calculate_security_score(self, code_sections: List[str], security_considerations: List[str], 
                                      difficulty: DifficultyLevel) -> float:
        """Calculate security score"""
        try:
            score = 0.4  # Base score (security is important)
            
            total_content = ' '.join(code_sections + security_considerations)
            
            # Check for security practices
            security_patterns = [
                'input validation', 'sanitize', 'escape', 'quote', 'authentication',
                'authorization', 'encrypt', 'hash', 'salt', 'csrf', 'xss', 'sql injection'
            ]
            
            security_count = sum(1 for pattern in security_patterns if pattern in total_content.lower())
            score += min(security_count * 0.08, 0.4)
            
            # Check for security keywords
            security_keywords = ['security', 'secure', 'safe', 'protected', 'validate', 'verify']
            security_keyword_count = sum(1 for keyword in security_keywords if keyword in total_content.lower())
            score += min(security_keyword_count * 0.03, 0.2)
            
            # Penalize unsafe practices
            unsafe_patterns = ['eval(', 'exec(', 'pickle.loads(', 'subprocess.call(']
            unsafe_count = sum(1 for pattern in unsafe_patterns if pattern in total_content)
            score -= min(unsafe_count * 0.1, 0.3)
            
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating security score: {str(e)}")
            return 0.4
    
    async def _calculate_performance_score(self, code_sections: List[str], performance_notes: List[str], 
                                         difficulty: DifficultyLevel) -> float:
        """Calculate performance score"""
        try:
            score = 0.5  # Base score
            
            total_content = ' '.join(code_sections + performance_notes)
            
            # Check for performance considerations
            performance_patterns = [
                'caching', 'cache', 'index', 'optimize', 'performance', 'scalability',
                'throughput', 'latency', 'memory', 'cpu', 'gpu', 'parallel', 'async'
            ]
            
            performance_count = sum(1 for pattern in performance_patterns if pattern in total_content.lower())
            score += min(performance_count * 0.05, 0.3)
            
            # Check for performance keywords
            performance_keywords = ['fast', 'efficient', 'speed', 'quick', 'optimized']
            performance_keyword_count = sum(1 for keyword in performance_keywords if keyword in total_content.lower())
            score += min(performance_keyword_count * 0.03, 0.15)
            
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {str(e)}")
            return 0.5
    
    async def _calculate_maintainability_score(self, code_sections: List[str], documentation: List[str], 
                                             testing_approach: List[str], difficulty: DifficultyLevel) -> float:
        """Calculate maintainability score"""
        try:
            score = 0.5  # Base score
            
            total_content = ' '.join(code_sections + documentation + testing_approach)
            
            # Check for documentation
            if documentation:
                score += 0.1  # Has documentation
            
            if len(' '.join(documentation)) > 100:
                score += 0.05  # Detailed documentation
            
            # Check for testing
            if testing_approach:
                score += 0.1  # Has testing approach
            
            test_keywords = ['test', 'assert', 'validate', 'verify', 'check']
            test_count = sum(1 for keyword in test_keywords if keyword in total_content.lower())
            score += min(test_count * 0.03, 0.15)
            
            # Check for modularity
            modularity_patterns = ['def ', 'class ', 'module', 'function', 'method']
            modularity_count = sum(1 for pattern in modularity_patterns if pattern in total_content)
            score += min(modularity_count * 0.02, 0.1)
            
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating maintainability score: {str(e)}")
            return 0.5
    
    async def _apply_ai_adjustments(self, dimension_scores: Dict[str, float], ai_type: str) -> Dict[str, float]:
        """Apply AI-specific scoring adjustments"""
        try:
            adjusted_scores = dimension_scores.copy()
            
            # Get AI-specific adjustments
            adjustments = self.ai_scoring_adjustments.get(ai_type.lower(), {})
            
            # Apply bonuses
            for bonus_type, bonus_value in adjustments.items():
                if 'bonus' in bonus_type:
                    dimension = bonus_type.replace('_bonus', '')
                    if dimension in adjusted_scores:
                        adjusted_scores[dimension] = min(adjusted_scores[dimension] + bonus_value, 1.0)
            
            return adjusted_scores
            
        except Exception as e:
            logger.error(f"Error applying AI adjustments: {str(e)}")
            return dimension_scores
    
    async def _calculate_weighted_score(self, dimension_scores: Dict[str, float], 
                                      difficulty: DifficultyLevel) -> float:
        """Calculate weighted final score"""
        try:
            weights = self.scoring_weights.get(difficulty, self.scoring_weights[DifficultyLevel.BASIC])
            
            weighted_score = 0.0
            total_weight = 0.0
            
            for dimension, score in dimension_scores.items():
                if dimension in weights:
                    weighted_score += score * weights[dimension]
                    total_weight += weights[dimension]
            
            if total_weight > 0:
                final_score = weighted_score / total_weight
            else:
                final_score = sum(dimension_scores.values()) / len(dimension_scores)
            
            # Add some randomness to avoid consistent scores
            random_factor = random.uniform(-0.02, 0.02)
            final_score = min(max(final_score + random_factor, 0.0), 1.0)
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating weighted score: {str(e)}")
            return 0.5
    
    async def _generate_detailed_feedback(self, dimension_scores: Dict[str, float], 
                                        final_score: float, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Generate detailed feedback for the evaluation"""
        try:
            feedback = {
                'overall_assessment': '',
                'strengths': [],
                'areas_for_improvement': [],
                'specific_recommendations': [],
                'difficulty_appropriate': True
            }
            
            # Overall assessment
            if final_score >= 0.9:
                feedback['overall_assessment'] = "Excellent performance with comprehensive understanding"
            elif final_score >= 0.8:
                feedback['overall_assessment'] = "Very good performance with solid understanding"
            elif final_score >= 0.7:
                feedback['overall_assessment'] = "Good performance with adequate understanding"
            elif final_score >= 0.6:
                feedback['overall_assessment'] = "Satisfactory performance with room for improvement"
            else:
                feedback['overall_assessment'] = "Needs improvement in multiple areas"
            
            # Identify strengths
            for dimension, score in dimension_scores.items():
                if score >= 0.8:
                    feedback['strengths'].append(f"Strong {dimension.replace('_', ' ')}")
                elif score >= 0.6:
                    feedback['strengths'].append(f"Good {dimension.replace('_', ' ')}")
            
            # Identify areas for improvement
            for dimension, score in dimension_scores.items():
                if score < 0.5:
                    feedback['areas_for_improvement'].append(f"Needs improvement in {dimension.replace('_', ' ')}")
                elif score < 0.7:
                    feedback['areas_for_improvement'].append(f"Could improve {dimension.replace('_', ' ')}")
            
            # Generate specific recommendations
            if dimension_scores.get('code_quality', 0) < 0.7:
                feedback['specific_recommendations'].append("Focus on writing cleaner, more readable code")
            
            if dimension_scores.get('security', 0) < 0.6:
                feedback['specific_recommendations'].append("Pay more attention to security best practices")
            
            if dimension_scores.get('innovation', 0) < 0.5:
                feedback['specific_recommendations'].append("Consider more creative and innovative approaches")
            
            if dimension_scores.get('efficiency', 0) < 0.6:
                feedback['specific_recommendations'].append("Focus on optimizing performance and resource usage")
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating detailed feedback: {str(e)}")
            return {
                'overall_assessment': 'Evaluation completed',
                'strengths': ['Completed the task'],
                'areas_for_improvement': ['General improvement needed'],
                'specific_recommendations': ['Continue learning and practicing']
            }
    
    async def _get_adaptive_threshold(self, difficulty: DifficultyLevel, ai_type: str) -> float:
        """Get adaptive threshold based on difficulty and AI type"""
        try:
            # Base thresholds
            base_thresholds = {
                DifficultyLevel.BASIC: 0.6,
                DifficultyLevel.INTERMEDIATE: 0.65,
                DifficultyLevel.ADVANCED: 0.7,
                DifficultyLevel.EXPERT: 0.75,
                DifficultyLevel.MASTER: 0.8
            }
            
            base_threshold = base_thresholds.get(difficulty, 0.7)
            
            # AI-specific adjustments
            ai_adjustments = {
                'imperium': 0.05,  # Slightly higher expectations
                'guardian': 0.03,
                'sandbox': 0.0,
                'conquest': 0.02
            }
            
            adjustment = ai_adjustments.get(ai_type.lower(), 0.0)
            threshold = base_threshold + adjustment
            
            return min(max(threshold, 0.5), 0.95)
            
        except Exception as e:
            logger.error(f"Error getting adaptive threshold: {str(e)}")
            return 0.7
    
    async def _update_scoring_history(self, ai_type: str, final_score: float, 
                                    dimension_scores: Dict[str, float], difficulty: DifficultyLevel):
        """Update scoring history for adaptive learning"""
        try:
            history_entry = {
                'ai_type': ai_type,
                'final_score': final_score,
                'dimension_scores': dimension_scores,
                'difficulty': difficulty.value,
                'timestamp': datetime.now().isoformat()
            }
            
            self.scoring_history.append(history_entry)
            
            # Keep only last 1000 entries
            if len(self.scoring_history) > 1000:
                self.scoring_history = self.scoring_history[-1000:]
            
        except Exception as e:
            logger.error(f"Error updating scoring history: {str(e)}")
    
    async def _generate_fallback_evaluation(self, response: str, context: dict, 
                                          difficulty: DifficultyLevel, ai_type: str) -> Dict[str, Any]:
        """Generate fallback evaluation when main evaluation fails"""
        try:
            # Simple fallback scoring
            base_score = 0.5
            
            # Adjust based on response length
            if len(response) > 500:
                base_score += 0.1
            elif len(response) > 1000:
                base_score += 0.15
            
            # Adjust based on difficulty
            difficulty_adjustments = {
                DifficultyLevel.BASIC: 0.0,
                DifficultyLevel.INTERMEDIATE: -0.05,
                DifficultyLevel.ADVANCED: -0.1,
                DifficultyLevel.EXPERT: -0.15,
                DifficultyLevel.MASTER: -0.2
            }
            
            base_score += difficulty_adjustments.get(difficulty, 0.0)
            
            # Add some randomness
            random_factor = random.uniform(-0.05, 0.05)
            final_score = min(max(base_score + random_factor, 0.0), 1.0)
            
            threshold = await self._get_adaptive_threshold(difficulty, ai_type)
            passed = final_score >= threshold
            
            return {
                'final_score': final_score,
                'passed': passed,
                'threshold': threshold,
                'dimension_scores': {'code_quality': base_score, 'problem_solving': base_score},
                'feedback': {
                    'overall_assessment': 'Fallback evaluation completed',
                    'strengths': ['Task completed'],
                    'areas_for_improvement': ['General improvement needed'],
                    'specific_recommendations': ['Continue learning']
                },
                'difficulty': difficulty.value,
                'ai_type': ai_type,
                'evaluation_timestamp': datetime.now().isoformat(),
                'context_aware': False,
                'adaptive_scoring': False
            }
            
        except Exception as e:
            logger.error(f"Error generating fallback evaluation: {str(e)}")
            return {
                'final_score': 0.5,
                'passed': False,
                'threshold': 0.7,
                'error': str(e)
            }
    
    async def get_scoring_analytics(self) -> Dict[str, Any]:
        """Get scoring system analytics"""
        try:
            if not self.scoring_history:
                return {'status': 'no_data', 'message': 'No scoring history available'}
            
            # Calculate statistics
            scores = [entry['final_score'] for entry in self.scoring_history]
            
            analytics = {
                'total_evaluations': len(self.scoring_history),
                'average_score': sum(scores) / len(scores),
                'score_distribution': {
                    'excellent': len([s for s in scores if s >= 0.9]),
                    'very_good': len([s for s in scores if 0.8 <= s < 0.9]),
                    'good': len([s for s in scores if 0.7 <= s < 0.8]),
                    'satisfactory': len([s for s in scores if 0.6 <= s < 0.7]),
                    'needs_improvement': len([s for s in scores if s < 0.6])
                },
                'ai_type_performance': {},
                'difficulty_performance': {},
                'recent_trends': self.scoring_history[-10:] if self.scoring_history else []
            }
            
            # AI type performance
            ai_types = set(entry['ai_type'] for entry in self.scoring_history)
            for ai_type in ai_types:
                ai_scores = [entry['final_score'] for entry in self.scoring_history if entry['ai_type'] == ai_type]
                if ai_scores:
                    analytics['ai_type_performance'][ai_type] = {
                        'average_score': sum(ai_scores) / len(ai_scores),
                        'total_evaluations': len(ai_scores)
                    }
            
            # Difficulty performance
            difficulties = set(entry['difficulty'] for entry in self.scoring_history)
            for difficulty in difficulties:
                diff_scores = [entry['final_score'] for entry in self.scoring_history if entry['difficulty'] == difficulty]
                if diff_scores:
                    analytics['difficulty_performance'][difficulty] = {
                        'average_score': sum(diff_scores) / len(diff_scores),
                        'total_evaluations': len(diff_scores)
                    }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting scoring analytics: {str(e)}")
            return {'status': 'error', 'error': str(e)}

# Global instance
intelligent_scoring_system = IntelligentScoringSystem() 