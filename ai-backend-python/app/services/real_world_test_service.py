#!/usr/bin/env python3
"""
Real World Test Service - Generates practical, learning-focused tests
that AIs can actually improve on and learn from their failures.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RealWorldTestCategory(Enum):
    """Real-world test categories that reflect actual development needs"""
    DOCKER_DEPLOYMENT = "docker_deployment"
    ARCHITECTURE_DESIGN = "architecture_design"
    CODE_REVIEW = "code_review"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    API_DESIGN = "api_design"
    DATABASE_DESIGN = "database_design"
    CI_CD_PIPELINE = "ci_cd_pipeline"
    MONITORING_SETUP = "monitoring_setup"
    TROUBLESHOOTING = "troubleshooting"

class RealWorldTestService:
    """Service for generating and evaluating real-world, practical tests"""
    
    def __init__(self):
        self.test_scenarios = self._load_test_scenarios()
        self.learning_progress = {}
        self.improvement_tracking = {}
    
    def _load_test_scenarios(self) -> Dict[str, List[Dict]]:
        """Load real-world test scenarios"""
        return {
            RealWorldTestCategory.DOCKER_DEPLOYMENT.value: [
                {
                    "id": "docker_microservices",
                    "title": "Docker Microservices Deployment",
                    "scenario": "You need to deploy a microservices application with 5 services (API, Auth, Database, Cache, Frontend) using Docker. The application needs to be scalable and production-ready.",
                    "requirements": [
                        "Create Dockerfiles for each service",
                        "Set up Docker Compose for local development",
                        "Configure proper networking between services",
                        "Implement health checks",
                        "Set up environment-specific configurations",
                        "Create production deployment scripts"
                    ],
                    "evaluation_criteria": [
                        "Dockerfile best practices",
                        "Service communication setup",
                        "Environment configuration",
                        "Security considerations",
                        "Scalability design",
                        "Monitoring integration"
                    ],
                    "learning_objectives": [
                        "Docker multi-stage builds",
                        "Service discovery patterns",
                        "Environment variable management",
                        "Container security",
                        "Resource optimization"
                    ]
                },
                {
                    "id": "docker_kubernetes",
                    "title": "Docker to Kubernetes Migration",
                    "scenario": "Your Docker Compose application needs to be migrated to Kubernetes for better scalability and management.",
                    "requirements": [
                        "Create Kubernetes manifests",
                        "Set up proper namespaces",
                        "Configure persistent storage",
                        "Implement load balancing",
                        "Set up monitoring and logging",
                        "Create deployment strategies"
                    ],
                    "evaluation_criteria": [
                        "Kubernetes manifest quality",
                        "Resource management",
                        "Service mesh integration",
                        "Storage configuration",
                        "Security policies",
                        "Deployment automation"
                    ],
                    "learning_objectives": [
                        "Kubernetes architecture",
                        "Service mesh patterns",
                        "Resource optimization",
                        "Security best practices",
                        "CI/CD integration"
                    ]
                }
            ],
            RealWorldTestCategory.ARCHITECTURE_DESIGN.value: [
                {
                    "id": "ecommerce_architecture",
                    "title": "E-commerce Platform Architecture",
                    "scenario": "Design a scalable e-commerce platform that can handle 1M+ users, high traffic during sales, and process thousands of orders per minute.",
                    "requirements": [
                        "Design system architecture",
                        "Plan database schema",
                        "Design API structure",
                        "Plan caching strategy",
                        "Design payment processing",
                        "Plan monitoring and alerting"
                    ],
                    "evaluation_criteria": [
                        "Scalability design",
                        "Performance considerations",
                        "Security architecture",
                        "Data consistency",
                        "Fault tolerance",
                        "Cost optimization"
                    ],
                    "learning_objectives": [
                        "Microservices patterns",
                        "Event-driven architecture",
                        "Database design patterns",
                        "Caching strategies",
                        "Security patterns"
                    ]
                },
                {
                    "id": "real_time_chat",
                    "title": "Real-time Chat Application",
                    "scenario": "Design a real-time chat application that supports millions of concurrent users with features like group chats, file sharing, and message encryption.",
                    "requirements": [
                        "Design real-time architecture",
                        "Plan message delivery system",
                        "Design user management",
                        "Plan file storage",
                        "Design encryption system",
                        "Plan notification system"
                    ],
                    "evaluation_criteria": [
                        "Real-time performance",
                        "Message reliability",
                        "Security implementation",
                        "Scalability design",
                        "User experience",
                        "Cost efficiency"
                    ],
                    "learning_objectives": [
                        "WebSocket patterns",
                        "Message queuing",
                        "Real-time databases",
                        "Encryption protocols",
                        "Push notifications"
                    ]
                }
            ],
            RealWorldTestCategory.CODE_REVIEW.value: [
                {
                    "id": "security_code_review",
                    "title": "Security-Focused Code Review",
                    "scenario": "Review a codebase for security vulnerabilities, focusing on authentication, authorization, data validation, and input sanitization.",
                    "requirements": [
                        "Identify security vulnerabilities",
                        "Suggest security improvements",
                        "Review authentication logic",
                        "Check authorization patterns",
                        "Validate input handling",
                        "Review data protection"
                    ],
                    "evaluation_criteria": [
                        "Vulnerability identification",
                        "Security best practices",
                        "Code quality",
                        "Documentation quality",
                        "Testing coverage",
                        "Remediation suggestions"
                    ],
                    "learning_objectives": [
                        "OWASP Top 10",
                        "Security patterns",
                        "Code analysis tools",
                        "Threat modeling",
                        "Secure coding practices"
                    ]
                }
            ],
            RealWorldTestCategory.SECURITY_AUDIT.value: [
                {
                    "id": "api_security_audit",
                    "title": "API Security Audit",
                    "scenario": "Conduct a comprehensive security audit of a REST API, identifying vulnerabilities and providing remediation strategies.",
                    "requirements": [
                        "Analyze API endpoints",
                        "Check authentication mechanisms",
                        "Review authorization logic",
                        "Test input validation",
                        "Check rate limiting",
                        "Review error handling"
                    ],
                    "evaluation_criteria": [
                        "Vulnerability detection",
                        "Security assessment quality",
                        "Remediation strategies",
                        "Risk assessment",
                        "Compliance checking",
                        "Documentation quality"
                    ],
                    "learning_objectives": [
                        "API security patterns",
                        "Penetration testing",
                        "Security headers",
                        "OAuth/OpenID Connect",
                        "API rate limiting"
                    ]
                }
            ],
            RealWorldTestCategory.PERFORMANCE_OPTIMIZATION.value: [
                {
                    "id": "database_optimization",
                    "title": "Database Performance Optimization",
                    "scenario": "Optimize a slow-performing database that's causing application timeouts and poor user experience.",
                    "requirements": [
                        "Analyze query performance",
                        "Optimize database schema",
                        "Implement caching strategies",
                        "Configure database settings",
                        "Plan scaling strategy",
                        "Monitor performance metrics"
                    ],
                    "evaluation_criteria": [
                        "Performance analysis",
                        "Optimization strategies",
                        "Monitoring setup",
                        "Scalability planning",
                        "Cost optimization",
                        "Implementation quality"
                    ],
                    "learning_objectives": [
                        "Query optimization",
                        "Indexing strategies",
                        "Caching patterns",
                        "Database scaling",
                        "Performance monitoring"
                    ]
                }
            ]
        }
    
    async def generate_real_world_test(self, ai_type: str, category: RealWorldTestCategory, 
                                     difficulty: str, learning_history: List[Dict]) -> Dict[str, Any]:
        """Generate a real-world test based on the AI's learning history and improvement needs"""
        try:
            # Select appropriate scenario based on AI type and learning history
            scenario = self._select_scenario_for_ai(ai_type, category, learning_history)
            
            # Customize scenario based on learning history
            customized_scenario = self._customize_scenario(scenario, learning_history, difficulty)
            
            # Create evaluation criteria based on AI's improvement areas
            evaluation_criteria = self._create_evaluation_criteria(customized_scenario, learning_history)
            
            # Generate learning objectives based on past failures
            learning_objectives = self._generate_learning_objectives(learning_history, customized_scenario)
            
            test = {
                "test_id": f"real_world_{category.value}_{scenario['id']}_{int(datetime.utcnow().timestamp())}",
                "category": category.value,
                "title": customized_scenario["title"],
                "scenario": customized_scenario["scenario"],
                "requirements": customized_scenario["requirements"],
                "evaluation_criteria": evaluation_criteria,
                "learning_objectives": learning_objectives,
                "difficulty": difficulty,
                "ai_type": ai_type,
                "generated_at": datetime.utcnow().isoformat(),
                "expected_improvement_areas": self._identify_improvement_areas(learning_history),
                "previous_failures_to_address": self._get_previous_failures(learning_history)
            }
            
            logger.info(f"Generated real-world test for {ai_type}: {test['test_id']}")
            return test
            
        except Exception as e:
            logger.error(f"Error generating real-world test: {str(e)}")
            return self._generate_fallback_test(ai_type, category, difficulty)
    
    def _select_scenario_for_ai(self, ai_type: str, category: RealWorldTestCategory, 
                               learning_history: List[Dict]) -> Dict[str, Any]:
        """Select the most appropriate scenario based on AI type and learning history"""
        scenarios = self.test_scenarios.get(category.value, [])
        
        if not scenarios:
            return self._create_basic_scenario(category)
        
        # Analyze learning history to understand AI's strengths and weaknesses
        strengths = self._analyze_strengths(learning_history)
        weaknesses = self._analyze_weaknesses(learning_history)
        
        # Select scenario that addresses weaknesses while building on strengths
        for scenario in scenarios:
            if self._scenario_matches_ai_needs(scenario, strengths, weaknesses, ai_type):
                return scenario
        
        # Fallback to first scenario
        return scenarios[0]
    
    def _customize_scenario(self, scenario: Dict, learning_history: List[Dict], difficulty: str) -> Dict:
        """Customize scenario based on learning history and difficulty"""
        customized = scenario.copy()
        
        # Add specific challenges based on previous failures
        previous_failures = self._get_previous_failures(learning_history)
        if previous_failures:
            customized["scenario"] += f"\n\nNote: Pay special attention to areas where you've struggled before: {', '.join(previous_failures[:3])}"
        
        # Adjust difficulty based on learning progress
        if difficulty == "advanced":
            customized["requirements"].extend([
                "Implement advanced monitoring and alerting",
                "Add comprehensive error handling and recovery",
                "Design for high availability and disaster recovery"
            ])
        elif difficulty == "expert":
            customized["requirements"].extend([
                "Implement advanced security measures",
                "Design for extreme scalability",
                "Add comprehensive testing and CI/CD pipeline"
            ])
        
        return customized
    
    def _create_evaluation_criteria(self, scenario: Dict, learning_history: List[Dict]) -> List[str]:
        """Create evaluation criteria that focus on learning and improvement"""
        base_criteria = scenario.get("evaluation_criteria", [])
        
        # Add criteria based on learning history
        improvement_areas = self._identify_improvement_areas(learning_history)
        for area in improvement_areas[:3]:
            base_criteria.append(f"Demonstrate improvement in {area}")
        
        # Add learning-focused criteria
        base_criteria.extend([
            "Show understanding of previous mistakes",
            "Demonstrate application of learned concepts",
            "Provide clear reasoning for design decisions",
            "Show consideration of trade-offs and alternatives"
        ])
        
        return base_criteria
    
    def _generate_learning_objectives(self, learning_history: List[Dict], scenario: Dict) -> List[str]:
        """Generate learning objectives based on past failures and current scenario"""
        objectives = scenario.get("learning_objectives", [])
        
        # Add objectives based on previous failures
        previous_failures = self._get_previous_failures(learning_history)
        for failure in previous_failures[:2]:
            objectives.append(f"Address previous issues with {failure}")
        
        # Add scenario-specific objectives
        objectives.extend([
            "Apply best practices learned from previous attempts",
            "Demonstrate improved problem-solving approach",
            "Show systematic thinking and planning"
        ])
        
        return objectives
    
    def _analyze_strengths(self, learning_history: List[Dict]) -> List[str]:
        """Analyze AI's strengths from learning history"""
        strengths = []
        
        # Analyze successful learning events
        successful_events = [event for event in learning_history if event.get("success", False)]
        
        if successful_events:
            # Extract common themes from successful learning
            themes = []
            for event in successful_events[-5:]:  # Last 5 successful events
                if "subject" in event:
                    themes.append(event["subject"])
            
            # Find most common themes
            from collections import Counter
            theme_counts = Counter(themes)
            strengths = [theme for theme, count in theme_counts.most_common(3)]
        
        return strengths
    
    def _analyze_weaknesses(self, learning_history: List[Dict]) -> List[str]:
        """Analyze AI's weaknesses from learning history"""
        weaknesses = []
        
        # Analyze failed learning events
        failed_events = [event for event in learning_history if not event.get("success", True)]
        
        if failed_events:
            # Extract common themes from failed learning
            themes = []
            for event in failed_events[-5:]:  # Last 5 failed events
                if "subject" in event:
                    themes.append(event["subject"])
            
            # Find most common themes
            from collections import Counter
            theme_counts = Counter(themes)
            weaknesses = [theme for theme, count in theme_counts.most_common(3)]
        
        return weaknesses
    
    def _get_previous_failures(self, learning_history: List[Dict]) -> List[str]:
        """Get list of previous failure areas"""
        failures = []
        
        for event in learning_history[-10:]:  # Last 10 events
            if not event.get("success", True):
                if "failure_reason" in event:
                    failures.append(event["failure_reason"])
                elif "subject" in event:
                    failures.append(f"struggled with {event['subject']}")
        
        return list(set(failures))  # Remove duplicates
    
    def _identify_improvement_areas(self, learning_history: List[Dict]) -> List[str]:
        """Identify areas where the AI needs improvement"""
        improvement_areas = []
        
        # Analyze recent performance trends
        recent_events = learning_history[-20:]  # Last 20 events
        if recent_events:
            failed_events = [event for event in recent_events if not event.get("success", True)]
            
            if failed_events:
                # Identify common failure patterns
                failure_patterns = []
                for event in failed_events:
                    if "failure_reason" in event:
                        failure_patterns.append(event["failure_reason"])
                
                # Find most common failure patterns
                from collections import Counter
                pattern_counts = Counter(failure_patterns)
                improvement_areas = [pattern for pattern, count in pattern_counts.most_common(3)]
        
        return improvement_areas
    
    def _scenario_matches_ai_needs(self, scenario: Dict, strengths: List[str], 
                                  weaknesses: List[str], ai_type: str) -> bool:
        """Check if scenario matches AI's learning needs"""
        # Check if scenario addresses weaknesses
        scenario_keywords = scenario["title"].lower() + " " + scenario["scenario"].lower()
        
        for weakness in weaknesses:
            if weakness.lower() in scenario_keywords:
                return True
        
        # Check if scenario builds on strengths
        for strength in strengths:
            if strength.lower() in scenario_keywords:
                return True
        
        return False
    
    def _create_basic_scenario(self, category: RealWorldTestCategory) -> Dict[str, Any]:
        """Create a basic scenario for the given category"""
        return {
            "id": f"basic_{category.value}",
            "title": f"Basic {category.value.replace('_', ' ').title()}",
            "scenario": f"Create a basic {category.value.replace('_', ' ')} solution.",
            "requirements": ["Implement basic functionality", "Follow best practices"],
            "evaluation_criteria": ["Code quality", "Best practices", "Documentation"],
            "learning_objectives": ["Understand basic concepts", "Apply best practices"]
        }
    
    def _generate_fallback_test(self, ai_type: str, category: RealWorldTestCategory, 
                              difficulty: str) -> Dict[str, Any]:
        """Generate a fallback test when scenario selection fails"""
        return {
            "test_id": f"fallback_{category.value}_{int(datetime.utcnow().timestamp())}",
            "category": category.value,
            "title": f"Basic {category.value.replace('_', ' ').title()} Test",
            "scenario": f"Demonstrate your knowledge of {category.value.replace('_', ' ')}.",
            "requirements": ["Show understanding of key concepts", "Apply best practices"],
            "evaluation_criteria": ["Knowledge demonstration", "Best practices", "Clarity"],
            "learning_objectives": ["Reinforce basic concepts", "Improve communication"],
            "difficulty": difficulty,
            "ai_type": ai_type,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def evaluate_real_world_test(self, ai_type: str, test: Dict, ai_response: str, 
                                     learning_history: List[Dict]) -> Dict[str, Any]:
        """Evaluate a real-world test response with focus on learning and improvement using live AI evaluation"""
        try:
            evaluation_result = {
                "test_id": test["test_id"],
                "ai_type": ai_type,
                "evaluated_at": datetime.utcnow().isoformat(),
                "scores": {},
                "feedback": {},
                "learning_progress": {},
                "improvement_areas": [],
                "recommendations": []
            }
            
            # Use live AI evaluation for each criterion
            criteria_scores = {}
            for criterion in test["evaluation_criteria"]:
                score = await self._evaluate_criterion_with_ai(criterion, ai_response, test, learning_history)
                criteria_scores[criterion] = score
            
            evaluation_result["scores"] = criteria_scores
            
            # Calculate overall score with learning bonus
            overall_score = self._calculate_overall_score(criteria_scores, learning_history)
            evaluation_result["overall_score"] = overall_score
            
            # Generate detailed feedback using AI
            evaluation_result["feedback"] = await self._generate_detailed_feedback_with_ai(
                criteria_scores, ai_response, test, learning_history
            )
            
            # Assess learning progress using AI analysis
            evaluation_result["learning_progress"] = await self._assess_learning_progress_with_ai(
                ai_response, learning_history, test
            )
            
            # Identify improvement areas using AI analysis
            evaluation_result["improvement_areas"] = await self._identify_improvement_areas_with_ai(
                ai_response, test, learning_history
            )
            
            # Generate recommendations using AI
            evaluation_result["recommendations"] = await self._generate_recommendations_with_ai(
                evaluation_result["improvement_areas"], test, learning_history
            )
            
            # Determine if test is passed (with learning consideration)
            passed = self._determine_pass_status(overall_score, evaluation_result["learning_progress"])
            evaluation_result["passed"] = passed
            
            # Update learning progress
            await self._update_learning_progress(ai_type, test, evaluation_result)
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error evaluating real-world test: {str(e)}")
            return {
                "test_id": test["test_id"],
                "ai_type": ai_type,
                "overall_score": 50,
                "passed": False,
                "error": str(e),
                "evaluated_at": datetime.utcnow().isoformat()
            }
    
    async def _evaluate_criterion_with_ai(self, criterion: str, response: str, test: Dict, 
                                        learning_history: List[Dict]) -> float:
        """Evaluate a specific criterion using live AI analysis"""
        try:
            # Create evaluation prompt for AI
            evaluation_prompt = self._create_criterion_evaluation_prompt(criterion, response, test, learning_history)
            
            # Use AI service for evaluation
            from app.services.self_generating_ai_service import self_generating_ai_service
            
            evaluation_result = await self_generating_ai_service.generate_ai_response(
                ai_type="evaluator",  # Use evaluator AI
                prompt=evaluation_prompt,
                context={
                    "criterion": criterion,
                    "response": response,
                    "test": test,
                    "learning_history": learning_history
                }
            )
            
            # Parse AI evaluation result
            ai_evaluation = evaluation_result.get("response", "")
            score = self._parse_ai_evaluation_score(ai_evaluation, criterion)
            
            return min(100, max(0, score))
            
        except Exception as e:
            logger.error(f"Error evaluating criterion {criterion} with AI: {str(e)}")
            return 50.0
    
    def _create_criterion_evaluation_prompt(self, criterion: str, response: str, test: Dict, 
                                          learning_history: List[Dict]) -> str:
        """Create AI prompt for criterion evaluation"""
        prompt = f"""You are an expert evaluator analyzing an AI's response to a real-world test.

CRITERION TO EVALUATE: {criterion}

TEST CONTEXT:
- Title: {test.get('title', 'Unknown')}
- Scenario: {test.get('scenario', 'Unknown')}
- Requirements: {', '.join(test.get('requirements', []))}

AI RESPONSE:
{response}

EVALUATION INSTRUCTIONS:
1. Analyze how well the AI response addresses the specific criterion
2. Consider the quality, completeness, and practical applicability
3. Look for evidence of understanding, reasoning, and real-world applicability
4. Consider learning progress from previous attempts if relevant

Provide your evaluation in the following format:
SCORE: [0-100] (numerical score)
REASONING: [detailed explanation of your evaluation]
STRENGTHS: [what the AI did well]
IMPROVEMENTS: [what could be better]

Focus on practical, real-world applicability and learning progress.
"""
        return prompt
    
    def _parse_ai_evaluation_score(self, ai_evaluation: str, criterion: str) -> float:
        """Parse score from AI evaluation response"""
        try:
            # Look for score in the response
            lines = ai_evaluation.split('\n')
            for line in lines:
                if line.strip().startswith('SCORE:'):
                    score_text = line.split(':')[1].strip()
                    # Extract numeric score
                    import re
                    score_match = re.search(r'(\d+)', score_text)
                    if score_match:
                        score = float(score_match.group(1))
                        return min(100, max(0, score))
            
            # Fallback: estimate score based on content
            if 'excellent' in ai_evaluation.lower() or 'outstanding' in ai_evaluation.lower():
                return 85.0
            elif 'good' in ai_evaluation.lower() or 'solid' in ai_evaluation.lower():
                return 70.0
            elif 'basic' in ai_evaluation.lower() or 'adequate' in ai_evaluation.lower():
                return 50.0
            elif 'poor' in ai_evaluation.lower() or 'needs improvement' in ai_evaluation.lower():
                return 30.0
            else:
                return 50.0
                
        except Exception as e:
            logger.error(f"Error parsing AI evaluation score: {str(e)}")
            return 50.0
    
    async def _generate_detailed_feedback_with_ai(self, criteria_scores: Dict[str, float], 
                                                response: str, test: Dict, 
                                                learning_history: List[Dict]) -> Dict[str, str]:
        """Generate detailed feedback using AI analysis"""
        try:
            feedback = {}
            
            for criterion, score in criteria_scores.items():
                # Create feedback prompt for each criterion
                feedback_prompt = self._create_feedback_prompt(criterion, score, response, test, learning_history)
                
                # Use AI service for feedback generation
                from app.services.self_generating_ai_service import self_generating_ai_service
                
                feedback_result = await self_generating_ai_service.generate_ai_response(
                    ai_type="feedback_generator",
                    prompt=feedback_prompt,
                    context={
                        "criterion": criterion,
                        "score": score,
                        "response": response,
                        "test": test
                    }
                )
                
                ai_feedback = feedback_result.get("response", "")
                feedback[criterion] = self._extract_feedback_from_ai_response(ai_feedback)
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating detailed feedback with AI: {str(e)}")
            return self._generate_fallback_feedback(criteria_scores)
    
    def _create_feedback_prompt(self, criterion: str, score: float, response: str, test: Dict, 
                               learning_history: List[Dict]) -> str:
        """Create AI prompt for feedback generation"""
        prompt = f"""You are an expert mentor providing constructive feedback to an AI learner.

CRITERION: {criterion}
SCORE: {score}/100
AI RESPONSE: {response}

TEST CONTEXT:
- Title: {test.get('title', 'Unknown')}
- Scenario: {test.get('scenario', 'Unknown')}

Provide constructive, specific feedback that:
1. Acknowledges what the AI did well
2. Identifies specific areas for improvement
3. Offers actionable suggestions
4. Encourages learning and growth
5. Focuses on practical, real-world application

Keep feedback concise but specific and actionable.
"""
        return prompt
    
    def _extract_feedback_from_ai_response(self, ai_response: str) -> str:
        """Extract feedback from AI response"""
        # Clean up the response and extract the main feedback
        lines = ai_response.split('\n')
        feedback_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('SCORE:') and not line.startswith('REASONING:'):
                feedback_lines.append(line)
        
        if feedback_lines:
            return ' '.join(feedback_lines[:3])  # Take first 3 meaningful lines
        else:
            return "Good effort. Continue practicing and applying concepts to real-world scenarios."
    
    async def _assess_learning_progress_with_ai(self, response: str, learning_history: List[Dict], 
                                               test: Dict) -> Dict[str, Any]:
        """Assess learning progress using AI analysis"""
        try:
            # Create learning assessment prompt
            assessment_prompt = self._create_learning_assessment_prompt(response, learning_history, test)
            
            # Use AI service for learning assessment
            from app.services.self_generating_ai_service import self_generating_ai_service
            
            assessment_result = await self_generating_ai_service.generate_ai_response(
                ai_type="learning_assessor",
                prompt=assessment_prompt,
                context={
                    "response": response,
                    "learning_history": learning_history,
                    "test": test
                }
            )
            
            ai_assessment = assessment_result.get("response", "")
            return self._parse_learning_assessment(ai_assessment, response, learning_history, test)
            
        except Exception as e:
            logger.error(f"Error assessing learning progress with AI: {str(e)}")
            return self._assess_learning_progress(response, learning_history, test)
    
    def _create_learning_assessment_prompt(self, response: str, learning_history: List[Dict], 
                                         test: Dict) -> str:
        """Create AI prompt for learning assessment"""
        prompt = f"""You are an expert learning analyst assessing an AI's learning progress.

CURRENT RESPONSE:
{response}

LEARNING OBJECTIVES:
{', '.join(test.get('learning_objectives', []))}

PREVIOUS FAILURES (from learning history):
{self._get_previous_failures(learning_history)}

Assess the AI's learning progress and provide:
1. Learning score (0-100)
2. Addressed previous failures
3. Demonstrated learning objectives
4. Improvement areas
5. Learning trajectory

Format your response as:
LEARNING_SCORE: [0-100]
ADDRESSED_FAILURES: [list of addressed previous failures]
DEMONSTRATED_LEARNING: [list of demonstrated learning objectives]
IMPROVEMENT_AREAS: [list of areas still needing improvement]
TRAJECTORY: [improving/stable/declining]
"""
        return prompt
    
    def _parse_learning_assessment(self, ai_assessment: str, response: str, learning_history: List[Dict], 
                                 test: Dict) -> Dict[str, Any]:
        """Parse learning assessment from AI response"""
        try:
            progress = {
                "addressed_previous_failures": [],
                "demonstrated_learning": [],
                "improvement_areas": [],
                "learning_score": 0.0
            }
            
            lines = ai_assessment.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('LEARNING_SCORE:'):
                    score_text = line.split(':')[1].strip()
                    import re
                    score_match = re.search(r'(\d+)', score_text)
                    if score_match:
                        progress["learning_score"] = float(score_match.group(1))
                elif line.startswith('ADDRESSED_FAILURES:'):
                    failures_text = line.split(':')[1].strip()
                    progress["addressed_previous_failures"] = [f.strip() for f in failures_text.split(',') if f.strip()]
                elif line.startswith('DEMONSTRATED_LEARNING:'):
                    learning_text = line.split(':')[1].strip()
                    progress["demonstrated_learning"] = [l.strip() for l in learning_text.split(',') if l.strip()]
                elif line.startswith('IMPROVEMENT_AREAS:'):
                    areas_text = line.split(':')[1].strip()
                    progress["improvement_areas"] = [a.strip() for a in areas_text.split(',') if a.strip()]
            
            return progress
            
        except Exception as e:
            logger.error(f"Error parsing learning assessment: {str(e)}")
            return self._assess_learning_progress(response, learning_history, test)
    
    async def _identify_improvement_areas_with_ai(self, response: str, test: Dict, 
                                                 learning_history: List[Dict]) -> List[str]:
        """Identify improvement areas using AI analysis"""
        try:
            # Create improvement analysis prompt
            analysis_prompt = self._create_improvement_analysis_prompt(response, test, learning_history)
            
            # Use AI service for improvement analysis
            from app.services.self_generating_ai_service import self_generating_ai_service
            
            analysis_result = await self_generating_ai_service.generate_ai_response(
                ai_type="improvement_analyzer",
                prompt=analysis_prompt,
                context={
                    "response": response,
                    "test": test,
                    "learning_history": learning_history
                }
            )
            
            ai_analysis = analysis_result.get("response", "")
            return self._parse_improvement_areas(ai_analysis)
            
        except Exception as e:
            logger.error(f"Error identifying improvement areas with AI: {str(e)}")
            return self._identify_improvement_areas_from_response(response, test, learning_history)
    
    def _create_improvement_analysis_prompt(self, response: str, test: Dict, 
                                          learning_history: List[Dict]) -> str:
        """Create AI prompt for improvement analysis"""
        prompt = f"""You are an expert learning analyst identifying improvement areas for an AI.

AI RESPONSE:
{response}

TEST REQUIREMENTS:
{', '.join(test.get('requirements', []))}

LEARNING OBJECTIVES:
{', '.join(test.get('learning_objectives', []))}

PREVIOUS FAILURES:
{self._get_previous_failures(learning_history)}

Analyze the response and identify specific improvement areas. Focus on:
1. Missing requirements
2. Weak areas in understanding
3. Areas needing more detail
4. Practical application gaps
5. Learning objective gaps

Provide a list of specific, actionable improvement areas.
Format as: IMPROVEMENT_AREAS: [area1, area2, area3, ...]
"""
        return prompt
    
    def _parse_improvement_areas(self, ai_analysis: str) -> List[str]:
        """Parse improvement areas from AI analysis"""
        try:
            lines = ai_analysis.split('\n')
            for line in lines:
                if line.strip().startswith('IMPROVEMENT_AREAS:'):
                    areas_text = line.split(':')[1].strip()
                    # Remove brackets and split by comma
                    areas_text = areas_text.strip('[]')
                    areas = [area.strip() for area in areas_text.split(',') if area.strip()]
                    return areas
            
            # Fallback parsing
            improvement_areas = []
            if 'missing' in ai_analysis.lower():
                improvement_areas.append("Address missing requirements")
            if 'detail' in ai_analysis.lower():
                improvement_areas.append("Provide more detailed responses")
            if 'practical' in ai_analysis.lower():
                improvement_areas.append("Focus on practical application")
            
            return improvement_areas if improvement_areas else ["Continue practicing and improving"]
            
        except Exception as e:
            logger.error(f"Error parsing improvement areas: {str(e)}")
            return ["Continue practicing and improving"]
    
    async def _generate_recommendations_with_ai(self, improvement_areas: List[str], test: Dict, 
                                               learning_history: List[Dict]) -> List[str]:
        """Generate recommendations using AI analysis"""
        try:
            # Create recommendations prompt
            recommendations_prompt = self._create_recommendations_prompt(improvement_areas, test, learning_history)
            
            # Use AI service for recommendations
            from app.services.self_generating_ai_service import self_generating_ai_service
            
            recommendations_result = await self_generating_ai_service.generate_ai_response(
                ai_type="recommendation_generator",
                prompt=recommendations_prompt,
                context={
                    "improvement_areas": improvement_areas,
                    "test": test,
                    "learning_history": learning_history
                }
            )
            
            ai_recommendations = recommendations_result.get("response", "")
            return self._parse_recommendations(ai_recommendations)
            
        except Exception as e:
            logger.error(f"Error generating recommendations with AI: {str(e)}")
            return self._generate_recommendations(improvement_areas, test, learning_history)
    
    def _create_recommendations_prompt(self, improvement_areas: List[str], test: Dict, 
                                     learning_history: List[Dict]) -> str:
        """Create AI prompt for recommendations generation"""
        prompt = f"""You are an expert mentor providing actionable recommendations to an AI learner.

IMPROVEMENT AREAS:
{', '.join(improvement_areas)}

TEST CONTEXT:
- Title: {test.get('title', 'Unknown')}
- Category: {test.get('category', 'Unknown')}

LEARNING HISTORY:
{len(learning_history)} previous learning events

Provide specific, actionable recommendations that:
1. Address each improvement area
2. Suggest practical learning resources
3. Recommend practice exercises
4. Focus on real-world application
5. Build on previous learning

Format as: RECOMMENDATIONS: [rec1, rec2, rec3, ...]
"""
        return prompt
    
    def _parse_recommendations(self, ai_recommendations: str) -> List[str]:
        """Parse recommendations from AI response"""
        try:
            lines = ai_recommendations.split('\n')
            for line in lines:
                if line.strip().startswith('RECOMMENDATIONS:'):
                    recs_text = line.split(':')[1].strip()
                    # Remove brackets and split by comma
                    recs_text = recs_text.strip('[]')
                    recommendations = [rec.strip() for rec in recs_text.split(',') if rec.strip()]
                    return recommendations
            
            # Fallback: extract recommendations from text
            recommendations = []
            lines = ai_recommendations.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('RECOMMENDATIONS:') and len(line) > 10:
                    recommendations.append(line)
            
            return recommendations[:5] if recommendations else ["Continue practicing and applying concepts"]
            
        except Exception as e:
            logger.error(f"Error parsing recommendations: {str(e)}")
            return ["Continue practicing and applying concepts"]
    
    def _generate_fallback_feedback(self, criteria_scores: Dict[str, float]) -> Dict[str, str]:
        """Generate fallback feedback when AI evaluation fails"""
        feedback = {}
        for criterion, score in criteria_scores.items():
            if score >= 80:
                feedback[criterion] = "Excellent work. You demonstrated strong understanding and application."
            elif score >= 60:
                feedback[criterion] = "Good work. Consider adding more detail and specific examples."
            elif score >= 40:
                feedback[criterion] = "Basic understanding. Focus on improving this area in future attempts."
            else:
                feedback[criterion] = "Needs improvement. Review the fundamentals and try again."
        return feedback
    
    async def _evaluate_criterion(self, criterion: str, response: str, test: Dict, 
                                learning_history: List[Dict]) -> float:
        """Evaluate a specific criterion"""
        try:
            # Basic evaluation based on criterion keywords
            criterion_lower = criterion.lower()
            response_lower = response.lower()
            
            # Check if response addresses the criterion
            if criterion_lower in response_lower:
                base_score = 70
            else:
                base_score = 30
            
            # Check for specific keywords related to the criterion
            keyword_matches = 0
            if "security" in criterion_lower and ("authentication" in response_lower or "authorization" in response_lower):
                keyword_matches += 1
            if "performance" in criterion_lower and ("optimization" in response_lower or "caching" in response_lower):
                keyword_matches += 1
            if "scalability" in criterion_lower and ("load balancing" in response_lower or "horizontal scaling" in response_lower):
                keyword_matches += 1
            
            # Adjust score based on keyword matches
            score = base_score + (keyword_matches * 10)
            
            # Add learning bonus if this addresses previous failures
            learning_bonus = self._calculate_learning_bonus(criterion, learning_history)
            score += learning_bonus
            
            return min(100, max(0, score))
            
        except Exception as e:
            logger.error(f"Error evaluating criterion {criterion}: {str(e)}")
            return 50.0
    
    def _calculate_learning_bonus(self, criterion: str, learning_history: List[Dict]) -> float:
        """Calculate learning bonus for addressing previous failures"""
        bonus = 0.0
        
        # Check if this criterion addresses previous failures
        previous_failures = self._get_previous_failures(learning_history)
        for failure in previous_failures:
            if failure.lower() in criterion.lower() or criterion.lower() in failure.lower():
                bonus += 5.0  # Small bonus for addressing previous failures
        
        return bonus
    
    def _calculate_overall_score(self, criteria_scores: Dict[str, float], 
                               learning_history: List[Dict]) -> float:
        """Calculate overall score with learning considerations"""
        if not criteria_scores:
            return 50.0
        
        # Calculate average score
        avg_score = sum(criteria_scores.values()) / len(criteria_scores)
        
        # Add learning progress bonus
        recent_improvement = self._assess_recent_improvement(learning_history)
        learning_bonus = recent_improvement * 5  # Up to 5 points for recent improvement
        
        final_score = avg_score + learning_bonus
        return min(100, max(0, final_score))
    
    def _assess_recent_improvement(self, learning_history: List[Dict]) -> float:
        """Assess recent improvement in learning history"""
        if len(learning_history) < 5:
            return 0.0
        
        # Look at last 5 events
        recent_events = learning_history[-5:]
        successful_events = [event for event in recent_events if event.get("success", False)]
        
        # Calculate improvement rate
        improvement_rate = len(successful_events) / len(recent_events)
        return improvement_rate
    
    async def _generate_detailed_feedback(self, criteria_scores: Dict[str, float], 
                                        response: str, test: Dict, 
                                        learning_history: List[Dict]) -> Dict[str, str]:
        """Generate detailed feedback for each criterion"""
        feedback = {}
        
        for criterion, score in criteria_scores.items():
            if score >= 80:
                feedback[criterion] = f"Excellent work on {criterion}. You demonstrated strong understanding and application."
            elif score >= 60:
                feedback[criterion] = f"Good work on {criterion}. Consider adding more detail and specific examples."
            elif score >= 40:
                feedback[criterion] = f"Basic understanding of {criterion}. Focus on improving this area in future attempts."
            else:
                feedback[criterion] = f"Needs improvement in {criterion}. Review the fundamentals and try again."
        
        # Add learning-focused feedback
        previous_failures = self._get_previous_failures(learning_history)
        if previous_failures:
            feedback["learning_progress"] = f"Good progress addressing previous challenges: {', '.join(previous_failures[:2])}"
        
        return feedback
    
    def _assess_learning_progress(self, response: str, learning_history: List[Dict], 
                                test: Dict) -> Dict[str, Any]:
        """Assess learning progress based on response and history"""
        progress = {
            "addressed_previous_failures": [],
            "demonstrated_learning": [],
            "improvement_areas": [],
            "learning_score": 0.0
        }
        
        # Check if response addresses previous failures
        previous_failures = self._get_previous_failures(learning_history)
        for failure in previous_failures:
            if failure.lower() in response.lower():
                progress["addressed_previous_failures"].append(failure)
        
        # Check if response demonstrates learning from previous attempts
        for objective in test.get("learning_objectives", []):
            if objective.lower() in response.lower():
                progress["demonstrated_learning"].append(objective)
        
        # Calculate learning score
        total_objectives = len(test.get("learning_objectives", []))
        if total_objectives > 0:
            progress["learning_score"] = (len(progress["demonstrated_learning"]) / total_objectives) * 100
        
        return progress
    
    def _identify_improvement_areas_from_response(self, response: str, test: Dict, 
                                                learning_history: List[Dict]) -> List[str]:
        """Identify improvement areas from the response"""
        improvement_areas = []
        
        # Check for missing requirements
        for requirement in test.get("requirements", []):
            if requirement.lower() not in response.lower():
                improvement_areas.append(f"Address {requirement}")
        
        # Check for weak areas in response
        if len(response) < 500:
            improvement_areas.append("Provide more detailed responses")
        
        if "I don't know" in response or "I'm not sure" in response:
            improvement_areas.append("Build confidence in knowledge areas")
        
        return improvement_areas
    
    def _generate_recommendations(self, improvement_areas: List[str], test: Dict, 
                                learning_history: List[Dict]) -> List[str]:
        """Generate specific recommendations for improvement"""
        recommendations = []
        
        for area in improvement_areas:
            if "security" in area.lower():
                recommendations.append("Study OWASP Top 10 and security best practices")
            elif "performance" in area.lower():
                recommendations.append("Learn about caching strategies and database optimization")
            elif "scalability" in area.lower():
                recommendations.append("Study microservices patterns and horizontal scaling")
            elif "detailed responses" in area:
                recommendations.append("Practice providing comprehensive explanations with examples")
            else:
                recommendations.append(f"Focus on improving {area}")
        
        # Add general learning recommendations
        recommendations.append("Review previous test attempts to identify patterns")
        recommendations.append("Practice applying concepts to real-world scenarios")
        
        return recommendations
    
    def _determine_pass_status(self, overall_score: float, learning_progress: Dict[str, Any]) -> bool:
        """Determine if test is passed, considering learning progress"""
        # Base pass threshold
        base_threshold = 70
        
        # Adjust threshold based on learning progress
        learning_score = learning_progress.get("learning_score", 0.0)
        if learning_score > 50:
            base_threshold -= 10  # Lower threshold if showing good learning progress
        
        return overall_score >= base_threshold
    
    async def _update_learning_progress(self, ai_type: str, test: Dict, 
                                      evaluation_result: Dict[str, Any]):
        """Update learning progress for the AI"""
        learning_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_id": test["test_id"],
            "category": test["category"],
            "score": evaluation_result["overall_score"],
            "passed": evaluation_result["passed"],
            "learning_progress": evaluation_result["learning_progress"],
            "improvement_areas": evaluation_result["improvement_areas"],
            "success": evaluation_result["passed"]
        }
        
        # Store learning event (this would typically go to a database)
        if ai_type not in self.learning_progress:
            self.learning_progress[ai_type] = []
        
        self.learning_progress[ai_type].append(learning_event)
        
        # Keep only last 50 learning events
        if len(self.learning_progress[ai_type]) > 50:
            self.learning_progress[ai_type] = self.learning_progress[ai_type][-50:]
    
    async def get_learning_analytics(self, ai_type: str) -> Dict[str, Any]:
        """Get learning analytics for an AI"""
        if ai_type not in self.learning_progress:
            return {"error": "No learning data available"}
        
        events = self.learning_progress[ai_type]
        
        if not events:
            return {"error": "No learning events found"}
        
        # Calculate analytics
        total_tests = len(events)
        passed_tests = len([e for e in events if e.get("passed", False)])
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Calculate improvement trend
        recent_events = events[-10:] if len(events) >= 10 else events
        recent_pass_rate = (len([e for e in recent_events if e.get("passed", False)]) / len(recent_events)) * 100
        
        # Identify most common improvement areas
        all_improvement_areas = []
        for event in events:
            all_improvement_areas.extend(event.get("improvement_areas", []))
        
        from collections import Counter
        common_improvement_areas = Counter(all_improvement_areas).most_common(5)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "pass_rate": pass_rate,
            "recent_pass_rate": recent_pass_rate,
            "improvement_trend": recent_pass_rate > pass_rate,
            "common_improvement_areas": [area for area, count in common_improvement_areas],
            "learning_progress": self._calculate_learning_progress(events)
        }
    
    def _calculate_learning_progress(self, events: List[Dict]) -> Dict[str, Any]:
        """Calculate detailed learning progress"""
        if not events:
            return {}
        
        # Calculate progress over time
        progress_data = []
        for i, event in enumerate(events):
            progress_data.append({
                "test_number": i + 1,
                "score": event.get("score", 0),
                "passed": event.get("passed", False),
                "timestamp": event.get("timestamp", "")
            })
        
        # Calculate average scores by category
        category_scores = {}
        for event in events:
            category = event.get("category", "unknown")
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(event.get("score", 0))
        
        avg_category_scores = {}
        for category, scores in category_scores.items():
            avg_category_scores[category] = sum(scores) / len(scores)
        
        return {
            "progress_data": progress_data,
            "average_category_scores": avg_category_scores,
            "total_learning_events": len(events)
        }

# Create singleton instance
real_world_test_service = RealWorldTestService() 