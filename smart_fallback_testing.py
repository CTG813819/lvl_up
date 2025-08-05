#!/usr/bin/env python3
"""
Smart Fallback Testing System
Intelligently switches between external AI and internal test generation
"""

import asyncio
import sys
import os
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_database
from app.services.custodes_fallback_testing import CustodesFallbackTesting, FallbackTestDifficulty, FallbackTestCategory
from app.services.custody_protocol_service import CustodyProtocolService
from app.services.ai_agent_service import AIAgentService

class SmartFallbackTesting:
    def __init__(self):
        self.fallback_service = CustodesFallbackTesting()
        self.ai_service = AIAgentService()
        self.token_limit = 1000
        self.estimated_tokens = 0
        
    async def generate_smart_test(self, ai_type: str, difficulty: str = "basic", category: str = "knowledge_verification") -> Dict[str, Any]:
        """Generate a test using smart fallback logic"""
        print(f"🧠 Generating smart test for {ai_type}...")
        
        # Step 1: Check if we have rich learning data
        learning_profiles = await self.fallback_service.learn_from_all_ais()
        profile = learning_profiles.get(ai_type)
        
        if not profile or len(profile.subjects_learned) < 5:
            print(f"⚠️  Insufficient learning data for {ai_type}, using basic fallback")
            return await self._generate_basic_fallback_test(ai_type, difficulty, category)
        
        # Step 2: Estimate token usage for external AI
        estimated_tokens = self._estimate_token_usage(profile, difficulty, category)
        
        # Step 3: Try external AI if tokens are available
        if estimated_tokens <= self.token_limit:
            print(f"🔄 Attempting external AI test generation ({estimated_tokens} tokens)...")
            try:
                external_test = await self._generate_external_ai_test(ai_type, profile, difficulty, category)
                if external_test:
                    print(f"✅ External AI test generated successfully")
                    return external_test
            except Exception as e:
                print(f"⚠️  External AI failed: {e}")
        
        # Step 4: Use rich internal test generation
        print(f"🔄 Using rich internal test generation with {len(profile.subjects_learned)} subjects...")
        return await self._generate_rich_internal_test(ai_type, profile, difficulty, category)
    
    def _estimate_token_usage(self, profile, difficulty: str, category: str) -> int:
        """Estimate token usage for external AI request"""
        base_tokens = 200  # Base prompt tokens
        
        # Add tokens for learning data
        subjects_tokens = len(profile.subjects_learned) * 5  # ~5 tokens per subject
        patterns_tokens = len(profile.code_patterns) * 10    # ~10 tokens per pattern
        improvements_tokens = len(profile.improvement_types) * 8  # ~8 tokens per improvement
        
        # Add difficulty multiplier
        difficulty_multiplier = {
            "basic": 1.0,
            "intermediate": 1.5,
            "advanced": 2.0,
            "expert": 2.5,
            "master": 3.0,
            "legendary": 3.5
        }.get(difficulty, 1.0)
        
        total_tokens = int((base_tokens + subjects_tokens + patterns_tokens + improvements_tokens) * difficulty_multiplier)
        return min(total_tokens, 2000)  # Cap at 2000 tokens
    
    async def _generate_external_ai_test(self, ai_type: str, profile, difficulty: str, category: str) -> Optional[Dict[str, Any]]:
        """Generate test using external AI"""
        try:
            # Create a focused prompt with key learning data
            subjects_sample = profile.subjects_learned[:20]  # Limit to 20 subjects
            patterns_sample = profile.code_patterns[:5]      # Limit to 5 patterns
            
            prompt = f"""
            Generate a {difficulty} level {category} test for {ai_type} AI based on their learning profile:
            
            Subjects learned: {', '.join(subjects_sample)}
            Code patterns: {', '.join(patterns_sample)}
            Improvement types: {', '.join(profile.improvement_types)}
            File types worked: {', '.join(profile.file_types_worked)}
            Learning score: {profile.learning_score}
            Level: {profile.level}
            
            Create a comprehensive test that challenges the AI's knowledge in these areas.
            """
            
            # Use AI service to generate test
            response_obj = await self.ai_service.process_request(
                ai_name=ai_type,
                request_type="test_generation",
                prompt=prompt,
                estimated_tokens=1000
            )
            response = response_obj.get("content") if response_obj.get("success") else None
            
            if response and len(response) > 100:
                return {
                    "title": f"External AI {category.title()} Test for {ai_type}",
                    "content": response,
                    "category": category,
                    "difficulty": difficulty,
                    "time_limit": self._get_time_limit(difficulty),
                    "source": "external_ai",
                    "subjects_covered": subjects_sample,
                    "patterns_covered": patterns_sample
                }
            
        except Exception as e:
            print(f"❌ External AI test generation failed: {e}")
        
        return None
    
    async def _generate_rich_internal_test(self, ai_type: str, profile, difficulty: str, category: str) -> Dict[str, Any]:
        """Generate rich internal test using learning data"""
        print(f"🎯 Generating rich internal test for {ai_type} with {len(profile.subjects_learned)} subjects...")
        
        # Select relevant subjects and patterns
        relevant_subjects = self._select_relevant_subjects(profile.subjects_learned, category)
        relevant_patterns = profile.code_patterns[:3] if profile.code_patterns else []
        
        # Generate test based on category
        if category == "knowledge_verification":
            test_content = self._generate_knowledge_test(ai_type, relevant_subjects, relevant_patterns, difficulty)
        elif category == "code_quality":
            test_content = self._generate_code_quality_test(ai_type, relevant_subjects, relevant_patterns, difficulty)
        elif category == "security_awareness":
            test_content = self._generate_security_test(ai_type, relevant_subjects, relevant_patterns, difficulty)
        else:
            test_content = self._generate_general_test(ai_type, relevant_subjects, relevant_patterns, difficulty, category)
        
        return {
            "title": f"Rich Internal {category.title()} Test for {ai_type}",
            "content": test_content,
            "category": category,
            "difficulty": difficulty,
            "time_limit": self._get_time_limit(difficulty),
            "source": "rich_internal",
            "subjects_covered": relevant_subjects,
            "patterns_covered": relevant_patterns,
            "learning_score": profile.learning_score
        }
    
    def _select_relevant_subjects(self, subjects: List[str], category: str) -> List[str]:
        """Select subjects relevant to the test category"""
        if not subjects:
            return []
        
        # Filter subjects by category relevance
        category_keywords = {
            "knowledge_verification": ["pattern", "learning", "analysis", "understanding"],
            "code_quality": ["quality", "performance", "optimization", "best_practices"],
            "security_awareness": ["security", "safety", "vulnerability", "protection"],
            "performance_optimization": ["performance", "optimization", "efficiency", "speed"],
            "innovation_capability": ["innovation", "creativity", "experimentation", "prototyping"]
        }
        
        keywords = category_keywords.get(category, [])
        relevant_subjects = []
        
        for subject in subjects:
            if any(keyword in subject.lower() for keyword in keywords):
                relevant_subjects.append(subject)
        
        # If no relevant subjects found, return random selection
        if not relevant_subjects:
            relevant_subjects = random.sample(subjects, min(10, len(subjects)))
        
        return relevant_subjects[:10]  # Limit to 10 subjects
    
    def _generate_knowledge_test(self, ai_type: str, subjects: List[str], patterns: List[str], difficulty: str) -> str:
        """Generate knowledge verification test"""
        test_content = f"""
# Knowledge Verification Test for {ai_type.upper()} AI
**Difficulty**: {difficulty.title()}
**Time Limit**: {self._get_time_limit(difficulty)} seconds

## Test Overview
This test evaluates your understanding of the subjects and patterns you've learned.

## Subjects Covered
{chr(10).join([f"- {subject}" for subject in subjects])}

## Code Patterns Covered
{chr(10).join([f"- {pattern}" for pattern in patterns])}

## Questions

### 1. Subject Knowledge (25 points)
Based on your learning history, explain how you would apply knowledge from the following subjects:
{chr(10).join([f"- {subject}" for subject in subjects[:3]])}

### 2. Pattern Recognition (25 points)
Describe how you would implement the following patterns in your work:
{chr(10).join([f"- {pattern}" for pattern in patterns])}

### 3. Practical Application (25 points)
Provide a practical example of how you would use your learned knowledge to solve a real-world problem.

### 4. Self-Assessment (25 points)
Reflect on your learning journey and describe:
- Your strongest areas of knowledge
- Areas where you need improvement
- How you plan to continue learning

## Evaluation Criteria
- Depth of understanding (40%)
- Practical application (30%)
- Self-awareness (20%)
- Communication clarity (10%)

**Total Points: 100**
"""
        return test_content
    
    def _generate_code_quality_test(self, ai_type: str, subjects: List[str], patterns: List[str], difficulty: str) -> str:
        """Generate code quality test"""
        test_content = f"""
# Code Quality Test for {ai_type.upper()} AI
**Difficulty**: {difficulty.title()}
**Time Limit**: {self._get_time_limit(difficulty)} seconds

## Test Overview
This test evaluates your understanding of code quality principles and best practices.

## Focus Areas
{chr(10).join([f"- {subject}" for subject in subjects[:5]])}

## Code Patterns
{chr(10).join([f"- {pattern}" for pattern in patterns])}

## Questions

### 1. Code Quality Principles (30 points)
Explain the key principles of code quality and how you apply them in your work.

### 2. Pattern Implementation (30 points)
Show how you would implement the following patterns with high quality:
{chr(10).join([f"- {pattern}" for pattern in patterns])}

### 3. Quality Assurance (25 points)
Describe your approach to ensuring code quality in your projects.

### 4. Continuous Improvement (15 points)
How do you continuously improve your code quality skills?

## Evaluation Criteria
- Understanding of quality principles (40%)
- Practical implementation (30%)
- Quality assurance approach (20%)
- Improvement mindset (10%)

**Total Points: 100**
"""
        return test_content
    
    def _generate_security_test(self, ai_type: str, subjects: List[str], patterns: List[str], difficulty: str) -> str:
        """Generate security awareness test"""
        test_content = f"""
# Security Awareness Test for {ai_type.upper()} AI
**Difficulty**: {difficulty.title()}
**Time Limit**: {self._get_time_limit(difficulty)} seconds

## Test Overview
This test evaluates your understanding of security principles and practices.

## Security Focus Areas
{chr(10).join([f"- {subject}" for subject in subjects[:5]])}

## Questions

### 1. Security Principles (30 points)
Explain the fundamental principles of secure coding and system design.

### 2. Threat Assessment (30 points)
How do you identify and assess security threats in your work?

### 3. Secure Implementation (25 points)
Describe how you implement security measures in your code and systems.

### 4. Security Best Practices (15 points)
What security best practices do you follow in your daily work?

## Evaluation Criteria
- Security knowledge (40%)
- Threat awareness (30%)
- Implementation skills (20%)
- Best practices (10%)

**Total Points: 100**
"""
        return test_content
    
    def _generate_general_test(self, ai_type: str, subjects: List[str], patterns: List[str], difficulty: str, category: str) -> str:
        """Generate general test"""
        test_content = f"""
# {category.title()} Test for {ai_type.upper()} AI
**Difficulty**: {difficulty.title()}
**Time Limit**: {self._get_time_limit(difficulty)} seconds

## Test Overview
This test evaluates your capabilities in {category.replace('_', ' ')}.

## Learning Areas
{chr(10).join([f"- {subject}" for subject in subjects[:5]])}

## Questions

### 1. Core Knowledge (40 points)
Demonstrate your understanding of {category.replace('_', ' ')}.

### 2. Practical Skills (35 points)
Show how you apply your knowledge in practical scenarios.

### 3. Continuous Learning (25 points)
Describe your approach to learning and improvement in this area.

## Evaluation Criteria
- Knowledge depth (50%)
- Practical application (35%)
- Learning mindset (15%)

**Total Points: 100**
"""
        return test_content
    
    async def _generate_basic_fallback_test(self, ai_type: str, difficulty: str, category: str) -> Dict[str, Any]:
        """Generate basic fallback test when learning data is insufficient"""
        return await self.fallback_service.generate_fallback_test(ai_type, 
                                                                  FallbackTestDifficulty(difficulty), 
                                                                  FallbackTestCategory(category))
    
    def _get_time_limit(self, difficulty: str) -> int:
        """Get time limit based on difficulty"""
        return {
            "basic": 300,
            "intermediate": 450,
            "advanced": 600,
            "expert": 900,
            "master": 1200,
            "legendary": 1800
        }.get(difficulty, 300)

