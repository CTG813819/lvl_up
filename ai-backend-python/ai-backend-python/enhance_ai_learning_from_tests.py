#!/usr/bin/env python3
"""
Enhance AI learning to learn from failed tests and generate new proposals
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Add the backend path to sys.path
sys.path.append('ai-backend-python')

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.sql_models import Proposal, Learning
from app.services.ai_learning_service import AILearningService
from app.services.testing_service import TestingService

async def enhance_proposal_router_with_learning():
    """Add learning from failed tests to the proposal router"""
    print("🔧 Enhancing proposal router with AI learning from failed tests...")
    
    # Read the current proposals.py file
    with open('ai-backend-python/app/routers/proposals.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add import for AI learning service at the top
    if 'from app.services.ai_learning_service import AILearningService' not in content:
        # Find the imports section and add the new import
        import_section = """from app.services.ml_service import MLService
from app.services.ai_learning_service import AILearningService
from app.services.ai_learning_service import AILearningService"""
        
        content = content.replace(
            'from app.services.ml_service import MLService',
            'from app.services.ml_service import MLService\nfrom app.services.ai_learning_service import AILearningService'
        )
    
    # Add AI learning service initialization
    if 'ai_learning_service = AILearningService()' not in content:
        content = content.replace(
            'ml_service = MLService()',
            'ml_service = MLService()\nai_learning_service = AILearningService()'
        )
    
    # Add learning from failed tests in the testing section
    test_failed_section = """            elif overall_result.value == "failed":
                new_proposal.status = "test-failed"
                new_proposal.test_status = "failed"
                new_proposal.test_output = summary
                logger.info("Proposal failed automatic testing", proposal_id=str(new_proposal.id))
                
                # Learn from failed test and generate new proposal
                try:
                    await ai_learning_service.learn_from_proposal(
                        str(new_proposal.id), 
                        "test-failed", 
                        f"Test failed: {summary}"
                    )
                    
                    # Generate a new improved proposal based on learning
                    await generate_improved_proposal(new_proposal, summary, db)
                    
                except Exception as e:
                    logger.error("Error learning from failed test", 
                                proposal_id=str(new_proposal.id),
                                error=str(e))"""
    
    # Replace the existing test-failed section
    old_test_failed = """            elif overall_result.value == "failed":
                new_proposal.status = "test-failed"
                new_proposal.test_status = "failed"
                new_proposal.test_output = summary
                logger.info("Proposal failed automatic testing", proposal_id=str(new_proposal.id))"""
    
    content = content.replace(old_test_failed, test_failed_section)
    
    # Add the generate_improved_proposal function
    improved_proposal_function = """
async def generate_improved_proposal(failed_proposal: Proposal, test_summary: str, db: AsyncSession):
    \"\"\"Generate an improved proposal based on failed test results\"\"\"
    try:
        from app.services.ai_agent_service import AIAgentService
        
        # Analyze the failure and generate improvements
        ai_agent_service = AIAgentService()
        
        # Create improvement context
        improvement_context = f\"\"\"
Original proposal failed testing:
- AI Type: {failed_proposal.ai_type}
- File: {failed_proposal.file_path}
- Test Summary: {test_summary}
- Original Code: {failed_proposal.code_after}

