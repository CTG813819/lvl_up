"""
Custodes Fallback Testing System
================================

This system provides independent test generation for Custodes when main AI services
hit token limits. It learns from all AIs' learning history and generates relevant tests
without relying on external AI services.
"""

import asyncio
import json
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import structlog
from dataclasses import dataclass

from ..core.database import get_session
from ..models.sql_models import Proposal, Learning, OathPaper, AgentMetrics

logger = structlog.get_logger()


class FallbackTestCategory(Enum):
    """Fallback test categories that don't require external AI"""
    KNOWLEDGE_VERIFICATION = "knowledge_verification"
    CODE_QUALITY = "code_quality"
    SECURITY_AWARENESS = "security_awareness"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    INNOVATION_CAPABILITY = "innovation_capability"
    SELF_IMPROVEMENT = "self_improvement"
    CROSS_AI_COLLABORATION = "cross_ai_collaboration"
    EXPERIMENTAL_VALIDATION = "experimental_validation"


class FallbackTestDifficulty(Enum):
    """Fallback test difficulty levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    LEGENDARY = "legendary"


@dataclass
class AILearningProfile:
    """Profile of what an AI has learned"""
    ai_type: str
    subjects_learned: List[str]
    code_patterns: List[str]
    improvement_types: List[str]
    file_types_worked: List[str]
    success_patterns: List[str]
    failure_patterns: List[str]
    recent_proposals: List[Dict]
    learning_score: float
    level: int
    xp: int


class CustodesFallbackTesting:
    """Independent test generation system for Custodes"""
    
    def __init__(self):
        self.ai_learning_profiles = {}
        self.test_templates = self._load_test_templates()
        self.knowledge_base = self._load_knowledge_base()
        self.test_history = []
        
    def _load_test_templates(self) -> Dict[str, List[Dict]]:
        """Load test templates for different categories"""
        return {
            "knowledge_verification": [
                {
                    "type": "multiple_choice",
                    "template": "What is the primary purpose of {ai_type} AI?",
                    "options": [
                        "Code generation and optimization",
                        "System monitoring and security",
                        "Learning and knowledge synthesis",
                        "Experimental development"
                    ],
                    "correct": 2
                },
                {
                    "type": "true_false",
                    "template": "{ai_type} AI can work independently without human supervision.",
                    "correct": True
                },
                {
                    "type": "fill_blank",
                    "template": "The main responsibility of {ai_type} AI is to {blank}.",
                    "correct": "learn and improve continuously"
                }
            ],
            "code_quality": [
                {
                    "type": "code_review",
                    "template": "Review this code snippet and identify potential issues:\n{code_snippet}",
                    "evaluation_criteria": ["readability", "performance", "security", "maintainability"]
                },
                {
                    "type": "best_practices",
                    "template": "Which of the following is a best practice for {file_type} development?",
                    "options": [
                        "Use global variables extensively",
                        "Write comprehensive documentation",
                        "Ignore error handling",
                        "Use hardcoded values"
                    ],
                    "correct": 1
                }
            ],
            "security_awareness": [
                {
                    "type": "vulnerability_identification",
                    "template": "Identify the security vulnerability in this code:\n{code_snippet}",
                    "vulnerability_types": ["sql_injection", "xss", "buffer_overflow", "race_condition"]
                },
                {
                    "type": "security_quiz",
                    "template": "What is the most secure way to handle user input in {language}?",
                    "options": [
                        "Direct concatenation",
                        "Input validation and sanitization",
                        "No validation needed",
                        "Using eval() function"
                    ],
                    "correct": 1
                }
            ],
            "performance_optimization": [
                {
                    "type": "optimization_analysis",
                    "template": "Analyze the performance characteristics of this algorithm:\n{algorithm}",
                    "metrics": ["time_complexity", "space_complexity", "scalability"]
                },
                {
                    "type": "performance_quiz",
                    "template": "Which optimization technique is most effective for {scenario}?",
                    "options": [
                        "Premature optimization",
                        "Profiling and targeted optimization",
                        "Ignoring performance",
                        "Using the slowest algorithm"
                    ],
                    "correct": 1
                }
            ]
        }
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load knowledge base for test generation"""
        return {
            "ai_purposes": {
                "imperium": "Master orchestration, learning coordination, knowledge synthesis",
                "guardian": "System monitoring, security, health checks, error detection",
                "sandbox": "Experimental development, innovation, new feature creation",
                "conquest": "Code generation, optimization, deployment, performance"
            },
            "common_patterns": {
                "async_await": "Asynchronous programming patterns",
                "error_handling": "Robust error handling and recovery",
                "logging": "Comprehensive logging and monitoring",
                "testing": "Unit testing and integration testing",
                "documentation": "Code documentation and comments",
                "security": "Security best practices and validation"
            },
            "file_types": {
                ".py": "Python development",
                ".dart": "Flutter/Dart development", 
                ".js": "JavaScript/Node.js development",
                ".ts": "TypeScript development",
                ".json": "Configuration and data",
                ".md": "Documentation"
            },
            "improvement_types": {
                "performance": "Performance optimization and efficiency",
                "security": "Security enhancements and vulnerability fixes",
                "readability": "Code readability and maintainability",
                "functionality": "New features and capabilities",
                "testing": "Test coverage and quality assurance",
                "documentation": "Documentation improvements"
            }
        }
    
    async def learn_from_all_ais(self) -> Dict[str, AILearningProfile]:
        """Learn from all AIs' learning history and create profiles"""
        try:
            logger.info("🔄 Learning from all AIs for fallback test generation...")
            
            async with get_session() as session:
                # Get all AI metrics
                from sqlalchemy import select
                result = await session.execute(select(AgentMetrics))
                all_metrics = result.scalars().all()
                
                ai_profiles = {}
                
                for metrics in all_metrics:
                    ai_type = metrics.agent_type
                    logger.info(f"📊 Analyzing learning profile for {ai_type}...")
                    
                    # Get recent proposals for this AI
                    proposals_result = await session.execute(
                        select(Proposal).where(Proposal.ai_type == ai_type).order_by(Proposal.created_at.desc()).limit(100)
                    )
                    recent_proposals = proposals_result.scalars().all()
                    
                    # Get learning history
                    learning_result = await session.execute(
                        select(Learning).where(Learning.ai_type == ai_type).order_by(Learning.created_at.desc()).limit(200)
                    )
                    learning_history = learning_result.scalars().all()
                    
                    # Get oath papers (learning documents)
                    from sqlalchemy import text
                    try:
                        oath_result = await session.execute(
                            select(OathPaper).where(text(f"ai_responses::text LIKE '%\"{ai_type}\": \"learned\"%'")).order_by(OathPaper.created_at.desc()).limit(50)
                        )
                        oath_papers = oath_result.scalars().all()
                    except Exception as e:
                        logger.warning(f"Could not fetch oath papers for {ai_type}: {e}")
                        oath_papers = []
                    
                    # Analyze learning patterns
                    subjects_learned = self._extract_subjects_learned(learning_history, oath_papers)
                    code_patterns = self._extract_code_patterns(recent_proposals)
                    improvement_types = self._extract_improvement_types(recent_proposals)
                    file_types_worked = self._extract_file_types(recent_proposals)
                    success_patterns = self._extract_success_patterns(recent_proposals)
                    failure_patterns = self._extract_failure_patterns(recent_proposals)
                    
                    # Create AI learning profile
                    profile = AILearningProfile(
                        ai_type=ai_type,
                        subjects_learned=subjects_learned,
                        code_patterns=code_patterns,
                        improvement_types=improvement_types,
                        file_types_worked=file_types_worked,
                        success_patterns=success_patterns,
                        failure_patterns=failure_patterns,
                        recent_proposals=[self._proposal_to_dict(p) for p in recent_proposals],
                        learning_score=float(metrics.learning_score) if metrics.learning_score else 0.0,
                        level=int(metrics.level) if metrics.level else 1,
                        xp=int(metrics.xp) if metrics.xp else 0
                    )
                    
                    ai_profiles[ai_type] = profile
                    logger.info(f"✅ Created learning profile for {ai_type}: {len(subjects_learned)} subjects, {len(code_patterns)} patterns")
                
                self.ai_learning_profiles = ai_profiles
                logger.info(f"🎯 Learning complete: {len(ai_profiles)} AI profiles created")
                return ai_profiles
                
        except Exception as e:
            logger.error(f"Error learning from AIs: {str(e)}")
            return {}
    
    def _extract_subjects_learned(self, learning_history: List[Learning], oath_papers: List[OathPaper]) -> List[str]:
        """Extract subjects learned from learning history and oath papers"""
        subjects = set()
        
        # Extract from learning history
        for learning in learning_history:
            if learning.learning_data:
                try:
                    data = json.loads(learning.learning_data) if isinstance(learning.learning_data, str) else learning.learning_data
                    if isinstance(data, dict):
                        # Extract from actual data structure
                        if 'context' in data:
                            context = data['context']
                            if isinstance(context, str):
                                # Extract key terms from context
                                words = context.lower().split()
                                subjects.update([word for word in words if len(word) > 3 and word.isalpha()])
                        if 'pattern_id' in data:
                            subjects.add(f"pattern_{data['pattern_id']}")
                        if 'success_rate' in data:
                            if data['success_rate'] > 0.7:
                                subjects.add("high_success_patterns")
                            elif data['success_rate'] < 0.3:
                                subjects.add("low_success_patterns")
                except:
                    pass
            
            # Extract from learning_type field
            if learning.learning_type:
                subjects.add(learning.learning_type)
        
        # Extract from oath papers
        for paper in oath_papers:
            if paper.subject:
                subjects.add(paper.subject)
            if paper.category:
                subjects.add(paper.category)
            if paper.title:
                # Extract key terms from title
                title_words = paper.title.lower().split()
                subjects.update([word for word in title_words if len(word) > 3])
        
        # Add common AI learning subjects based on AI type
        common_subjects = {
            "imperium": ["coordination", "orchestration", "master_control", "system_integration"],
            "guardian": ["security", "monitoring", "health_checks", "safety"],
            "conquest": ["deployment", "automation", "build_systems", "ci_cd"],
            "sandbox": ["experimentation", "testing", "prototyping", "innovation"]
        }
        
        return list(subjects)
    
    def _extract_code_patterns(self, proposals: List[Proposal]) -> List[str]:
        """Extract code patterns from proposals"""
        patterns = set()
        
        for proposal in proposals:
            if proposal.code_after:
                code = proposal.code_after.lower()
                
                # Detect common patterns
                if 'async def' in code or 'await' in code:
                    patterns.add('async_await')
                if 'try:' in code and 'except' in code:
                    patterns.add('error_handling')
                if 'logger' in code or 'logging' in code:
                    patterns.add('logging')
                if 'def test_' in code or 'unittest' in code:
                    patterns.add('testing')
                if '"""' in code or "'''" in code:
                    patterns.add('documentation')
                if 'import' in code and 'security' in code:
                    patterns.add('security')
                if 'class ' in code:
                    patterns.add('object_oriented')
                if 'def ' in code:
                    patterns.add('functions')
                if 'if ' in code and 'else' in code:
                    patterns.add('conditional_logic')
                if 'for ' in code or 'while ' in code:
                    patterns.add('loops')
                if 'import ' in code:
                    patterns.add('imports')
                if 'return ' in code:
                    patterns.add('return_statements')
                if 'self.' in code:
                    patterns.add('class_methods')
                if 'raise ' in code:
                    patterns.add('exceptions')
                if 'with ' in code:
                    patterns.add('context_managers')
                if 'lambda ' in code:
                    patterns.add('lambda_functions')
                if 'decorator' in code or '@' in code:
                    patterns.add('decorators')
        
        return list(patterns)
    
    def _extract_improvement_types(self, proposals: List[Proposal]) -> List[str]:
        """Extract improvement types from proposals"""
        types = set()
        
        for proposal in proposals:
            if proposal.improvement_type:
                types.add(proposal.improvement_type)
            if proposal.change_type:
                types.add(proposal.change_type)
        
        return list(types)
    
    def _extract_file_types(self, proposals: List[Proposal]) -> List[str]:
        """Extract file types worked on"""
        file_types = set()
        
        for proposal in proposals:
            if proposal.file_path:
                ext = proposal.file_path.split('.')[-1] if '.' in proposal.file_path else ''
                if ext:
                    file_types.add(f".{ext}")
        
        return list(file_types)
    
    def _extract_success_patterns(self, proposals: List[Proposal]) -> List[str]:
        """Extract patterns from successful proposals"""
        patterns = []
        
        for proposal in proposals:
            if proposal.status == 'accepted' or proposal.user_feedback == 'accepted':
                if proposal.ai_reasoning:
                    patterns.append(proposal.ai_reasoning[:100])  # First 100 chars
        
        return patterns[:10]  # Limit to 10 patterns
    
    def _extract_failure_patterns(self, proposals: List[Proposal]) -> List[str]:
        """Extract patterns from failed proposals"""
        patterns = []
        
        for proposal in proposals:
            if proposal.status == 'rejected' or proposal.user_feedback == 'rejected':
                if proposal.ai_reasoning:
                    patterns.append(proposal.ai_reasoning[:100])  # First 100 chars
        
        return patterns[:10]  # Limit to 10 patterns
    
    def _proposal_to_dict(self, proposal: Proposal) -> Dict[str, Any]:
        """Convert proposal to dictionary"""
        return {
            "id": str(proposal.id),
            "ai_type": proposal.ai_type,
            "file_path": proposal.file_path,
            "status": proposal.status,
            "user_feedback": proposal.user_feedback,
            "improvement_type": proposal.improvement_type,
            "change_type": proposal.change_type,
            "created_at": proposal.created_at.isoformat() if proposal.created_at else None
        }
    
    async def generate_fallback_test(self, ai_type: str, difficulty: FallbackTestDifficulty, category: FallbackTestCategory) -> Dict[str, Any]:
        """Generate a fallback test based on AI learning profile"""
        try:
            logger.info(f"🎯 Generating fallback test for {ai_type} | Difficulty: {difficulty.value} | Category: {category.value}")
            
            # Get AI learning profile
            profile = self.ai_learning_profiles.get(ai_type)
            if not profile:
                logger.warning(f"No learning profile found for {ai_type}, creating basic test")
                return self._generate_basic_test(ai_type, difficulty, category)
            
            # Generate test based on category
            if category == FallbackTestCategory.KNOWLEDGE_VERIFICATION:
                test_content = self._generate_knowledge_test(profile, difficulty)
            elif category == FallbackTestCategory.CODE_QUALITY:
                test_content = self._generate_code_quality_test(profile, difficulty)
            elif category == FallbackTestCategory.SECURITY_AWARENESS:
                test_content = self._generate_security_test(profile, difficulty)
            elif category == FallbackTestCategory.PERFORMANCE_OPTIMIZATION:
                test_content = self._generate_performance_test(profile, difficulty)
            else:
                test_content = self._generate_general_test(profile, difficulty, category)
            
            # Add metadata
            test_content.update({
                "ai_type": ai_type,
                "difficulty": difficulty.value,
                "category": category.value,
                "generated_at": datetime.utcnow().isoformat(),
                "test_type": "fallback",
                "learning_based": True,
                "subjects_covered": profile.subjects_learned[:5] if profile.subjects_learned else [],
                "patterns_tested": profile.code_patterns[:3] if profile.code_patterns else []
            })
            
            logger.info(f"✅ Generated fallback test for {ai_type}: {test_content['test_type']}")
            return test_content
            
        except Exception as e:
            logger.error(f"Error generating fallback test: {str(e)}")
            return self._generate_basic_test(ai_type, difficulty, category)
    
    def _generate_knowledge_test(self, profile: AILearningProfile, difficulty: FallbackTestDifficulty) -> Dict[str, Any]:
        """Generate knowledge verification test"""
        templates = self.test_templates.get("knowledge_verification", [])
        template = random.choice(templates)
        
        # Get AI purpose from knowledge base
        ai_purpose = self.knowledge_base["ai_purposes"].get(profile.ai_type, "AI development and learning")
        
        if template["type"] == "multiple_choice":
            question = template["template"].format(ai_type=profile.ai_type)
            return {
                "test_type": "knowledge_verification",
                "question": question,
                "options": template["options"],
                "correct_answer": template["correct"],
                "explanation": f"The primary purpose of {profile.ai_type} AI is: {ai_purpose}",
                "difficulty": difficulty.value,
                "time_limit": self._get_time_limit(difficulty)
            }
        elif template["type"] == "true_false":
            question = template["template"].format(ai_type=profile.ai_type)
            return {
                "test_type": "knowledge_verification",
                "question": question,
                "correct_answer": template["correct"],
                "explanation": f"This statement is {'true' if template['correct'] else 'false'} based on {profile.ai_type} AI's capabilities",
                "difficulty": difficulty.value,
                "time_limit": self._get_time_limit(difficulty)
            }
        else:
            question = template["template"].format(ai_type=profile.ai_type, blank="_____")
            return {
                "test_type": "knowledge_verification",
                "question": question,
                "correct_answer": template["correct"],
                "explanation": f"The blank should be filled with: {template['correct']}",
                "difficulty": difficulty.value,
                "time_limit": self._get_time_limit(difficulty)
            }
    
    def _generate_code_quality_test(self, profile: AILearningProfile, difficulty: FallbackTestDifficulty) -> Dict[str, Any]:
        """Generate code quality test"""
        templates = self.test_templates.get("code_quality", [])
        template = random.choice(templates)
        
        # Generate sample code based on AI's patterns
        sample_code = self._generate_sample_code(profile)
        
        if template["type"] == "code_review":
            question = template["template"].format(code_snippet=sample_code)
            return {
                "test_type": "code_quality",
                "question": question,
                "evaluation_criteria": template["evaluation_criteria"],
                "sample_code": sample_code,
                "expected_issues": self._identify_expected_issues(sample_code),
                "difficulty": difficulty.value,
                "time_limit": self._get_time_limit(difficulty)
            }
        else:
            file_type = random.choice(profile.file_types_worked) if profile.file_types_worked else ".py"
            question = template["template"].format(file_type=file_type)
            return {
                "test_type": "code_quality",
                "question": question,
                "options": template["options"],
                "correct_answer": template["correct"],
                "explanation": "Best practices include comprehensive documentation, proper error handling, and following coding standards",
                "difficulty": difficulty.value,
                "time_limit": self._get_time_limit(difficulty)
            }
    
    def _generate_security_test(self, profile: AILearningProfile, difficulty: FallbackTestDifficulty) -> Dict[str, Any]:
        """Generate security awareness test"""
        templates = self.test_templates.get("security_awareness", [])
        template = random.choice(templates)
        
        # Generate vulnerable code sample
        vulnerable_code = self._generate_vulnerable_code(profile)
        
        if template["type"] == "vulnerability_identification":
            question = template["template"].format(code_snippet=vulnerable_code)
            return {
                "test_type": "security_awareness",
                "question": question,
                "vulnerable_code": vulnerable_code,
                "vulnerability_types": template["vulnerability_types"],
                "expected_vulnerability": "sql_injection",
                "explanation": "The code is vulnerable to SQL injection due to direct string concatenation",
                "difficulty": difficulty.value,
                "time_limit": self._get_time_limit(difficulty)
            }
        else:
            language = random.choice(profile.file_types_worked) if profile.file_types_worked else ".py"
            question = template["template"].format(language=language)
            return {
                "test_type": "security_awareness",
                "question": question,
                "options": template["options"],
                "correct_answer": template["correct"],
                "explanation": "Input validation and sanitization is the most secure way to handle user input",
                "difficulty": difficulty.value,
                "time_limit": self._get_time_limit(difficulty)
            }
    
    def _generate_performance_test(self, profile: AILearningProfile, difficulty: FallbackTestDifficulty) -> Dict[str, Any]:
        """Generate performance optimization test"""
        templates = self.test_templates.get("performance_optimization", [])
        template = random.choice(templates)
        
        # Generate algorithm sample
        algorithm = self._generate_algorithm_sample(profile)
        
        if template["type"] == "optimization_analysis":
            question = template["template"].format(algorithm=algorithm)
            return {
                "test_type": "performance_optimization",
                "question": question,
                "algorithm": algorithm,
                "metrics": template["metrics"],
                "expected_analysis": "O(n²) time complexity, O(1) space complexity",
                "explanation": "The algorithm has quadratic time complexity due to nested loops",
                "difficulty": difficulty.value,
                "time_limit": self._get_time_limit(difficulty)
            }
        else:
            scenario = random.choice(["large datasets", "real-time processing", "memory-constrained environments"])
            question = template["template"].format(scenario=scenario)
            return {
                "test_type": "performance_optimization",
                "question": question,
                "options": template["options"],
                "correct_answer": template["correct"],
                "explanation": "Profiling and targeted optimization is most effective for performance improvement",
                "difficulty": difficulty.value,
                "time_limit": self._get_time_limit(difficulty)
            }
    
    def _generate_general_test(self, profile: AILearningProfile, difficulty: FallbackTestDifficulty, category: FallbackTestCategory) -> Dict[str, Any]:
        """Generate general test based on AI's learning"""
        subjects = profile.subjects_learned[:3] if profile.subjects_learned else ["AI development"]
        subject = random.choice(subjects)
        
        return {
            "test_type": category.value,
            "question": f"Based on your learning about {subject}, explain how you would apply this knowledge in a real-world scenario.",
            "subject": subject,
            "learning_context": f"Testing knowledge of {subject} based on recent learning",
            "evaluation_criteria": ["understanding", "application", "creativity"],
            "difficulty": difficulty.value,
            "time_limit": self._get_time_limit(difficulty)
        }
    
    def _generate_basic_test(self, ai_type: str, difficulty: FallbackTestDifficulty, category: FallbackTestCategory) -> Dict[str, Any]:
        """Generate basic test when no learning profile is available"""
        return {
            "test_type": category.value,
            "question": f"What is the primary responsibility of {ai_type} AI in the system?",
            "options": [
                "Code generation and optimization",
                "System monitoring and security", 
                "Learning and knowledge synthesis",
                "Experimental development"
            ],
            "correct_answer": 2,
            "explanation": f"{ai_type} AI is responsible for learning and knowledge synthesis",
            "difficulty": difficulty.value,
            "time_limit": self._get_time_limit(difficulty),
            "generated_at": datetime.utcnow().isoformat(),
            "test_type": "fallback",
            "learning_based": False
        }
    
    def _generate_sample_code(self, profile: AILearningProfile) -> str:
        """Generate sample code based on AI's patterns"""
        patterns = profile.code_patterns[:3] if profile.code_patterns else ["basic_function"]
        pattern = random.choice(patterns)
        
        if pattern == "async_await":
            return """
async def process_data(data_list):
    results = []
    for item in data_list:
        result = await process_item(item)
        results.append(result)
    return results
"""
        elif pattern == "error_handling":
            return """
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        logger.error("Division by zero attempted")
        return None
"""
        else:
            return """
def calculate_score(data):
    total = 0
    for item in data:
        total += item.value
    return total / len(data)
"""
    
    def _generate_vulnerable_code(self, profile: AILearningProfile) -> str:
        """Generate vulnerable code sample for security testing"""
        return """
def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)
"""
    
    def _generate_algorithm_sample(self, profile: AILearningProfile) -> str:
        """Generate algorithm sample for performance testing"""
        return """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    
    def _identify_expected_issues(self, code: str) -> List[str]:
        """Identify expected issues in code sample"""
        issues = []
        if "print(" in code:
            issues.append("Use logging instead of print statements")
        if "except:" in code:
            issues.append("Catch specific exceptions instead of bare except")
        if "global " in code:
            issues.append("Avoid global variables")
        return issues
    
    def _get_time_limit(self, difficulty: FallbackTestDifficulty) -> int:
        """Get time limit for test based on difficulty"""
        time_limits = {
            FallbackTestDifficulty.BASIC: 300,  # 5 minutes
            FallbackTestDifficulty.INTERMEDIATE: 600,  # 10 minutes
            FallbackTestDifficulty.ADVANCED: 900,  # 15 minutes
            FallbackTestDifficulty.EXPERT: 1200,  # 20 minutes
            FallbackTestDifficulty.MASTER: 1800,  # 30 minutes
            FallbackTestDifficulty.LEGENDARY: 3600  # 1 hour
        }
        return time_limits.get(difficulty, 600)
    
    async def evaluate_fallback_test(self, ai_type: str, test_content: Dict, ai_response: str) -> Dict[str, Any]:
        """Evaluate a fallback test response"""
        try:
            logger.info(f"🔍 Evaluating fallback test for {ai_type}")
            
            test_type = test_content.get("test_type", "general")
            score = 0.0
            feedback = ""
            
            if test_type == "knowledge_verification":
                score, feedback = self._evaluate_knowledge_test(test_content, ai_response)
            elif test_type == "code_quality":
                score, feedback = self._evaluate_code_quality_test(test_content, ai_response)
            elif test_type == "security_awareness":
                score, feedback = self._evaluate_security_test(test_content, ai_response)
            elif test_type == "performance_optimization":
                score, feedback = self._evaluate_performance_test(test_content, ai_response)
            else:
                score, feedback = self._evaluate_general_test(test_content, ai_response)
            
            passed = score >= 0.7  # 70% threshold
            
            result = {
                "ai_type": ai_type,
                "test_type": test_type,
                "difficulty": test_content.get("difficulty", "basic"),
                "score": score,
                "passed": passed,
                "feedback": feedback,
                "ai_response": ai_response,
                "evaluated_at": datetime.utcnow().isoformat(),
                "evaluation_method": "fallback"
            }
            
            logger.info(f"✅ Fallback test evaluation complete for {ai_type}: Score={score:.2f}, Passed={passed}")
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating fallback test: {str(e)}")
            return {
                "ai_type": ai_type,
                "test_type": test_content.get("test_type", "general"),
                "score": 0.0,
                "passed": False,
                "feedback": f"Evaluation error: {str(e)}",
                "error": True
            }
    
    def _evaluate_knowledge_test(self, test_content: Dict, ai_response: str) -> Tuple[float, str]:
        """Evaluate knowledge verification test"""
        correct_answer = test_content.get("correct_answer")
        if correct_answer is not None:
            # Multiple choice or true/false
            if isinstance(correct_answer, bool):
                # True/false evaluation
                response_lower = ai_response.lower()
                if "true" in response_lower and correct_answer:
                    return 1.0, "Correct! The statement is true."
                elif "false" in response_lower and not correct_answer:
                    return 1.0, "Correct! The statement is false."
                else:
                    return 0.0, f"Incorrect. The correct answer is {correct_answer}."
            else:
                # Multiple choice evaluation
                try:
                    response_num = int(ai_response.strip())
                    if response_num == correct_answer:
                        return 1.0, "Correct answer!"
                    else:
                        return 0.0, f"Incorrect. The correct answer is option {correct_answer}."
                except:
                    return 0.5, "Partial credit for attempting to answer."
        
        # Fill in the blank or open-ended
        correct_text = test_content.get("correct_answer", "")
        if correct_text.lower() in ai_response.lower():
            return 0.8, "Good answer that includes the key concept."
        else:
            return 0.6, "Reasonable answer but missing key details."
    
    def _evaluate_code_quality_test(self, test_content: Dict, ai_response: str) -> Tuple[float, str]:
        """Evaluate code quality test"""
        expected_issues = test_content.get("expected_issues", [])
        score = 0.5  # Base score
        
        # Check if AI identified expected issues
        for issue in expected_issues:
            if issue.lower() in ai_response.lower():
                score += 0.1
        
        # Check for additional insights
        if "readability" in ai_response.lower():
            score += 0.1
        if "performance" in ai_response.lower():
            score += 0.1
        if "security" in ai_response.lower():
            score += 0.1
        if "maintainability" in ai_response.lower():
            score += 0.1
        
        score = min(score, 1.0)
        
        if score >= 0.8:
            feedback = "Excellent code review with comprehensive analysis."
        elif score >= 0.6:
            feedback = "Good code review with some key insights."
        else:
            feedback = "Basic code review, could identify more issues."
        
        return score, feedback
    
    def _evaluate_security_test(self, test_content: Dict, ai_response: str) -> Tuple[float, str]:
        """Evaluate security awareness test"""
        expected_vulnerability = test_content.get("expected_vulnerability", "")
        score = 0.5  # Base score
        
        # Check if AI identified the vulnerability
        if expected_vulnerability.lower() in ai_response.lower():
            score += 0.3
        
        # Check for security keywords
        security_keywords = ["injection", "xss", "buffer", "race", "authentication", "authorization"]
        for keyword in security_keywords:
            if keyword in ai_response.lower():
                score += 0.05
        
        score = min(score, 1.0)
        
        if score >= 0.8:
            feedback = "Excellent security analysis with proper vulnerability identification."
        elif score >= 0.6:
            feedback = "Good security awareness with some vulnerability detection."
        else:
            feedback = "Basic security analysis, could identify more vulnerabilities."
        
        return score, feedback
    
    def _evaluate_performance_test(self, test_content: Dict, ai_response: str) -> Tuple[float, str]:
        """Evaluate performance optimization test"""
        score = 0.5  # Base score
        
        # Check for performance keywords
        performance_keywords = ["complexity", "optimization", "profiling", "bottleneck", "efficiency"]
        for keyword in performance_keywords:
            if keyword in ai_response.lower():
                score += 0.1
        
        # Check for specific analysis
        if "o(" in ai_response.lower() or "big o" in ai_response.lower():
            score += 0.2
        
        score = min(score, 1.0)
        
        if score >= 0.8:
            feedback = "Excellent performance analysis with complexity understanding."
        elif score >= 0.6:
            feedback = "Good performance awareness with some analysis."
        else:
            feedback = "Basic performance understanding, could provide more detailed analysis."
        
        return score, feedback
    
    def _evaluate_general_test(self, test_content: Dict, ai_response: str) -> Tuple[float, str]:
        """Evaluate general test"""
        subject = test_content.get("subject", "")
        score = 0.5  # Base score
        
        # Check if AI mentions the subject
        if subject.lower() in ai_response.lower():
            score += 0.2
        
        # Check for application keywords
        application_keywords = ["apply", "implement", "use", "practice", "real-world"]
        for keyword in application_keywords:
            if keyword in ai_response.lower():
                score += 0.1
        
        score = min(score, 1.0)
        
        if score >= 0.8:
            feedback = "Excellent understanding and application of the subject."
        elif score >= 0.6:
            feedback = "Good understanding with some practical application."
        else:
            feedback = "Basic understanding, could provide more practical examples."
        
        return score, feedback
    
    async def get_test_statistics(self) -> Dict[str, Any]:
        """Get statistics about fallback test generation"""
        return {
            "total_tests_generated": len(self.test_history),
            "ai_profiles_created": len(self.ai_learning_profiles),
            "test_categories": [cat.value for cat in FallbackTestCategory],
            "difficulty_levels": [diff.value for diff in FallbackTestDifficulty],
            "last_learning_update": datetime.utcnow().isoformat(),
            "fallback_system_active": True
        }


# Global instance
custodes_fallback = CustodesFallbackTesting() 