async def test_smart_fallback():
    """Test the smart fallback system"""
    print("🧠 Testing Smart Fallback System...")
    
    # Initialize database
    await init_database()
    
    # Initialize smart fallback system
    smart_system = SmartFallbackTesting()
    
    # Test for each AI
    ai_types = ["imperium", "guardian", "conquest", "sandbox"]
    
    for ai_type in ai_types:
        print(f"\n{'='*60}")
        print(f"🧪 Testing {ai_type.upper()} with Smart Fallback")
        print(f"{'='*60}")
        
        try:
            # Generate smart test
            test = await smart_system.generate_smart_test(ai_type, "intermediate", "knowledge_verification")
            
            print(f"✅ Test generated for {ai_type}:")
            print(f"   Title: {test.get('title', 'N/A')}")
            print(f"   Category: {test.get('category', 'N/A')}")
            print(f"   Difficulty: {test.get('difficulty', 'N/A')}")
            print(f"   Source: {test.get('source', 'N/A')}")
            print(f"   Time Limit: {test.get('time_limit', 'N/A')} seconds")
            print(f"   Subjects Covered: {len(test.get('subjects_covered', []))}")
            print(f"   Patterns Covered: {len(test.get('patterns_covered', []))}")
            
            # Show sample content
            content = test.get('content', '')
            if content:
                print(f"   Content Preview: {content[:200]}...")
            
        except Exception as e:
            print(f"❌ Error testing {ai_type}: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 Smart Fallback Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_smart_fallback()) 