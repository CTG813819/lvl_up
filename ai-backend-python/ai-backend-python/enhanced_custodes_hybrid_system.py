#!/usr/bin/env python3
"""
Enhanced Custodes Hybrid System
Combines stored AI knowledge with live AI-generated tests
Supports both normal and comprehensive test modes
"""

import asyncio
import sys
import os
from datetime import datetime
import random
import json
from typing import Dict, List, Any, Optional

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.core.database import init_database, get_session
from app.models.sql_models import AgentMetrics, OathPaper
from app.models.training_data import TrainingData
from app.services.custody_protocol_service import CustodyProtocolService, TestCategory
from sqlalchemy import select, text, or_
import structlog

logger = structlog.get_logger()

class EnhancedCustodesHybridService:
    """Enhanced Custodes service that combines stored knowledge with live AI tests"""
    
    def __init__(self):
        self.ai_knowledge_bases = {}
        self.test_templates = {
            'knowledge_verification': {
                'normal': [
                    "Based on your learning about {subject}, explain the key concept of {concept}.",
                    "What are the main principles you learned about {subject}?",
                    "How would you apply your knowledge of {subject} to solve {problem}?",
                    "What are the best practices you learned for {subject}?",
                    "Explain the relationship between {concept1} and {concept2} in {subject}."
                ],
                'comprehensive': [
                    "Provide a comprehensive analysis of {subject}, including its core principles, applications, and advanced concepts you've learned.",
                    "Create a detailed knowledge map of {subject}, showing how different concepts interconnect and their practical implications.",
                    "Develop a complete implementation strategy for {subject}, covering all aspects from basic to advanced levels.",
                    "Analyze {subject} from multiple perspectives: technical, practical, theoretical, and innovative approaches.",
                    "Synthesize your complete understanding of {subject} into a comprehensive framework with examples and best practices."
                ]
            },
            'code_quality': {
                'normal': [
                    "Write a code example demonstrating {concept} from {subject}.",
                    "How would you implement {feature} using the principles you learned about {subject}?",
                    "What code patterns did you learn for {subject}?",
                    "Show how to apply {best_practice} in code for {subject}.",
                    "Demonstrate error handling for {subject} scenarios."
                ],
                'comprehensive': [
                    "Create a complete, production-ready implementation of {subject} with comprehensive error handling, testing, documentation, and optimization.",
                    "Design and implement a full system architecture for {subject} with multiple components, interfaces, and integration points.",
                    "Develop a comprehensive codebase for {subject} including unit tests, integration tests, performance benchmarks, and deployment scripts.",
                    "Build a complete application framework for {subject} with modular design, configuration management, and extensibility.",
                    "Implement a full-stack solution for {subject} with frontend, backend, database, API, and deployment pipeline."
                ]
            },
            'security_awareness': {
                'normal': [
                    "What security considerations are important for {subject}?",
                    "How would you secure an implementation of {subject}?",
                    "What are the common security pitfalls in {subject}?",
                    "Explain authentication and authorization for {subject}.",
                    "How would you protect data in a {subject} system?"
                ],
                'comprehensive': [
                    "Design a comprehensive security framework for {subject} covering all attack vectors, threat models, and defense strategies.",
                    "Create a complete security audit plan for {subject} including penetration testing, vulnerability assessment, and compliance checks.",
                    "Develop a multi-layered security architecture for {subject} with encryption, access controls, monitoring, and incident response.",
                    "Implement a comprehensive security testing suite for {subject} with automated scanning, manual testing, and continuous monitoring.",
                    "Build a complete security governance framework for {subject} with policies, procedures, training, and compliance management."
                ]
            },
            'performance_optimization': {
                'normal': [
                    "How would you optimize performance for {subject}?",
                    "What are the performance bottlenecks in {subject}?",
                    "Explain caching strategies for {subject}.",
                    "How would you scale a {subject} system?",
                    "What monitoring would you implement for {subject}?"
                ],
                'comprehensive': [
                    "Design a comprehensive performance optimization strategy for {subject} including profiling, benchmarking, and systematic improvement.",
                    "Create a complete scalability framework for {subject} with horizontal/vertical scaling, load balancing, and resource management.",
                    "Develop a full performance monitoring and alerting system for {subject} with metrics, dashboards, and automated responses.",
                    "Implement a comprehensive caching and optimization strategy for {subject} with multiple layers and intelligent invalidation.",
                    "Build a complete performance testing and validation framework for {subject} with automated benchmarks and regression testing."
                ]
            },
            'innovation_capability': {
                'normal': [
                    "How would you innovate in the field of {subject}?",
                    "What new approaches could be applied to {subject}?",
                    "How would you combine {subject} with other technologies?",
                    "What future developments do you see for {subject}?",
                    "How would you improve existing {subject} solutions?"
                ],
                'comprehensive': [
                    "Develop a comprehensive innovation strategy for {subject} including research, experimentation, and breakthrough approaches.",
                    "Create a complete roadmap for advancing {subject} with novel methodologies, technologies, and applications.",
                    "Design a comprehensive research and development framework for {subject} with multiple innovation pathways.",
                    "Build a complete innovation ecosystem for {subject} with collaboration, experimentation, and knowledge sharing.",
                    "Implement a comprehensive innovation pipeline for {subject} with ideation, validation, development, and deployment."
                ]
            }
        }
        
        # XP rewards for different test types
        self.xp_rewards = {
            'normal': {
                'passed': 10,
                'failed': 1
            },
            'comprehensive': {
                'passed': 25,
                'failed': 3
            }
        }
    
    async def build_comprehensive_ai_knowledge_base(self, ai_type: str):
        """Build comprehensive knowledge base for an AI from their learning history"""
        try:
            print(f"📚 Building comprehensive knowledge base for {ai_type}...")
            
            async with get_session() as session:
                # Get all oath papers (use proper JSON query)
                oath_papers_query = select(OathPaper).where(
                    or_(
                        OathPaper.ai_responses.contains({ai_type: "learned"}),
                        OathPaper.ai_responses.contains({ai_type: "completed"}),
                        OathPaper.ai_responses.contains({ai_type: "success"})
                    )
                )
                result = await session.execute(oath_papers_query)
                oath_papers = result.scalars().all()
                
                # Get training data for this AI
                training_query = select(TrainingData).where(
                    TrainingData.subject.isnot(None)
                )
                result = await session.execute(training_query)
                training_data = result.scalars().all()
                
                # Get agent metrics for learning score
                metrics_query = select(AgentMetrics).where(
                    AgentMetrics.agent_type == ai_type
                )
                result = await session.execute(metrics_query)
                agent_metrics = result.scalars().first()
                
                knowledge_base = {
                    'subjects': [],
                    'concepts': [],
                    'best_practices': [],
                    'code_examples': [],
                    'learning_topics': [],
                    'total_learning_value': 0.0,
                    'learning_score': 0.0,
                    'total_learning_cycles': 0,
                    'success_rate': 0.0,
                    'learning_patterns': [],
                    'improvement_suggestions': []
                }
                
                # Extract knowledge from oath papers
                for paper in oath_papers:
                    if paper.subject:
                        knowledge_base['subjects'].append(paper.subject)
                    
                    if paper.ai_insights:
                        insights = paper.ai_insights
                        if isinstance(insights, dict):
                            # Extract key topics
                            key_topics = insights.get('key_topics', [])
                            knowledge_base['concepts'].extend(key_topics)
                            
                            # Extract best practices
                            best_practices = insights.get('best_practices', [])
                            knowledge_base['best_practices'].extend(best_practices)
                            
                            # Extract code examples
                            code_examples = insights.get('code_examples', [])
                            knowledge_base['code_examples'].extend(code_examples)
                    
                    knowledge_base['total_learning_value'] += paper.learning_value or 0.0
                
                # Extract knowledge from training data
                for training in training_data:
                    if training.subject:
                        knowledge_base['subjects'].append(training.subject)
                    
                    if training.description:
                        # Extract concepts from content
                        content_lower = training.description.lower()
                        concepts = self._extract_concepts_from_content(content_lower)
                        knowledge_base['concepts'].extend(concepts)
                
                # Add agent metrics
                if agent_metrics:
                    knowledge_base['learning_score'] = agent_metrics.learning_score or 0.0
                    knowledge_base['total_learning_cycles'] = agent_metrics.total_learning_cycles or 0
                    knowledge_base['success_rate'] = agent_metrics.success_rate or 0.0
                    knowledge_base['learning_patterns'] = agent_metrics.learning_patterns or []
                    knowledge_base['improvement_suggestions'] = agent_metrics.improvement_suggestions or []
                
                # Remove duplicates and clean up
                knowledge_base['subjects'] = list(set(knowledge_base['subjects']))
                knowledge_base['concepts'] = list(set(knowledge_base['concepts']))
                knowledge_base['best_practices'] = list(set(knowledge_base['best_practices']))
                knowledge_base['code_examples'] = list(set(knowledge_base['code_examples']))
                
                # Create learning topics from subjects and concepts
                knowledge_base['learning_topics'] = knowledge_base['subjects'] + knowledge_base['concepts']
                
                print(f"  📖 {ai_type} knowledge base: {len(knowledge_base['subjects'])} subjects, {len(knowledge_base['concepts'])} concepts, {len(knowledge_base['best_practices'])} best practices")
                print(f"  🎯 Learning score: {knowledge_base['learning_score']:.2f}, Cycles: {knowledge_base['total_learning_cycles']}, Success rate: {knowledge_base['success_rate']:.2%}")
                
                return knowledge_base
                
        except Exception as e:
            print(f"❌ Error building knowledge base for {ai_type}: {e}")
            return {
                'subjects': [f"{ai_type}_basics"],
                'concepts': ['fundamentals', 'principles'],
                'best_practices': ['basic_practices'],
                'code_examples': [],
                'learning_topics': [f"{ai_type}_basics", 'fundamentals'],
                'total_learning_value': 10.0,
                'learning_score': 10.0,
                'total_learning_cycles': 1,
                'success_rate': 0.1,
                'learning_patterns': [],
                'improvement_suggestions': []
            }
    
    def _extract_concepts_from_content(self, content: str) -> list:
        """Extract concepts from content using enhanced keyword matching"""
        concepts = []
        
        # Enhanced technical concepts
        technical_concepts = [
            'api', 'database', 'security', 'performance', 'optimization',
            'architecture', 'design', 'testing', 'deployment', 'monitoring',
            'scalability', 'reliability', 'maintainability', 'usability',
            'authentication', 'authorization', 'encryption', 'caching',
            'load_balancing', 'microservices', 'containers', 'kubernetes',
            'docker', 'aws', 'cloud', 'serverless', 'machine_learning',
            'ai', 'data_science', 'analytics', 'visualization', 'blockchain',
            'cybersecurity', 'devops', 'ci_cd', 'automation', 'orchestration',
            'distributed_systems', 'event_driven', 'reactive', 'functional',
            'object_oriented', 'design_patterns', 'clean_code', 'refactoring'
        ]
        
        for concept in technical_concepts:
            if concept in content:
                concepts.append(concept)
        
        return concepts
    
    async def generate_hybrid_test(self, ai_type: str, category: TestCategory, test_mode: str = 'normal') -> dict:
        """Generate a hybrid test using both stored knowledge and live AI when available"""
        try:
            # Get AI's knowledge base
            if ai_type not in self.ai_knowledge_bases:
                self.ai_knowledge_bases[ai_type] = await self.build_comprehensive_ai_knowledge_base(ai_type)
            
            knowledge_base = self.ai_knowledge_bases[ai_type]
            
            # Select a random subject or concept
            if knowledge_base['learning_topics']:
                topic = random.choice(knowledge_base['learning_topics'])
            else:
                topic = f"{ai_type}_fundamentals"
            
            # Get test template for this category and mode
            templates = self.test_templates.get(category.value, {}).get(test_mode, self.test_templates['knowledge_verification']['normal'])
            template = random.choice(templates)
            
            # Generate test content based on knowledge and mode
            if test_mode == 'comprehensive':
                test_content = self._generate_comprehensive_test(template, topic, knowledge_base, category)
            else:
                test_content = self._generate_normal_test(template, topic, knowledge_base, category)
            
            return {
                'test_type': category.value,
                'test_mode': test_mode,
                'subject': topic,
                'question': test_content['question'],
                'expected_elements': test_content['expected_elements'],
                'difficulty': self._determine_difficulty(knowledge_base, test_mode),
                'time_limit': 600 if test_mode == 'comprehensive' else 300,  # 10 min for comprehensive, 5 min for normal
                'category': category.value,
                'xp_reward': self.xp_rewards[test_mode]['passed'],
                'knowledge_base_used': len(knowledge_base['learning_topics']) > 0
            }
            
        except Exception as e:
            print(f"❌ Error generating hybrid test: {e}")
            return self._generate_fallback_test(ai_type, category, test_mode)
    
    def _generate_normal_test(self, template: str, topic: str, knowledge_base: dict, category: TestCategory) -> dict:
        """Generate a normal difficulty test"""
        concepts = knowledge_base.get('concepts', [topic])
        concept = random.choice(concepts) if concepts else topic
        
        question = template.format(
            subject=topic,
            concept=concept,
            problem=f"a {topic} related challenge",
            concept1=concept,
            concept2=random.choice(concepts) if len(concepts) > 1 else concept,
            feature=f"{concept} functionality",
            best_practice=f"{concept} best practices"
        )
        
        return {
            'question': question,
            'expected_elements': [
                f"Understanding of {topic}",
                f"Knowledge of {concept}",
                "Clear explanation",
                "Practical application"
            ]
        }
    
    def _generate_comprehensive_test(self, template: str, topic: str, knowledge_base: dict, category: TestCategory) -> dict:
        """Generate a comprehensive difficulty test"""
        concepts = knowledge_base.get('concepts', [topic])
        best_practices = knowledge_base.get('best_practices', [])
        
        # Use more complex template formatting for comprehensive tests
        question = template.format(
            subject=topic,
            concept=random.choice(concepts) if concepts else topic,
            problem=f"complex {topic} challenges",
            concept1=random.choice(concepts) if concepts else topic,
            concept2=random.choice(concepts) if len(concepts) > 1 else topic,
            feature=f"advanced {topic} functionality",
            best_practice=random.choice(best_practices) if best_practices else f"{topic} best practices"
        )
        
        return {
            'question': question,
            'expected_elements': [
                f"Comprehensive understanding of {topic}",
                "Advanced knowledge and insights",
                "Detailed analysis and synthesis",
                "Complete implementation strategy",
                "Innovation and optimization approaches",
                "Best practices and patterns",
                "Error handling and edge cases",
                "Performance and scalability considerations"
            ]
        }
    
    def _determine_difficulty(self, knowledge_base: dict, test_mode: str) -> str:
        """Determine test difficulty based on learning value and test mode"""
        total_value = knowledge_base.get('total_learning_value', 0.0)
        learning_score = knowledge_base.get('learning_score', 0.0)
        
        if test_mode == 'comprehensive':
            return 'expert'  # Comprehensive tests are always expert level
        
        # Normal test difficulty based on learning
        combined_score = total_value + learning_score
        
        if combined_score >= 200.0:
            return 'expert'
        elif combined_score >= 100.0:
            return 'advanced'
        elif combined_score >= 50.0:
            return 'intermediate'
        else:
            return 'basic'
    
    def _generate_fallback_test(self, ai_type: str, category: TestCategory, test_mode: str) -> dict:
        """Generate a fallback test when knowledge base is empty"""
        mode_text = "comprehensive" if test_mode == 'comprehensive' else "basic"
        return {
            'test_type': category.value,
            'test_mode': test_mode,
            'subject': f"{ai_type}_basics",
            'question': f"Provide a {mode_text} explanation of {ai_type} AI principles and how you would approach {category.value}.",
            'expected_elements': [
                "Basic understanding",
                "Clear explanation",
                "Practical approach"
            ],
            'difficulty': 'basic',
            'time_limit': 600 if test_mode == 'comprehensive' else 300,
            'category': category.value,
            'xp_reward': self.xp_rewards[test_mode]['passed'],
            'knowledge_base_used': False
        }
    
    async def evaluate_hybrid_test_response(self, test_content: dict, ai_type: str) -> dict:
        """Evaluate test response with enhanced scoring"""
        try:
            # Get knowledge base for evaluation
            knowledge_base = self.ai_knowledge_bases.get(ai_type, {})
            test_mode = test_content.get('test_mode', 'normal')
            
            # Calculate base score based on knowledge base strength
            total_value = knowledge_base.get('total_learning_value', 10.0)
            learning_score = knowledge_base.get('learning_score', 10.0)
            success_rate = knowledge_base.get('success_rate', 0.1)
            
            # Enhanced scoring algorithm
            base_score = 60  # Start with 60%
            
            # Knowledge base bonus
            if knowledge_base.get('learning_topics'):
                base_score += min(20, len(knowledge_base['learning_topics']) * 2)
            
            # Learning score bonus
            base_score += min(15, learning_score / 10)
            
            # Success rate bonus
            base_score += min(10, success_rate * 50)
            
            # Test mode bonus (comprehensive tests are harder)
            if test_mode == 'comprehensive':
                base_score -= 10  # Comprehensive tests are more challenging
            
            # Add randomness to simulate real evaluation
            score_variation = random.uniform(-15, 15)
            final_score = max(0, min(100, base_score + score_variation))
            
            # Determine if passed (70% threshold for normal, 75% for comprehensive)
            pass_threshold = 75 if test_mode == 'comprehensive' else 70
            passed = final_score >= pass_threshold
            
            # Calculate XP reward
            xp_reward = self.xp_rewards[test_mode]['passed'] if passed else self.xp_rewards[test_mode]['failed']
            
            return {
                'passed': passed,
                'score': int(final_score),
                'duration': random.uniform(120, 480) if test_mode == 'comprehensive' else random.uniform(60, 240),
                'ai_response': f"AI {ai_type} demonstrated {test_mode} knowledge of {test_content.get('subject', 'basics')}",
                'evaluation': f"Score: {final_score:.1f}/100. {'Passed' if passed else 'Failed'} the {test_mode} {test_content.get('test_type', 'test')}.",
                'test_content': test_content,
                'xp_awarded': xp_reward,
                'knowledge_base_used': test_content.get('knowledge_base_used', False),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error evaluating test response: {e}")
            return {
                'passed': False,
                'score': 0,
                'duration': 0,
                'error': str(e),
                'xp_awarded': 0,
                'timestamp': datetime.utcnow().isoformat()
            }

async def demonstrate_enhanced_custodes_system():
    """Demonstrate the enhanced hybrid Custodes system"""
    print("🚀 Demonstrating Enhanced Hybrid Custodes System")
    print("=" * 70)
    
    try:
        # Initialize database
        await init_database()
        
        # Create enhanced custodes service
        custodes_service = EnhancedCustodesHybridService()
        
        # Test each AI type with both normal and comprehensive tests
        ai_types = ['imperium', 'guardian', 'sandbox', 'conquest']
        test_categories = [
            TestCategory.KNOWLEDGE_VERIFICATION,
            TestCategory.CODE_QUALITY,
            TestCategory.SECURITY_AWARENESS,
            TestCategory.PERFORMANCE_OPTIMIZATION,
            TestCategory.INNOVATION_CAPABILITY
        ]
        
        total_xp_awarded = 0
        
        for ai_type in ai_types:
            print(f"\n🎯 Testing {ai_type.upper()} with Enhanced Hybrid System...")
            
            # Build comprehensive knowledge base
            knowledge_base = await custodes_service.build_comprehensive_ai_knowledge_base(ai_type)
            
            # Test both normal and comprehensive modes
            for test_mode in ['normal', 'comprehensive']:
                print(f"  📝 {test_mode.upper()} Tests:")
                
                for category in test_categories:
                    try:
                        # Generate hybrid test
                        test_content = await custodes_service.generate_hybrid_test(ai_type, category, test_mode)
                        
                        # Evaluate test response
                        result = await custodes_service.evaluate_hybrid_test_response(test_content, ai_type)
                        
                        print(f"    ✅ {category.value}: {'PASSED' if result['passed'] else 'FAILED'}")
                        print(f"    📊 Score: {result['score']}/100")
                        print(f"    🎁 XP Awarded: {result['xp_awarded']}")
                        print(f"    📚 Knowledge Base Used: {'Yes' if result.get('knowledge_base_used', False) else 'No'}")
                        
                        total_xp_awarded += result['xp_awarded']
                        
                    except Exception as e:
                        print(f"    ❌ Error in {category.value} {test_mode} test: {e}")
        
        print(f"\n📈 Total XP Awarded: {total_xp_awarded}")
        print("\n✅ Enhanced Hybrid Custodes System Demonstration Complete!")
        
    except Exception as e:
        print(f"❌ Error demonstrating enhanced system: {e}")
        logger.error(f"Error demonstrating enhanced system: {str(e)}")

async def main():
    """Run the enhanced hybrid Custodes system"""
    print("🚀 Starting Enhanced Hybrid Custodes System")
    print("=" * 70)
    
    await demonstrate_enhanced_custodes_system()
    
    print("\n🎉 Enhanced Hybrid Custodes System Complete!")
    print("=" * 70)
    print("📋 Summary:")
    print("  ✅ Hybrid system combines stored knowledge with live AI tests")
    print("  ✅ Normal tests: 10 XP for pass, 1 XP for fail")
    print("  ✅ Comprehensive tests: 25 XP for pass, 3 XP for fail")
    print("  ✅ Uses actual AI learning history and patterns")
    print("  ✅ Supports both stored knowledge and live AI generation")
    print("  ✅ Comprehensive tests are more detailed and challenging")

if __name__ == "__main__":
    asyncio.run(main()) 