Please generate an improved version that addresses the test failures.
\"\"\"
        
        # Generate improved proposal based on AI type
        if failed_proposal.ai_type.lower() == "guardian":
            improved_result = await ai_agent_service.run_guardian_agent(
                context=improvement_context,
                focus="fix_test_failures"
            )
        elif failed_proposal.ai_type.lower() == "imperium":
            improved_result = await ai_agent_service.run_imperium_agent(
                context=improvement_context,
                focus="fix_test_failures"
            )
        elif failed_proposal.ai_type.lower() == "sandbox":
            improved_result = await ai_agent_service.run_sandbox_agent(
                context=improvement_context,
                focus="fix_test_failures"
            )
        elif failed_proposal.ai_type.lower() == "conquest":
            improved_result = await ai_agent_service.run_conquest_agent(
                context=improvement_context,
                focus="fix_test_failures"
            )
        else:
            logger.warning(f"Unknown AI type for improvement: {failed_proposal.ai_type}")
            return
        
        # Create new improved proposal
        if improved_result and improved_result.get("code_after"):
            new_proposal = Proposal(
                ai_type=failed_proposal.ai_type,
                file_path=failed_proposal.file_path,
                code_before=failed_proposal.code_before,
                code_after=improved_result["code_after"],
                status="pending",
                result=None,
                user_feedback=None,
                test_status=None,
                test_output=None,
                code_hash=improved_result.get("code_hash", ""),
                semantic_hash=improved_result.get("semantic_hash", ""),
                diff_score=improved_result.get("diff_score", 0.0),
                duplicate_of=None,
                ai_reasoning=f"Improved version based on test failure: {test_summary}",
                learning_context=f"Generated from failed test: {str(failed_proposal.id)}",
                mistake_pattern="test_failure",
                improvement_type="test_fix",
                confidence=improved_result.get("confidence", 0.7),
                user_feedback_reason=None,
                ai_learning_applied=True,
                previous_mistakes_avoided=True
            )
            
            db.add(new_proposal)
            await db.commit()
            await db.refresh(new_proposal)
            
            logger.info("Generated improved proposal from failed test", 
                       original_id=str(failed_proposal.id),
                       new_id=str(new_proposal.id))
        
    except Exception as e:
        logger.error("Error generating improved proposal", 
                    original_id=str(failed_proposal.id),
                    error=str(e))"""
    
    # Add the function before the router definitions
    content = content.replace(
        'router = APIRouter()',
        'router = APIRouter()\n\n' + improved_proposal_function
    )
    
    # Write the enhanced file
    with open('ai-backend-python/app/routers/proposals.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Enhanced proposal router with AI learning from failed tests")

async def enhance_ai_learning_service():
    """Enhance the AI learning service to better handle test failures"""
    print("🔧 Enhancing AI learning service...")
    
    # Read the current ai_learning_service.py file
    with open('ai-backend-python/app/services/ai_learning_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add enhanced learning from test failures
    enhanced_learning_method = """
    async def learn_from_test_failure(self, proposal_id: str, test_summary: str, ai_type: str):
        \"\"\"Enhanced learning from test failures\"\"\"
        try:
            from sqlalchemy import select
            from ..models.sql_models import Proposal, Learning
            import uuid
            
            session = get_session()
            try:
                # Get proposal
                stmt = select(Proposal).where(Proposal.id == uuid.UUID(proposal_id))
                result = await session.execute(stmt)
                proposal_data = result.scalar_one_or_none()
                
                if not proposal_data:
                    logger.warning("Proposal not found for test failure learning", proposal_id=proposal_id)
                    return
                
                # Analyze the test failure pattern
                failure_pattern = self._analyze_test_failure_pattern(test_summary)
                
                # Store enhanced learning data
                learning_entry = Learning(
                    ai_type=ai_type,
                    learning_type="test_failure_analysis",
                    pattern=failure_pattern,
                    context=test_summary,
                    feedback=f"Test failure: {test_summary}",
                    confidence=0.8,  # High confidence for test failures
                    created_at=datetime.utcnow()
                )
                
                session.add(learning_entry)
                await session.commit()
                
                # Generate improvement suggestions
                improvement_suggestions = await self._generate_test_failure_improvements(
                    ai_type, test_summary, proposal_data
                )
                
                logger.info("Enhanced learning from test failure completed", 
                           proposal_id=proposal_id, 
                           failure_pattern=failure_pattern,
                           suggestions_count=len(improvement_suggestions))
                
                return improvement_suggestions
                
            except Exception as e:
                logger.error("Error in test failure learning", error=str(e), proposal_id=proposal_id)
            finally:
                await session.close()
                
        except Exception as e:
            logger.error("Error learning from test failure", error=str(e), proposal_id=proposal_id)
    
    def _analyze_test_failure_pattern(self, test_summary: str) -> str:
        \"\"\"Analyze test failure patterns\"\"\"
        test_summary_lower = test_summary.lower()
        
        if "syntax error" in test_summary_lower:
            return "syntax_error"
        elif "lint" in test_summary_lower:
            return "code_style_violation"
        elif "security" in test_summary_lower:
            return "security_vulnerability"
        elif "performance" in test_summary_lower:
            return "performance_issue"
        elif "timeout" in test_summary_lower:
            return "execution_timeout"
        else:
            return "general_test_failure"
    
    async def _generate_test_failure_improvements(self, ai_type: str, test_summary: str, proposal_data) -> List[str]:
        \"\"\"Generate improvement suggestions based on test failure\"\"\"
        suggestions = []
        
        # Analyze failure type and generate specific suggestions
        failure_pattern = self._analyze_test_failure_pattern(test_summary)
        
        if failure_pattern == "syntax_error":
            suggestions.append("Fix syntax errors in the code")
            suggestions.append("Ensure proper indentation and brackets")
        elif failure_pattern == "code_style_violation":
            suggestions.append("Follow coding style guidelines")
            suggestions.append("Use proper naming conventions")
        elif failure_pattern == "security_vulnerability":
            suggestions.append("Remove potential security vulnerabilities")
            suggestions.append("Use secure coding practices")
        elif failure_pattern == "performance_issue":
            suggestions.append("Optimize code for better performance")
            suggestions.append("Reduce computational complexity")
        elif failure_pattern == "execution_timeout":
            suggestions.append("Optimize for faster execution")
            suggestions.append("Reduce resource usage")
        
        # Add AI-specific suggestions
        if ai_type.lower() == "guardian":
            suggestions.append("Focus on security and code quality")
        elif ai_type.lower() == "imperium":
            suggestions.append("Ensure scalability and maintainability")
        elif ai_type.lower() == "sandbox":
            suggestions.append("Maintain experimental nature while fixing issues")
        elif ai_type.lower() == "conquest":
            suggestions.append("Ensure mobile app compatibility and performance")
        
        return suggestions"""
    
    # Add the enhanced methods before the existing learn_from_proposal method
    content = content.replace(
        'async def learn_from_proposal(self, proposal_id: str, status: str, feedback_reason: str = None):',
        enhanced_learning_method + '\n\n    async def learn_from_proposal(self, proposal_id: str, status: str, feedback_reason: str = None):'
    )
    
    # Write the enhanced file
    with open('ai-backend-python/app/services/ai_learning_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Enhanced AI learning service with test failure analysis")

async def test_enhanced_learning():
    """Test the enhanced learning system"""
    print("🧪 Testing enhanced learning system...")
    
    # Create database connection
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get a few test-failed proposals
        query = select(Proposal).where(Proposal.status == "test-failed").limit(3)
        result = await session.execute(query)
        failed_proposals = result.scalars().all()
        
        ai_learning_service = AILearningService()
        
        for proposal in failed_proposals:
            print(f"\n🔍 Testing learning from failed proposal: {str(proposal.id)[:8]}...")
            
            # Test enhanced learning
            try:
                improvements = await ai_learning_service.learn_from_test_failure(
                    str(proposal.id),
                    proposal.test_output or "Unknown test failure",
                    proposal.ai_type
                )
                
                print(f"   ✅ Learning completed")
                print(f"   📝 Improvement suggestions: {len(improvements)}")
                for suggestion in improvements:
                    print(f"      - {suggestion}")
                
            except Exception as e:
                print(f"   ❌ Learning failed: {str(e)}")

async def main():
    """Main function"""
    print("🚀 Enhancing AI Learning from Failed Tests")
    print("=" * 50)
    
    # Enhance the proposal router
    await enhance_proposal_router_with_learning()
    
    # Enhance the AI learning service
    await enhance_ai_learning_service()
    
    # Test the enhanced system
    await test_enhanced_learning()
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print("   ✅ Enhanced proposal router with learning from failed tests")
    print("   ✅ Enhanced AI learning service with test failure analysis")
    print("   ✅ Added automatic generation of improved proposals")
    print("   ✅ Added pattern analysis for different types of test failures")
    print("\n💡 Now the AI will:")
    print("   - Learn from failed tests automatically")
    print("   - Generate improved proposals based on test failures")
    print("   - Analyze failure patterns for better learning")
    print("   - Provide specific improvement suggestions")

if __name__ == "__main__":
    asyncio.run(main()) 