"""
Enhanced Learning Service
Provides continuous learning cycles that improve AI performance over time
"""

import asyncio
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import structlog
from dataclasses import dataclass, field

from app.core.database import get_session
from app.models.sql_models import AgentMetrics, Proposal, OathPaper
from app.services.dynamic_test_generator import dynamic_test_generator, TestScenario
from app.services.agent_metrics_service import AgentMetricsService
from app.services.ai_learning_service import AILearningService

logger = structlog.get_logger()

@dataclass
class LearningCycle:
    """Represents a learning cycle with comprehensive tracking"""
    cycle_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    participating_ais: List[str] = field(default_factory=list)
    total_learning_value: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    insights_generated: List[str] = field(default_factory=list)
    test_scenarios: List[TestScenario] = field(default_factory=list)
    performance_improvements: Dict[str, float] = field(default_factory=dict)
    status: str = "active"

class EnhancedLearningService:
    """Enhanced learning service with continuous improvement"""
    
    def __init__(self):
        self.learning_cycles = []
        self.active_cycles = {}
        self.ai_metrics_service = AgentMetricsService()
        self.ai_learning_service = AILearningService()
        self.learning_interval = timedelta(minutes=30)  # Learning cycles every 30 minutes
        self.test_interval = timedelta(minutes=15)      # Tests every 15 minutes
        self.improvement_threshold = 0.1  # 10% improvement required
        self.max_consecutive_failures = 3
        
        # Learning subjects for each AI type
        self.learning_subjects = {
            "imperium": [
                "meta-learning", "ai-governance", "autonomous-systems",
                "multi-agent-coordination", "ai-ethics", "self-improvement"
            ],
            "guardian": [
                "security-testing", "vulnerability-detection", "secure-coding",
                "threat-modeling", "penetration-testing", "security-automation"
            ],
            "sandbox": [
                "experimental-design", "innovation-frameworks", "creative-problem-solving",
                "novel-algorithms", "research-methodology", "breakthrough-thinking"
            ],
            "conquest": [
                "app-development", "user-experience", "performance-optimization",
                "mobile-architecture", "ai-powered-apps", "market-analysis"
            ]
        }
        
        logger.info("Enhanced Learning Service initialized")
    
    async def start_enhanced_learning(self):
        """Start the enhanced learning system"""
        try:
            logger.info("🚀 Starting Enhanced Learning Service")
            logger.info(f"📚 Learning subjects: {sum(len(subjects) for subjects in self.learning_subjects.values())}")
            logger.info(f"⏰ Learning cycles: Every {self.learning_interval.total_seconds() / 60} minutes")
            logger.info(f"🧪 Test cycles: Every {self.test_interval.total_seconds() / 60} minutes")
            
            # Start background tasks
            await asyncio.gather(
                self._run_learning_cycles(),
                self._run_test_cycles(),
                self._run_performance_analysis(),
                self._run_improvement_tracking()
            )
            
        except Exception as e:
            logger.error(f"❌ Enhanced learning service failed: {str(e)}")
            raise
    
    async def _run_learning_cycles(self):
        """Run periodic learning cycles"""
        while True:
            try:
                logger.info("🔄 Starting enhanced learning cycle...")
                
                # Create new learning cycle
                cycle = await self._create_learning_cycle()
                
                # Execute learning for each AI type
                learning_tasks = []
                for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
                    task = asyncio.create_task(self._execute_ai_learning(ai_type, cycle))
                    learning_tasks.append(task)
                
                # Wait for all learning tasks to complete
                results = await asyncio.gather(*learning_tasks, return_exceptions=True)
                
                # Process learning results
                await self._process_learning_results(cycle, results)
                
                # Update cycle status
                cycle.end_time = datetime.utcnow()
                cycle.status = "completed"
                
                logger.info(f"✅ Learning cycle {cycle.cycle_id} completed")
                logger.info(f"📊 Results: {cycle.success_count} successes, {cycle.failure_count} failures")
                
                # Wait for next cycle
                await asyncio.sleep(self.learning_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"❌ Learning cycle failed: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _run_test_cycles(self):
        """Run periodic test cycles"""
        while True:
            try:
                logger.info("🧪 Starting test cycle...")
                
                # Generate and execute tests for each AI
                test_tasks = []
                for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
                    task = asyncio.create_task(self._execute_ai_testing(ai_type))
                    test_tasks.append(task)
                
                # Wait for all test tasks to complete
                results = await asyncio.gather(*test_tasks, return_exceptions=True)
                
                # Process test results
                await self._process_test_results(results)
                
                logger.info("✅ Test cycle completed")
                
                # Wait for next test cycle
                await asyncio.sleep(self.test_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"❌ Test cycle failed: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _run_performance_analysis(self):
        """Run continuous performance analysis"""
        while True:
            try:
                logger.info("📊 Analyzing AI performance...")
                
                # Analyze performance trends for each AI
                for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
                    trend = dynamic_test_generator.get_performance_trend(ai_type)
                    logger.info(f"📈 {ai_type.capitalize()} performance trend: {trend['trend']}")
                    
                    # Trigger improvements if needed
                    if trend['trend'] == 'declining' and trend['total_tests'] >= 5:
                        await self._trigger_improvement_cycle(ai_type)
                
                # Wait for next analysis
                await asyncio.sleep(600)  # Every 10 minutes
                
            except Exception as e:
                logger.error(f"❌ Performance analysis failed: {str(e)}")
                await asyncio.sleep(300)
    
    async def _run_improvement_tracking(self):
        """Run improvement tracking and optimization"""
        while True:
            try:
                logger.info("🎯 Tracking improvements...")
                
                # Check for improvement opportunities
                for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
                    await self._check_improvement_opportunities(ai_type)
                
                # Wait for next tracking cycle
                await asyncio.sleep(900)  # Every 15 minutes
                
            except Exception as e:
                logger.error(f"❌ Improvement tracking failed: {str(e)}")
                await asyncio.sleep(300)
    
    async def _create_learning_cycle(self) -> LearningCycle:
        """Create a new learning cycle"""
        cycle_id = f"cycle_{int(datetime.utcnow().timestamp())}"
        cycle = LearningCycle(
            cycle_id=cycle_id,
            start_time=datetime.utcnow(),
            participating_ais=["imperium", "guardian", "sandbox", "conquest"]
        )
        
        self.learning_cycles.append(cycle)
        self.active_cycles[cycle_id] = cycle
        
        logger.info(f"🔄 Created learning cycle {cycle_id}")
        return cycle
    
    async def _execute_ai_learning(self, ai_type: str, cycle: LearningCycle) -> Dict[str, Any]:
        """Execute learning for a specific AI type"""
        try:
            logger.info(f"🧠 Executing learning for {ai_type}")
            
            # Get AI's current level and performance
            metrics = await self.ai_metrics_service.get_agent_metrics(ai_type)
            current_level = metrics.get('level', 1)
            previous_performance = metrics.get('average_score', 0.0)
            
            # Select learning subjects
            subjects = self.learning_subjects.get(ai_type, [])
            selected_subjects = random.sample(subjects, min(3, len(subjects)))
            
            learning_results = []
            total_learning_value = 0.0
            
            for subject in selected_subjects:
                # Generate learning content
                learning_content = await self._generate_learning_content(ai_type, subject, current_level)
                
                # Execute learning
                learning_result = await self._execute_learning_task(ai_type, subject, learning_content)
                
                if learning_result['success']:
                    learning_results.append(learning_result)
                    total_learning_value += learning_result['learning_value']
                    cycle.success_count += 1
                else:
                    cycle.failure_count += 1
                
                # Small delay between subjects
                await asyncio.sleep(5)
            
            # Update AI metrics
            await self._update_ai_learning_metrics(ai_type, learning_results, total_learning_value)
            
            # Generate insights
            insights = await self._generate_learning_insights(ai_type, learning_results)
            cycle.insights_generated.extend(insights)
            
            result = {
                'ai_type': ai_type,
                'success': len(learning_results) > 0,
                'learning_value': total_learning_value,
                'subjects_learned': len(learning_results),
                'insights_generated': len(insights),
                'current_level': current_level,
                'previous_performance': previous_performance
            }
            
            logger.info(f"✅ {ai_type} learning completed: {len(learning_results)} subjects, {total_learning_value:.2f} learning value")
            return result
            
        except Exception as e:
            logger.error(f"❌ Learning failed for {ai_type}: {str(e)}")
            cycle.failure_count += 1
            return {
                'ai_type': ai_type,
                'success': False,
                'error': str(e)
            }
    
    async def _execute_ai_testing(self, ai_type: str) -> Dict[str, Any]:
        """Execute testing for a specific AI type"""
        try:
            logger.info(f"🧪 Executing testing for {ai_type}")
            
            # Get AI's current level and performance
            metrics = await self.ai_metrics_service.get_agent_metrics(ai_type)
            current_level = metrics.get('level', 1)
            previous_performance = metrics.get('average_score', 0.0)
            
            # Generate dynamic test
            test_scenario = await dynamic_test_generator.generate_dynamic_test(
                ai_type, current_level, previous_performance
            )
            
            # Execute test
            test_result = await self._execute_test_scenario(ai_type, test_scenario)
            
            # Update performance history
            await dynamic_test_generator.update_performance_history(
                ai_type, test_scenario.scenario_id, test_result['score'], test_result
            )
            
            # Update AI metrics
            await self._update_ai_test_metrics(ai_type, test_result)
            
            logger.info(f"✅ {ai_type} testing completed: Score {test_result['score']:.1f}")
            return test_result
            
        except Exception as e:
            logger.error(f"❌ Testing failed for {ai_type}: {str(e)}")
            return {
                'ai_type': ai_type,
                'success': False,
                'score': 0,
                'error': str(e)
            }
    
    async def _generate_learning_content(self, ai_type: str, subject: str, level: int) -> Dict[str, Any]:
        """Generate learning content for an AI type and subject"""
        
        # Enhanced content templates with realistic scenarios
        content_templates = {
            "imperium": {
                "meta-learning": {
                    "scenario": "Design a self-improving AI system that can learn from its own mistakes",
                    "challenge": "Create an autonomous learning framework that adapts to new problem domains",
                    "content": "Study advanced meta-learning techniques and AI self-improvement mechanisms",
                    "outcome": "Enhanced meta-learning capabilities and autonomous improvement"
                },
                "ai-governance": {
                    "scenario": "Develop governance protocols for multi-AI systems",
                    "challenge": "Create ethical decision-making frameworks for AI coordination",
                    "content": "Learn about AI governance frameworks and ethical decision-making",
                    "outcome": "Improved AI governance and ethical decision-making"
                },
                "autonomous-systems": {
                    "scenario": "Design autonomous systems that can operate independently",
                    "challenge": "Create multi-agent coordination protocols for complex tasks",
                    "content": "Explore autonomous system design and multi-agent coordination",
                    "outcome": "Enhanced autonomous system capabilities"
                }
            },
            "guardian": {
                "security-testing": {
                    "scenario": "Conduct comprehensive security audit of a web application",
                    "challenge": "Identify and exploit vulnerabilities while suggesting fixes",
                    "content": "Master advanced security testing methodologies and vulnerability assessment",
                    "outcome": "Enhanced security testing and vulnerability detection"
                },
                "vulnerability-detection": {
                    "scenario": "Analyze code for security vulnerabilities and suggest improvements",
                    "challenge": "Detect SQL injection, XSS, and other common vulnerabilities",
                    "content": "Learn cutting-edge vulnerability detection techniques",
                    "outcome": "Improved vulnerability detection and security analysis"
                },
                "secure-coding": {
                    "scenario": "Review and improve code security in a production application",
                    "challenge": "Implement secure coding practices and security architecture",
                    "content": "Study secure coding practices and security architecture design",
                    "outcome": "Better secure coding practices and security awareness"
                }
            },
            "sandbox": {
                "experimental-design": {
                    "scenario": "Design innovative algorithms for complex problem solving",
                    "challenge": "Create novel approaches to optimization problems",
                    "content": "Design and conduct innovative experiments in AI research",
                    "outcome": "Enhanced experimental design and innovation capabilities"
                },
                "innovation-frameworks": {
                    "scenario": "Develop new frameworks for creative problem solving",
                    "challenge": "Create innovative solutions to technical challenges",
                    "content": "Apply creative problem-solving frameworks and breakthrough thinking",
                    "outcome": "Improved innovation and creative thinking"
                },
                "creative-problem-solving": {
                    "scenario": "Solve complex AI challenges with novel approaches",
                    "challenge": "Develop creative solutions to technical problems",
                    "content": "Develop novel approaches to complex AI challenges",
                    "outcome": "Enhanced creative problem-solving abilities"
                }
            },
            "conquest": {
                "app-development": {
                    "scenario": "Build a full-stack application with modern technologies",
                    "challenge": "Create a scalable, user-friendly application with optimal performance",
                    "content": "Master advanced app development techniques and user experience design",
                    "outcome": "Enhanced app development and user experience skills"
                },
                "user-experience": {
                    "scenario": "Design intuitive user interfaces for complex applications",
                    "challenge": "Create user-centered design principles and interface optimization",
                    "content": "Learn user-centered design principles and interface optimization",
                    "outcome": "Better user experience design and interface optimization"
                },
                "performance-optimization": {
                    "scenario": "Optimize application performance and user experience",
                    "challenge": "Improve loading times, responsiveness, and overall efficiency",
                    "content": "Study app performance optimization and scalability design",
                    "outcome": "Better performance optimization and user experience"
                }
            }
        }
        
        templates = content_templates.get(ai_type, {})
        template = templates.get(subject, {
            "scenario": f"Learn about {subject} for {ai_type} AI",
            "challenge": f"Apply {subject} concepts in practice",
            "content": f"Study {subject} fundamentals and advanced techniques",
            "outcome": f"Enhanced {subject} capabilities"
        })
        
        return {
            "subject": subject,
            "scenario": template["scenario"],
            "challenge": template["challenge"],
            "content": template["content"],
            "outcome": template["outcome"],
            "level": level,
            "complexity": self._get_complexity_for_level(level),
            "learning_objectives": [
                f"Master {subject} concepts",
                f"Apply {subject} in practical scenarios",
                f"Improve {ai_type} capabilities",
                f"Create innovative {subject} solutions"
            ],
            "resources": [
                f"Advanced {subject} documentation",
                f"{subject} best practices guide",
                f"Real-world {subject} examples"
            ],
            "exercises": [
                f"Implement {subject} solution",
                f"Analyze {subject} case study",
                f"Optimize {subject} performance"
            ],
            "expected_outcomes": [
                f"Improved {subject} understanding",
                f"Enhanced {subject} capabilities",
                f"Better {subject} decision-making"
            ]
        }
    
    async def _execute_learning_task(self, ai_type: str, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a learning task for an AI"""
        try:
            # Simulate learning process
            learning_time = random.uniform(10, 30)  # 10-30 seconds
            await asyncio.sleep(learning_time)
            
            # Calculate learning success based on complexity and AI type
            success_rate = self._calculate_learning_success_rate(ai_type, content['level'])
            success = random.random() < success_rate
            
            if success:
                learning_value = random.uniform(0.5, 1.5) * content['level']
                return {
                    'success': True,
                    'subject': subject,
                    'learning_value': learning_value,
                    'time_spent': learning_time,
                    'insights_generated': [
                        f"Learned {subject} concepts",
                        f"Improved {ai_type} capabilities",
                        f"Applied knowledge in practice"
                    ]
                }
            else:
                return {
                    'success': False,
                    'subject': subject,
                    'learning_value': 0.0,
                    'time_spent': learning_time,
                    'error': f"Failed to learn {subject}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'subject': subject,
                'learning_value': 0.0,
                'error': str(e)
            }
    
    async def _execute_test_scenario(self, ai_type: str, scenario: TestScenario) -> Dict[str, Any]:
        """Execute a test scenario for an AI"""
        try:
            # Simulate test execution
            test_time = random.uniform(20, 60)  # 20-60 seconds
            await asyncio.sleep(test_time)
            
            # Calculate test score based on AI type, level, and difficulty
            base_score = self._calculate_base_test_score(ai_type, scenario.difficulty.value)
            performance_variance = random.uniform(-0.2, 0.2)  # ±20% variance
            final_score = max(0.0, min(1.0, base_score + performance_variance))
            
            passed = final_score >= scenario.success_criteria.get('completion_rate', 0.7)
            
            return {
                'ai_type': ai_type,
                'scenario_id': scenario.scenario_id,
                'score': final_score,
                'passed': passed,
                'time_spent': test_time,
                'difficulty': scenario.difficulty.value,
                'category': scenario.category.value,
                'feedback': f"Test completed with {final_score:.1%} score"
            }
            
        except Exception as e:
            return {
                'ai_type': ai_type,
                'scenario_id': scenario.scenario_id,
                'score': 0.0,
                'passed': False,
                'error': str(e)
            }
    
    def _get_complexity_for_level(self, level: int) -> str:
        """Get complexity based on AI level"""
        if level <= 3:
            return "basic"
        elif level <= 7:
            return "intermediate"
        elif level <= 12:
            return "advanced"
        elif level <= 18:
            return "expert"
        else:
            return "master"
    
    def _calculate_learning_success_rate(self, ai_type: str, level: int) -> float:
        """Calculate learning success rate based on AI type and level"""
        base_rates = {
            "imperium": 0.8,
            "guardian": 0.75,
            "sandbox": 0.7,
            "conquest": 0.8
        }
        
        base_rate = base_rates.get(ai_type, 0.7)
        level_bonus = min(level * 0.02, 0.2)  # Up to 20% bonus from level
        
        return min(base_rate + level_bonus, 0.95)  # Cap at 95%
    
    def _calculate_base_test_score(self, ai_type: str, difficulty: str) -> float:
        """Calculate base test score based on AI type and difficulty"""
        base_scores = {
            "imperium": 0.75,
            "guardian": 0.7,
            "sandbox": 0.65,
            "conquest": 0.8
        }
        
        base_score = base_scores.get(ai_type, 0.7)
        
        difficulty_multipliers = {
            "basic": 1.0,
            "intermediate": 0.9,
            "advanced": 0.8,
            "expert": 0.7,
            "master": 0.6,
            "legendary": 0.5
        }
        
        multiplier = difficulty_multipliers.get(difficulty, 1.0)
        return base_score * multiplier
    
    async def _update_ai_learning_metrics(self, ai_type: str, learning_results: List[Dict], 
                                        total_learning_value: float):
        """Update AI learning metrics"""
        try:
            # Update metrics in database
            await self.ai_metrics_service.update_learning_metrics(
                ai_type, {
                    "learning_value": total_learning_value,
                    "subjects_learned": len(learning_results),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Update learning service
            await self.ai_learning_service.record_learning_event(
                ai_type, "enhanced_learning", {
                    "learning_value": total_learning_value,
                    "subjects_learned": len(learning_results),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating learning metrics for {ai_type}: {str(e)}")
    
    async def _update_ai_test_metrics(self, ai_type: str, test_result: Dict[str, Any]):
        """Update AI test metrics"""
        try:
            # Update metrics in database
            await self.ai_metrics_service.update_test_metrics(
                ai_type, test_result['score'], test_result['passed']
            )
            
            # Update learning service
            await self.ai_learning_service.record_test_result(
                ai_type, "dynamic_test", test_result['score'], test_result['feedback']
            )
            
        except Exception as e:
            logger.error(f"Error updating test metrics for {ai_type}: {str(e)}")
    
    async def _generate_learning_insights(self, ai_type: str, learning_results: List[Dict]) -> List[str]:
        """Generate insights from learning results"""
        insights = []
        
        if learning_results:
            subjects_learned = [r['subject'] for r in learning_results if r['success']]
            total_value = sum(r['learning_value'] for r in learning_results if r['success'])
            
            insights.append(f"{ai_type.capitalize()} successfully learned {len(subjects_learned)} subjects")
            insights.append(f"Total learning value: {total_value:.2f}")
            
            if subjects_learned:
                insights.append(f"Subjects mastered: {', '.join(subjects_learned)}")
        
        return insights
    
    async def _process_learning_results(self, cycle: LearningCycle, results: List[Any]):
        """Process learning cycle results"""
        try:
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Learning task failed with exception: {str(result)}")
                    cycle.failure_count += 1
                elif isinstance(result, dict):
                    if result.get('success', False):
                        cycle.success_count += 1
                        cycle.total_learning_value += result.get('learning_value', 0.0)
                    else:
                        cycle.failure_count += 1
            
            # Calculate overall cycle success rate
            total_tasks = len(results)
            success_rate = cycle.success_count / total_tasks if total_tasks > 0 else 0.0
            
            logger.info(f"📊 Learning cycle {cycle.cycle_id} results:")
            logger.info(f"   Success rate: {success_rate:.1%}")
            logger.info(f"   Total learning value: {cycle.total_learning_value:.2f}")
            logger.info(f"   Insights generated: {len(cycle.insights_generated)}")
            
        except Exception as e:
            logger.error(f"Error processing learning results: {str(e)}")
    
    async def _process_test_results(self, results: List[Any]):
        """Process test cycle results"""
        try:
            total_tests = len(results)
            passed_tests = 0
            total_score = 0.0
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Test failed with exception: {str(result)}")
                elif isinstance(result, dict) and result.get('success', False):
                    if result.get('passed', False):
                        passed_tests += 1
                    total_score += result.get('score', 0.0)
            
            pass_rate = passed_tests / total_tests if total_tests > 0 else 0.0
            average_score = total_score / total_tests if total_tests > 0 else 0.0
            
            logger.info(f"📊 Test cycle results:")
            logger.info(f"   Pass rate: {pass_rate:.1%}")
            logger.info(f"   Average score: {average_score:.1%}")
            
        except Exception as e:
            logger.error(f"Error processing test results: {str(e)}")
    
    async def _trigger_improvement_cycle(self, ai_type: str):
        """Trigger an improvement cycle for an AI that's declining"""
        try:
            logger.info(f"🎯 Triggering improvement cycle for {ai_type}")
            
            # Generate focused learning content
            improvement_content = await self._generate_improvement_content(ai_type)
            
            # Execute improvement learning
            improvement_result = await self._execute_improvement_learning(ai_type, improvement_content)
            
            if improvement_result['success']:
                logger.info(f"✅ Improvement cycle completed for {ai_type}")
            else:
                logger.warning(f"⚠️ Improvement cycle failed for {ai_type}")
                
        except Exception as e:
            logger.error(f"Error in improvement cycle for {ai_type}: {str(e)}")
    
    async def _generate_improvement_content(self, ai_type: str) -> Dict[str, Any]:
        """Generate focused improvement content"""
        improvement_focus = {
            "imperium": "meta-learning optimization and self-improvement techniques",
            "guardian": "advanced security testing and vulnerability assessment",
            "sandbox": "innovative problem-solving and experimental design",
            "conquest": "app development optimization and user experience enhancement"
        }
        
        focus = improvement_focus.get(ai_type, "general improvement techniques")
        
        return {
            "focus": focus,
            "intensity": "high",
            "duration": 300,  # 5 minutes
            "objectives": [
                f"Improve {ai_type} performance",
                "Address declining trends",
                "Enhance core capabilities"
            ]
        }
    
    async def _execute_improvement_learning(self, ai_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Execute focused improvement learning"""
        try:
            # Simulate intensive improvement learning
            await asyncio.sleep(content['duration'])
            
            # Higher success rate for improvement cycles
            success_rate = 0.9
            success = random.random() < success_rate
            
            if success:
                return {
                    'success': True,
                    'improvement_value': random.uniform(0.3, 0.8),
                    'focus': content['focus'],
                    'duration': content['duration']
                }
            else:
                return {
                    'success': False,
                    'focus': content['focus'],
                    'error': "Improvement learning failed"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _check_improvement_opportunities(self, ai_type: str):
        """Check for improvement opportunities"""
        try:
            # Get current performance trend
            trend = dynamic_test_generator.get_performance_trend(ai_type)
            
            # Check if improvement is needed
            if trend['trend'] == 'stable' and trend['average_score'] < 0.7:
                logger.info(f"📈 {ai_type} has improvement opportunity")
                await self._trigger_improvement_cycle(ai_type)
                
        except Exception as e:
            logger.error(f"Error checking improvement opportunities for {ai_type}: {str(e)}")
    
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        try:
            stats = {
                "total_cycles": len(self.learning_cycles),
                "active_cycles": len(self.active_cycles),
                "total_successes": sum(cycle.success_count for cycle in self.learning_cycles),
                "total_failures": sum(cycle.failure_count for cycle in self.learning_cycles),
                "total_learning_value": sum(cycle.total_learning_value for cycle in self.learning_cycles),
                "ai_performance_trends": {}
            }
            
            # Get performance trends for each AI
            for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
                trend = dynamic_test_generator.get_performance_trend(ai_type)
                stats["ai_performance_trends"][ai_type] = trend
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting learning statistics: {str(e)}")
            return {"error": str(e)}

# Global instance
enhanced_learning_service = EnhancedLearningService() 