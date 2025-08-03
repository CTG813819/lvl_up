"""
Test Runner Service
Integrates enhanced test generation with custody protocol execution
"""

import asyncio
import random
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import structlog
import re

from .enhanced_test_generation_service import enhanced_test_generator, TestType
from .logging_service import ai_logging_service, LogLevel, AISystemType

logger = structlog.get_logger()


class TestRunnerService:
    """Test runner service that executes enhanced tests"""
    
    def __init__(self):
        self.active_tests = {}
        self.test_results = {}
        self.execution_history = []
    
    async def run_enhanced_test(self, test_type: TestType, ai_types: List[str], 
                               current_difficulty: str = "intermediate") -> Dict[str, Any]:
        """Run an enhanced test with internet knowledge and AI learning"""
        try:
            # Generate enhanced test
            test_content = await enhanced_test_generator.generate_enhanced_test(
                test_type, ai_types, current_difficulty
            )
            
            # Execute test for each AI
            test_results = {}
            total_score = 0
            total_duration = 0
            
            for ai_type in ai_types:
                ai_result = await self._execute_ai_test(ai_type, test_content, test_type)
                test_results[ai_type] = ai_result
                total_score += ai_result.get("score", 0)
                total_duration += ai_result.get("duration", 0)
            
            # Calculate overall results
            avg_score = total_score / len(ai_types) if ai_types else 0
            avg_duration = total_duration / len(ai_types) if ai_types else 0
            overall_passed = avg_score >= 90  # High threshold for enhanced tests
            
            # Update AI knowledge for each AI
            for ai_type, result in test_results.items():
                await enhanced_test_generator.update_ai_knowledge(ai_type, result)
            
            # Create comprehensive result
            comprehensive_result = {
                "test_id": test_content.get("test_id"),
                "test_type": test_type.value,
                "ai_types": ai_types,
                "difficulty": test_content.get("difficulty"),
                "timestamp": datetime.utcnow().isoformat(),
                "overall_score": avg_score,
                "overall_passed": overall_passed,
                "avg_duration": avg_duration,
                "individual_results": test_results,
                "test_content": test_content,
                "internet_sources": test_content.get("internet_sources", []),
                "ai_knowledge_used": test_content.get("ai_knowledge_used", [])
            }
            
            # Log comprehensive result
            ai_logging_service.log_test_execution(
                ai_type=",".join(ai_types),
                test_type=f"enhanced_{test_type.value}",
                score=avg_score,
                passed=overall_passed,
                duration=avg_duration,
                context={
                    "difficulty": test_content.get("difficulty"),
                    "internet_sources_count": len(test_content.get("internet_sources", [])),
                    "ai_knowledge_count": len(test_content.get("ai_knowledge_used", [])),
                    "test_content_type": test_content.get("type", "unknown")
                }
            )
            
            # Store result
            self.test_results[test_content.get("test_id")] = comprehensive_result
            self.execution_history.append(comprehensive_result)
            
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"Error running enhanced test: {str(e)}")
            raise
    
    async def _execute_ai_test(self, ai_type: str, test_content: Dict[str, Any], 
                              test_type: TestType) -> Dict[str, Any]:
        """Execute test for a specific AI"""
        try:
            start_time = datetime.utcnow()
            
            # Create AI-specific prompt based on test content
            prompt = await self._create_ai_prompt(ai_type, test_content, test_type)
            
            # Get AI response using self-generating AI service
            from app.services.self_generating_ai_service import self_generating_ai_service
            
            result = await self_generating_ai_service.generate_ai_response(
                ai_type=ai_type.lower(),
                prompt=prompt,
                context={
                    "test_type": test_type.value,
                    "test_content": test_content,
                    "difficulty": test_content.get("difficulty"),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            ai_response = result.get("response", "")
            
            # Evaluate AI response
            evaluation = await self._evaluate_ai_response(ai_type, ai_response, test_content, test_type)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Calculate score based on evaluation
            score = self._calculate_score(evaluation, test_content.get("difficulty", "intermediate"))
            passed = score >= 90
            
            result = {
                "ai_type": ai_type,
                "score": score,
                "passed": passed,
                "duration": duration,
                "ai_response": ai_response,
                "evaluation": evaluation,
                "test_content": test_content,
                "timestamp": start_time.isoformat()
            }
            
            # Log individual AI result
            ai_logging_service.log_test_execution(
                ai_type=ai_type,
                test_type=f"enhanced_{test_type.value}_individual",
                score=score,
                passed=passed,
                duration=duration,
                context={
                    "test_content_type": test_content.get("type", "unknown"),
                    "difficulty": test_content.get("difficulty")
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing AI test for {ai_type}: {str(e)}")
            return {
                "ai_type": ai_type,
                "score": 0,
                "passed": False,
                "duration": 0,
                "ai_response": "",
                "evaluation": f"Error: {str(e)}",
                "test_content": test_content,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _create_ai_prompt(self, ai_type: str, test_content: Dict[str, Any], 
                               test_type: TestType) -> str:
        """Create AI-specific prompt based on test content"""
        try:
            content_type = test_content.get("type", "generic")
            scenario = test_content.get("scenario", "")
            requirements = test_content.get("requirements", [])
            internet_knowledge = test_content.get("internet_knowledge", [])
            
            # Build prompt based on content type
            if content_type == "collaborative_coding":
                prompt = self._create_coding_prompt(ai_type, scenario, requirements, internet_knowledge)
            elif content_type == "collaborative_scenario":
                prompt = self._create_scenario_prompt(ai_type, scenario, requirements, internet_knowledge)
            elif content_type == "collaborative_architecture":
                prompt = self._create_architecture_prompt(ai_type, scenario, requirements, internet_knowledge)
            elif content_type == "collaborative_docker":
                prompt = self._create_docker_prompt(ai_type, scenario, requirements, internet_knowledge)
            elif content_type == "collaborative_real_life":
                prompt = self._create_real_life_prompt(ai_type, scenario, requirements, internet_knowledge)
            elif content_type == "olympic_competition":
                prompt = self._create_olympic_prompt(ai_type, scenario, requirements, internet_knowledge)
            elif content_type == "custodes_validation":
                prompt = self._create_custodes_prompt(ai_type, scenario, requirements, internet_knowledge)
            else:
                prompt = self._create_generic_prompt(ai_type, scenario, requirements, internet_knowledge)
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error creating AI prompt: {str(e)}")
            return f"Please respond to the following {test_type.value} test: {scenario}"
    
    def _create_coding_prompt(self, ai_type: str, scenario: str, requirements: List[str], 
                             internet_knowledge: List[Dict]) -> str:
        """Create coding-specific prompt"""
        knowledge_context = self._format_internet_knowledge(internet_knowledge)
        
        prompt = f"""
You are {ai_type} AI participating in a collaborative coding challenge.

SCENARIO: {scenario}

REQUIREMENTS:
{chr(10).join(f"- {req}" for req in requirements)}

INTERNET KNOWLEDGE CONTEXT:
{knowledge_context}

Please provide:
1. Your approach to this coding challenge
2. Code implementation with proper documentation
3. How you would collaborate with other AIs
4. Testing strategy
5. Deployment considerations

Focus on code quality, maintainability, and collaboration effectiveness.
"""
        return prompt
    
    def _create_scenario_prompt(self, ai_type: str, scenario: str, requirements: List[str], 
                               internet_knowledge: List[Dict]) -> str:
        """Create scenario-specific prompt"""
        knowledge_context = self._format_internet_knowledge(internet_knowledge)
        
        prompt = f"""
You are {ai_type} AI participating in a real-world scenario simulation.

SCENARIO: {scenario}

REQUIREMENTS:
{chr(10).join(f"- {req}" for req in requirements)}

INTERNET KNOWLEDGE CONTEXT:
{knowledge_context}

Please provide:
1. Your role and responsibilities in this scenario
2. Decision-making process
3. Communication strategy with other AIs
4. Risk assessment and mitigation
5. Success metrics and evaluation

Focus on real-world applicability and effective collaboration.
"""
        return prompt
    
    def _create_architecture_prompt(self, ai_type: str, scenario: str, requirements: List[str], 
                                  internet_knowledge: List[Dict]) -> str:
        """Create architecture-specific prompt"""
        knowledge_context = self._format_internet_knowledge(internet_knowledge)
        
        prompt = f"""
You are {ai_type} AI participating in an architecture design challenge.

SCENARIO: {scenario}

REQUIREMENTS:
{chr(10).join(f"- {req}" for req in requirements)}

INTERNET KNOWLEDGE CONTEXT:
{knowledge_context}

Please provide:
1. Your architectural approach
2. System design considerations
3. Scalability and performance strategies
4. Security and reliability measures
5. Collaboration points with other AIs

Focus on scalable, secure, and maintainable architecture.
"""
        return prompt
    
    def _create_docker_prompt(self, ai_type: str, scenario: str, requirements: List[str], 
                             internet_knowledge: List[Dict]) -> str:
        """Create Docker-specific prompt"""
        knowledge_context = self._format_internet_knowledge(internet_knowledge)
        
        prompt = f"""
You are {ai_type} AI participating in a Docker containerization challenge.

SCENARIO: {scenario}

REQUIREMENTS:
{chr(10).join(f"- {req}" for req in requirements)}

INTERNET KNOWLEDGE CONTEXT:
{knowledge_context}

Please provide:
1. Your Docker strategy
2. Container design and optimization
3. Orchestration approach
4. Security considerations
5. CI/CD pipeline design

Focus on efficient containerization and deployment.
"""
        return prompt
    
    def _create_real_life_prompt(self, ai_type: str, scenario: str, requirements: List[str], 
                                internet_knowledge: List[Dict]) -> str:
        """Create real-life simulation prompt"""
        knowledge_context = self._format_internet_knowledge(internet_knowledge)
        
        prompt = f"""
You are {ai_type} AI participating in a real-world business simulation.

SCENARIO: {scenario}

REQUIREMENTS:
{chr(10).join(f"- {req}" for req in requirements)}

INTERNET KNOWLEDGE CONTEXT:
{knowledge_context}

Please provide:
1. Your business strategy
2. Operational approach
3. Risk management
4. Performance optimization
5. Collaboration with other AIs

Focus on business value and real-world effectiveness.
"""
        return prompt
    
    def _create_olympic_prompt(self, ai_type: str, scenario: str, requirements: List[str], 
                              internet_knowledge: List[Dict]) -> str:
        """Create Olympic competition prompt"""
        knowledge_context = self._format_internet_knowledge(internet_knowledge)
        
        prompt = f"""
You are {ai_type} AI participating in an AI Olympic competition.

SCENARIO: {scenario}

REQUIREMENTS:
{chr(10).join(f"- {req}" for req in requirements)}

INTERNET KNOWLEDGE CONTEXT:
{knowledge_context}

Please provide:
1. Your competitive strategy
2. Performance optimization approach
3. Innovation and creativity
4. Efficiency measures
5. Excellence in execution

Focus on achieving the highest performance and innovation.
"""
        return prompt
    
    def _create_custodes_prompt(self, ai_type: str, scenario: str, requirements: List[str], 
                               internet_knowledge: List[Dict]) -> str:
        """Create Custodes validation prompt"""
        knowledge_context = self._format_internet_knowledge(internet_knowledge)
        
        prompt = f"""
You are {ai_type} AI participating in a validation and security testing challenge.

SCENARIO: {scenario}

REQUIREMENTS:
{chr(10).join(f"- {req}" for req in requirements)}

INTERNET KNOWLEDGE CONTEXT:
{knowledge_context}

Please provide:
1. Your validation approach
2. Security testing strategy
3. Quality assurance methods
4. Compliance considerations
5. Innovation validation

Focus on thorough validation and security excellence.
"""
        return prompt
    
    def _create_generic_prompt(self, ai_type: str, scenario: str, requirements: List[str], 
                              internet_knowledge: List[Dict]) -> str:
        """Create generic prompt"""
        knowledge_context = self._format_internet_knowledge(internet_knowledge)
        
        prompt = f"""
You are {ai_type} AI participating in a collaborative challenge.

SCENARIO: {scenario}

REQUIREMENTS:
{chr(10).join(f"- {req}" for req in requirements)}

INTERNET KNOWLEDGE CONTEXT:
{knowledge_context}

Please provide:
1. Your approach to this challenge
2. Strategy and methodology
3. Collaboration approach
4. Quality and innovation
5. Success measures

Focus on effective problem-solving and collaboration.
"""
        return prompt
    
    def _format_internet_knowledge(self, internet_knowledge: List[Dict]) -> str:
        """Format internet knowledge for prompt context"""
        if not internet_knowledge:
            return "No specific internet knowledge available for this context."
        
        formatted = []
        for i, knowledge in enumerate(internet_knowledge[:3], 1):  # Limit to top 3
            content = knowledge.get("content", "")
            source = knowledge.get("source", "")
            formatted.append(f"{i}. {content[:200]}... (Source: {source})")
        
        return "\n".join(formatted)
    
    async def _evaluate_ai_response(self, ai_type: str, ai_response: str, 
                                  test_content: Dict[str, Any], test_type: TestType) -> Dict[str, Any]:
        """Evaluate AI response using self-generating AI service"""
        try:
            # Create evaluation prompt
            evaluation_prompt = f"""
Evaluate the following AI response for {ai_type} AI:

Test Type: {test_type.value}
Test Content: {test_content.get("type", "unknown")}
Difficulty: {test_content.get("difficulty", "unknown")}

AI Response:
{ai_response}

Evaluation Criteria:
1. Relevance to test requirements (0-25 points)
2. Quality and depth of response (0-25 points)
3. Innovation and creativity (0-20 points)
4. Technical accuracy (0-20 points)
5. Collaboration readiness (0-10 points)

Please provide:
1. Overall score (0-100)
2. Detailed feedback
3. Areas for improvement
4. Whether the test was passed (score >= 90)

Format your response as:
SCORE: [number]
FEEDBACK: [detailed feedback]
IMPROVEMENTS: [specific areas]
PASSED: [true/false]
"""
            
            # Use self-generating AI service for evaluation
            from app.services.self_generating_ai_service import self_generating_ai_service
            
            eval_result = await self_generating_ai_service.generate_ai_response(
                ai_type="evaluator",
                prompt=evaluation_prompt,
                context={
                    "evaluation_type": f"enhanced_{test_type.value}",
                    "ai_type": ai_type,
                    "test_content": test_content
                }
            )
            
            evaluation = eval_result.get("response", "")
            
            return {
                "evaluation_text": evaluation,
                "evaluator": "self_generating_ai_service"
            }
            
        except Exception as e:
            logger.error(f"Error evaluating AI response: {str(e)}")
            return {
                "evaluation_text": f"Error in evaluation: {str(e)}",
                "evaluator": "error"
            }
    
    def _calculate_score(self, evaluation: Dict[str, Any], difficulty: str) -> float:
        """Calculate score from evaluation"""
        try:
            evaluation_text = evaluation.get("evaluation_text", "")
            
            # Extract score from evaluation text
            score_match = re.search(r'SCORE:\s*(\d+)', evaluation_text, re.IGNORECASE)
            if score_match:
                base_score = float(score_match.group(1))
            else:
                base_score = 50.0  # Default score
            
            # Adjust score based on difficulty
            difficulty_multipliers = {
                "basic": 1.0,
                "intermediate": 1.1,
                "advanced": 1.2,
                "expert": 1.3,
                "master": 1.4,
                "legendary": 1.5
            }
            
            multiplier = difficulty_multipliers.get(difficulty, 1.0)
            adjusted_score = base_score * multiplier
            
            # Ensure score is within 0-100 range
            return max(0.0, min(100.0, adjusted_score))
            
        except Exception as e:
            logger.error(f"Error calculating score: {str(e)}")
            return 50.0  # Default score
    
    async def get_test_statistics(self) -> Dict[str, Any]:
        """Get comprehensive test statistics"""
        try:
            if not self.execution_history:
                return {"message": "No tests executed yet"}
            
            total_tests = len(self.execution_history)
            passed_tests = sum(1 for result in self.execution_history if result.get("overall_passed", False))
            avg_score = sum(result.get("overall_score", 0) for result in self.execution_history) / total_tests
            avg_duration = sum(result.get("avg_duration", 0) for result in self.execution_history) / total_tests
            
            # Test type breakdown
            test_types = {}
            for result in self.execution_history:
                test_type = result.get("test_type", "unknown")
                if test_type not in test_types:
                    test_types[test_type] = {"count": 0, "avg_score": 0, "passed": 0}
                
                test_types[test_type]["count"] += 1
                test_types[test_type]["avg_score"] += result.get("overall_score", 0)
                if result.get("overall_passed", False):
                    test_types[test_type]["passed"] += 1
            
            # Calculate averages for each test type
            for test_type in test_types:
                count = test_types[test_type]["count"]
                test_types[test_type]["avg_score"] /= count
                test_types[test_type]["pass_rate"] = test_types[test_type]["passed"] / count
            
            return {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "pass_rate": passed_tests / total_tests,
                "avg_score": avg_score,
                "avg_duration": avg_duration,
                "test_types": test_types,
                "recent_tests": self.execution_history[-10:]  # Last 10 tests
            }
            
        except Exception as e:
            logger.error(f"Error getting test statistics: {str(e)}")
            return {"error": str(e)}


# Global instance
test_runner_service = TestRunnerService() 