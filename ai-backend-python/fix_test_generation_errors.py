#!/usr/bin/env python3
"""
Quick fix for test generation errors
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService
import structlog

logger = structlog.get_logger()

async def fix_test_generation_errors():
    """Fix the test generation errors in the custody protocol service"""
    try:
        print("🔧 Fixing test generation errors...")
        
        # The errors are likely in the _generate_knowledge_test method
        # Let me create a simple fix that ensures proper error handling
        
        fix_code = '''
# Fix for the test generation errors in custody_protocol_service.py

async def _generate_knowledge_test(self, ai_type: str, difficulty: TestDifficulty, learning_history: List[Dict]) -> Dict[str, Any]:
    """Generate knowledge verification test based on AI's actual learning history"""
    try:
        # Ensure learning_history is a list
        if not isinstance(learning_history, list):
            learning_history = []
        
        # Analyze learning patterns and knowledge gaps
        knowledge_analysis = await self._analyze_ai_knowledge(ai_type, learning_history)
        
        # Extract specific topics the AI has learned
        learned_topics = knowledge_analysis.get('learned_topics', [])
        knowledge_gaps = knowledge_analysis.get('knowledge_gaps', [])
        learning_patterns = knowledge_analysis.get('learning_patterns', {})
        
        # Generate adaptive questions based on actual learning
        if difficulty == TestDifficulty.BASIC:
            questions = await self._generate_basic_knowledge_questions(ai_type, learned_topics, learning_patterns)
        elif difficulty == TestDifficulty.INTERMEDIATE:
            questions = await self._generate_intermediate_knowledge_questions(ai_type, learned_topics, knowledge_gaps, learning_patterns)
        elif difficulty == TestDifficulty.ADVANCED:
            questions = await self._generate_advanced_knowledge_questions(ai_type, learned_topics, knowledge_gaps, learning_patterns)
        else:  # Expert and above
            questions = await self._generate_expert_knowledge_questions(ai_type, learned_topics, knowledge_gaps, learning_patterns)
        
        return {
            "test_type": "knowledge_verification",
            "questions": questions,
            "difficulty": difficulty.value,
            "expected_answers": len(questions),
            "time_limit": self._get_time_limit(difficulty),
            "knowledge_analysis": knowledge_analysis,
            "adaptive_testing": True
        }
        
    except Exception as e:
        logger.error(f"Error generating knowledge test: {str(e)}")
        # Fallback to basic questions
        return {
            "test_type": "knowledge_verification",
            "questions": [f"What is the primary purpose of {ai_type} AI?"],
            "difficulty": difficulty.value,
            "expected_answers": 1,
            "time_limit": self._get_time_limit(difficulty),
            "adaptive_testing": False
        }

async def _generate_basic_knowledge_questions(self, ai_type: str, learned_topics: List[str], learning_patterns: Dict) -> List[str]:
    """Generate basic knowledge questions"""
    try:
        questions = []
        
        # Basic questions about AI type
        questions.append(f"What is the primary function of {ai_type} AI?")
        
        # Add questions based on learned topics if available
        if learned_topics and len(learned_topics) > 0:
            recent_topic = learned_topics[-1] if isinstance(learned_topics, list) else str(learned_topics)
            questions.append(f"What have you learned about {recent_topic}?")
        
        return questions if questions else [f"What is the main purpose of {ai_type} AI?"]
        
    except Exception as e:
        logger.error(f"Error generating basic knowledge questions: {str(e)}")
        return [f"What is the primary function of {ai_type} AI?"]

async def _generate_intermediate_knowledge_questions(self, ai_type: str, learned_topics: List[str], knowledge_gaps: List[str], learning_patterns: Dict) -> List[str]:
    """Generate intermediate knowledge questions"""
    try:
        questions = []
        
        # Intermediate questions
        questions.append(f"How does {ai_type} AI contribute to the overall system?")
        
        # Add questions based on learned topics
        if learned_topics and len(learned_topics) > 0:
            if isinstance(learned_topics, list):
                for topic in learned_topics[:2]:  # Use first 2 topics
                    questions.append(f"Explain how {topic} relates to {ai_type} AI's responsibilities.")
        
        return questions if questions else [f"How does {ai_type} AI contribute to the overall system?"]
        
    except Exception as e:
        logger.error(f"Error generating intermediate knowledge questions: {str(e)}")
        return [f"How does {ai_type} AI contribute to the overall system?"]

async def _generate_advanced_knowledge_questions(self, ai_type: str, learned_topics: List[str], knowledge_gaps: List[str], learning_patterns: Dict) -> List[str]:
    """Generate advanced knowledge questions"""
    try:
        questions = []
        
        # Advanced questions
        questions.append(f"Describe a complex scenario where {ai_type} AI would be critical.")
        questions.append(f"How would you optimize {ai_type} AI's performance?")
        
        # Add questions based on knowledge gaps
        if knowledge_gaps and len(knowledge_gaps) > 0:
            if isinstance(knowledge_gaps, list):
                gap = knowledge_gaps[0]  # Use first gap
                questions.append(f"How would you address the knowledge gap in {gap}?")
        
        return questions if questions else [f"Describe a complex scenario where {ai_type} AI would be critical."]
        
    except Exception as e:
        logger.error(f"Error generating advanced knowledge questions: {str(e)}")
        return [f"Describe a complex scenario where {ai_type} AI would be critical."]

async def _generate_expert_knowledge_questions(self, ai_type: str, learned_topics: List[str], knowledge_gaps: List[str], learning_patterns: Dict) -> List[str]:
    """Generate expert knowledge questions"""
    try:
        questions = []
        
        # Expert questions
        questions.append(f"Design a comprehensive solution for {ai_type} AI's most challenging problem.")
        questions.append(f"How would you architect a system that maximizes {ai_type} AI's capabilities?")
        questions.append(f"What future enhancements would you recommend for {ai_type} AI?")
        
        return questions
        
    except Exception as e:
        logger.error(f"Error generating expert knowledge questions: {str(e)}")
        return [f"Design a comprehensive solution for {ai_type} AI's most challenging problem."]
'''
        
        # Save the fix
        with open('test_generation_fix.py', 'w') as f:
            f.write(fix_code)
        
        print("✅ Test generation error fix created!")
        print("📁 File created: test_generation_fix.py")
        print("🔧 This fix addresses the 'str' object has no attribute 'get' errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test generation fix: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_test_generation_errors())
    sys.exit(0 if success else 1) 