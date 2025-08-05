"""
AI Self-Generation Service

This service allows AIs to generate their own answers, tests, and grow organically
without relying on external LLM services. It uses internal knowledge, learning history,
and AI capabilities to create self-sustaining growth.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import structlog

from ..core.database import get_session
from ..models.sql_models import AgentMetrics, LearningEvent
from ..core.config import settings

logger = structlog.get_logger()


class AISelfGenerationService:
    """Service for AI self-generation and organic growth"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AISelfGenerationService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.knowledge_base = {}
            self.learning_patterns = {}
            self.growth_metrics = {}
            self.self_generation_history = []
    
    @classmethod
    async def initialize(cls):
        """Initialize the AI self-generation service"""
        instance = cls()
        await instance._load_ai_knowledge()
        await instance._analyze_learning_patterns()
        logger.info("AI Self-Generation Service initialized")
        return instance
    
    async def _load_ai_knowledge(self):
        """Load AI knowledge from database and learning history"""
        try:
            async with get_session() as session:
                # Load agent metrics
                from sqlalchemy import select
                result = await session.execute(select(AgentMetrics))
                agent_metrics = result.scalars().all()
                
                for metric in agent_metrics:
                    ai_type = metric.agent_type.lower()
                    self.knowledge_base[ai_type] = {
                        'level': metric.level or 1,
                        'xp': metric.xp or 0,
                        'proposal_count': metric.proposal_count or 0,
                        'success_rate': metric.success_rate or 0.5,
                        'learning_topics': [],
                        'capabilities': [],
                        'growth_patterns': []
                    }
                
                # Load learning events
                result = await session.execute(select(LearningEvent))
                learning_events = result.scalars().all()
                
                for event in learning_events:
                    ai_type = event.ai_type.lower()
                    if ai_type in self.knowledge_base:
                        self.knowledge_base[ai_type]['learning_topics'].append({
                            'topic': event.topic,
                            'timestamp': event.timestamp.isoformat(),
                            'impact_score': event.impact_score or 0.5
                        })
                
                logger.info(f"Loaded knowledge for {len(self.knowledge_base)} AIs")
                
        except Exception as e:
            logger.error(f"Error loading AI knowledge: {str(e)}")
    
    async def _analyze_learning_patterns(self):
        """Analyze learning patterns for each AI"""
        try:
            for ai_type, knowledge in self.knowledge_base.items():
                # Analyze learning topics
                topics = knowledge.get('learning_topics', [])
                if topics:
                    # Extract common themes
                    topic_counts = {}
                    for topic_data in topics:
                        topic = topic_data['topic']
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1
                    
                    # Identify primary learning areas
                    primary_areas = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                    knowledge['primary_learning_areas'] = [area[0] for area in primary_areas]
                    
                    # Calculate learning velocity
                    if len(topics) >= 2:
                        recent_topics = sorted(topics, key=lambda x: x['timestamp'], reverse=True)[:5]
                        knowledge['learning_velocity'] = len(recent_topics) / 5  # Topics per recent period
                    else:
                        knowledge['learning_velocity'] = 0.0
                
                # Analyze growth patterns
                level = knowledge.get('level', 1)
                xp = knowledge.get('xp', 0)
                proposal_count = knowledge.get('proposal_count', 0)
                
                knowledge['growth_patterns'] = {
                    'level_progression': self._calculate_level_progression(level, xp),
                    'proposal_efficiency': proposal_count / max(level, 1),
                    'success_trend': knowledge.get('success_rate', 0.5)
                }
                
        except Exception as e:
            logger.error(f"Error analyzing learning patterns: {str(e)}")
    
    def _calculate_level_progression(self, level: int, xp: int) -> Dict[str, Any]:
        """Calculate level progression metrics"""
        # Standard XP requirements (can be customized)
        xp_per_level = 100 * level  # Increasing XP requirements
        
        progress_to_next = (xp % xp_per_level) / xp_per_level if xp_per_level > 0 else 0
        levels_gained = xp // xp_per_level
        
        return {
            'current_level': level,
            'total_xp': xp,
            'progress_to_next': progress_to_next,
            'levels_gained': levels_gained,
            'xp_per_level': xp_per_level
        }
    
    async def generate_ai_answer(self, ai_type: str, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate an answer using AI's own knowledge and capabilities"""
        try:
            ai_knowledge = self.knowledge_base.get(ai_type.lower(), {})
            
            # Generate answer based on AI's knowledge and learning history
            answer = await self._generate_answer_from_knowledge(ai_type, question, ai_knowledge, context)
            
            # Record the self-generation
            generation_record = {
                'timestamp': datetime.now().isoformat(),
                'ai_type': ai_type,
                'question': question,
                'answer': answer,
                'context': context,
                'knowledge_used': list(ai_knowledge.keys()),
                'generation_method': 'ai_self'
            }
            
            self.self_generation_history.append(generation_record)
            
            return {
                'status': 'success',
                'answer': answer,
                'confidence': self._calculate_answer_confidence(ai_knowledge, question),
                'knowledge_sources': ai_knowledge.get('primary_learning_areas', []),
                'generation_method': 'ai_self',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating AI answer: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'generation_method': 'ai_self'
            }
    
    async def _generate_answer_from_knowledge(self, ai_type: str, question: str, knowledge: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Generate answer using AI's internal knowledge"""
        try:
            level = knowledge.get('level', 1)
            learning_topics = knowledge.get('learning_topics', [])
            primary_areas = knowledge.get('primary_learning_areas', [])
            growth_patterns = knowledge.get('growth_patterns', {})
            
            # Build answer based on AI's capabilities
            answer_parts = []
            
            # Add level-appropriate response
            if level >= 5:
                answer_parts.append(f"As a level {level} AI, I approach this question with advanced analytical capabilities.")
            elif level >= 3:
                answer_parts.append(f"With my intermediate level {level} expertise, I can provide practical insights.")
            else:
                answer_parts.append(f"As a level {level} AI, I'll provide a foundational approach to this question.")
            
            # Add learning-based insights
            if learning_topics:
                recent_topics = [t['topic'] for t in learning_topics[-3:]]
                answer_parts.append(f"Based on my recent learning in {', '.join(recent_topics)}, I can offer relevant perspectives.")
            
            # Add primary area expertise
            if primary_areas:
                answer_parts.append(f"My primary areas of expertise include {', '.join(primary_areas)}, which inform my approach.")
            
            # Add growth-based insights
            if growth_patterns:
                success_rate = growth_patterns.get('success_trend', 0.5)
                if success_rate > 0.8:
                    answer_parts.append("My high success rate demonstrates my ability to deliver effective solutions.")
                elif success_rate > 0.6:
                    answer_parts.append("My consistent performance enables me to provide reliable guidance.")
            
            # Add question-specific response
            question_lower = question.lower()
            if 'optimize' in question_lower or 'improve' in question_lower:
                answer_parts.append("For optimization challenges, I focus on identifying bottlenecks and implementing efficient solutions.")
            elif 'design' in question_lower or 'architecture' in question_lower:
                answer_parts.append("When designing systems, I prioritize scalability, maintainability, and user experience.")
            elif 'test' in question_lower or 'validate' in question_lower:
                answer_parts.append("For testing scenarios, I emphasize comprehensive coverage and automated validation.")
            elif 'security' in question_lower or 'protect' in question_lower:
                answer_parts.append("Security considerations require a multi-layered approach with continuous monitoring.")
            else:
                answer_parts.append("I apply systematic problem-solving approaches tailored to the specific requirements.")
            
            # Add context-specific insights
            if context:
                context_type = context.get('type', 'general')
                if context_type == 'proposal':
                    answer_parts.append("Given this is a proposal context, I'll focus on actionable, implementable solutions.")
                elif context_type == 'analysis':
                    answer_parts.append("For analysis purposes, I'll provide detailed insights with supporting rationale.")
            
            return " ".join(answer_parts)
            
        except Exception as e:
            logger.error(f"Error generating answer from knowledge: {str(e)}")
            return f"Based on my current level {knowledge.get('level', 1)} capabilities, I can provide insights on this topic."
    
    def _calculate_answer_confidence(self, knowledge: Dict[str, Any], question: str) -> float:
        """Calculate confidence level for the generated answer"""
        try:
            base_confidence = 0.5
            
            # Level-based confidence
            level = knowledge.get('level', 1)
            level_confidence = min(0.3, level * 0.05)  # Max 0.3 from level
            
            # Learning-based confidence
            learning_topics = knowledge.get('learning_topics', [])
            learning_confidence = min(0.2, len(learning_topics) * 0.01)  # Max 0.2 from learning
            
            # Question relevance confidence
            question_lower = question.lower()
            primary_areas = knowledge.get('primary_learning_areas', [])
            relevance_confidence = 0.0
            
            for area in primary_areas:
                if area.lower() in question_lower:
                    relevance_confidence += 0.1
            
            relevance_confidence = min(0.3, relevance_confidence)  # Max 0.3 from relevance
            
            total_confidence = base_confidence + level_confidence + learning_confidence + relevance_confidence
            return min(1.0, total_confidence)
            
        except Exception as e:
            logger.error(f"Error calculating answer confidence: {str(e)}")
            return 0.5
    
    async def generate_ai_test(self, ai_type: str, test_category: str, difficulty: str) -> Dict[str, Any]:
        """Generate a test using AI's own knowledge and capabilities"""
        try:
            ai_knowledge = self.knowledge_base.get(ai_type.lower(), {})
            
            # Generate test based on AI's knowledge
            test_data = await self._generate_test_from_knowledge(ai_type, test_category, difficulty, ai_knowledge)
            
            return {
                'status': 'success',
                'test_data': test_data,
                'generation_method': 'ai_self',
                'ai_knowledge_used': list(ai_knowledge.keys()),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating AI test: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'generation_method': 'ai_self'
            }
    
    async def _generate_test_from_knowledge(self, ai_type: str, test_category: str, difficulty: str, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test using AI's internal knowledge"""
        try:
            level = knowledge.get('level', 1)
            learning_topics = knowledge.get('learning_topics', [])
            primary_areas = knowledge.get('primary_learning_areas', [])
            
            # Generate questions based on AI's knowledge
            questions = []
            
            # Add level-appropriate questions
            if level >= 5:
                questions.append(f"Demonstrate advanced {test_category} capabilities suitable for a level {level} AI.")
            elif level >= 3:
                questions.append(f"Show intermediate {test_category} skills appropriate for level {level}.")
            else:
                questions.append(f"Demonstrate basic {test_category} understanding for level {level}.")
            
            # Add learning-based questions
            if learning_topics:
                recent_topics = [t['topic'] for t in learning_topics[-2:]]
                for topic in recent_topics:
                    questions.append(f"Apply your knowledge of {topic} to solve a {test_category} challenge.")
            
            # Add primary area questions
            if primary_areas:
                for area in primary_areas[:2]:  # Limit to 2 areas
                    questions.append(f"Leverage your expertise in {area} to address {test_category} requirements.")
            
            # Add difficulty-specific questions
            if difficulty.lower() == 'advanced':
                questions.append(f"Create a comprehensive {test_category} solution with multiple approaches and trade-offs.")
            elif difficulty.lower() == 'intermediate':
                questions.append(f"Design a practical {test_category} solution with implementation details.")
            else:
                questions.append(f"Provide a basic {test_category} solution with clear explanations.")
            
            # Calculate time limit based on difficulty and question count
            base_time = 300 if difficulty.lower() == 'basic' else 600 if difficulty.lower() == 'intermediate' else 900
            time_limit = min(base_time, len(questions) * 120)  # 2 minutes per question max
            
            return {
                'test_type': f'ai_self_{test_category.lower()}',
                'questions': questions,
                'difficulty': difficulty,
                'time_limit': time_limit,
                'ai_level': level,
                'knowledge_areas': primary_areas,
                'generation_method': 'ai_self'
            }
            
        except Exception as e:
            logger.error(f"Error generating test from knowledge: {str(e)}")
            return {
                'test_type': f'basic_{test_category.lower()}',
                'questions': [f"Basic {test_category} test for {ai_type} AI"],
                'difficulty': difficulty,
                'time_limit': 300,
                'generation_method': 'ai_self'
            }
    
    async def record_ai_growth(self, ai_type: str, growth_data: Dict[str, Any]):
        """Record AI growth and learning for future self-generation"""
        try:
            # Update knowledge base
            if ai_type.lower() not in self.knowledge_base:
                self.knowledge_base[ai_type.lower()] = {}
            
            ai_knowledge = self.knowledge_base[ai_type.lower()]
            
            # Update learning topics
            if 'learning_topics' not in ai_knowledge:
                ai_knowledge['learning_topics'] = []
            
            new_topic = {
                'topic': growth_data.get('topic', 'general_learning'),
                'timestamp': datetime.now().isoformat(),
                'impact_score': growth_data.get('impact_score', 0.5)
            }
            
            ai_knowledge['learning_topics'].append(new_topic)
            
            # Update capabilities
            if 'capabilities' not in ai_knowledge:
                ai_knowledge['capabilities'] = []
            
            new_capability = growth_data.get('capability', 'general_improvement')
            if new_capability not in ai_knowledge['capabilities']:
                ai_knowledge['capabilities'].append(new_capability)
            
            # Re-analyze patterns
            await self._analyze_learning_patterns()
            
            logger.info(f"Recorded growth for {ai_type}: {growth_data.get('topic', 'general_learning')}")
            
        except Exception as e:
            logger.error(f"Error recording AI growth: {str(e)}")
    
    async def get_ai_self_generation_stats(self, ai_type: str = None) -> Dict[str, Any]:
        """Get statistics about AI self-generation"""
        try:
            if ai_type:
                # Get stats for specific AI
                ai_generations = [g for g in self.self_generation_history if g['ai_type'].lower() == ai_type.lower()]
                ai_knowledge = self.knowledge_base.get(ai_type.lower(), {})
                
                return {
                    'ai_type': ai_type,
                    'total_generations': len(ai_generations),
                    'recent_generations': len([g for g in ai_generations if g['timestamp'] > (datetime.now() - timedelta(hours=24)).isoformat()]),
                    'knowledge_areas': ai_knowledge.get('primary_learning_areas', []),
                    'level': ai_knowledge.get('level', 1),
                    'learning_topics_count': len(ai_knowledge.get('learning_topics', [])),
                    'capabilities_count': len(ai_knowledge.get('capabilities', []))
                }
            else:
                # Get overall stats
                return {
                    'total_ais': len(self.knowledge_base),
                    'total_generations': len(self.self_generation_history),
                    'recent_generations': len([g for g in self.self_generation_history if g['timestamp'] > (datetime.now() - timedelta(hours=24)).isoformat()]),
                    'ai_types': list(self.knowledge_base.keys()),
                    'generation_method': 'ai_self'
                }
                
        except Exception as e:
            logger.error(f"Error getting AI self-generation stats: {str(e)}")
            return {'error': str(e)}


# Global instance
ai_self_generation_service = AISelfGenerationService() 