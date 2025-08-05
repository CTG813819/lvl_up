#!/usr/bin/env python3
"""
<<<<<<< HEAD
Complete fix for custody_protocol_service.py indentation errors
"""

import re

def fix_custody_protocol_service():
    """Fix all malformed try-except blocks in custody_protocol_service.py"""
    
    # Read the file with UTF-8 encoding
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find malformed try-except blocks where code is after except blocks
    # This pattern matches:
    # try:
    #         pass
    # except AttributeError as e:
    #         logger.warning(...)
    #         # Continue with fallback behavior
    #     except Exception as e:
    #         logger.warning(...)
    #         # Continue with fallback behavior
    #     actual_code_here (this should be inside the try block)
    
    # Find all occurrences of this pattern
    pattern = r'try:\s*\n\s*pass\s*\nexcept AttributeError as e:\s*\n\s*logger\.warning\([^)]+\)\s*\n\s*# Continue with fallback behavior\s*\nexcept Exception as e:\s*\n\s*logger\.warning\([^)]+\)\s*\n\s*# Continue with fallback behavior\s*\n\s*([^}]+?)(?=\n\s*except Exception as e:|$)'
    
    def replace_malformed_block(match):
        actual_code = match.group(1).strip()
        if actual_code:
            # Move the actual code into the try block
            return f'''try:
        {actual_code}
except AttributeError as e:
        logger.warning(f"⚠️ EnhancedTestGenerator method not available: {{e}}")
        # Continue with fallback behavior
except Exception as e:
        logger.warning(f"⚠️ EnhancedTestGenerator method not available: {{e}}")
        # Continue with fallback behavior'''
        else:
            # If no actual code, just fix the structure
            return '''try:
        pass
except AttributeError as e:
        logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
        # Continue with fallback behavior
except Exception as e:
        logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
        # Continue with fallback behavior'''
    
    # Apply the fix
    fixed_content = re.sub(pattern, replace_malformed_block, content, flags=re.MULTILINE | re.DOTALL)
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("Fixed malformed try-except blocks in custody_protocol_service.py")

if __name__ == "__main__":
    fix_custody_protocol_service()
=======
Complete fix for custody_protocol_service.py
"""

def fix_custody_complete():
    """Complete fix for custody protocol service"""
    file_path = "ai-backend-python/app/services/custody_protocol_service.py"
    
    print(f"🔧 Complete fix for {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic method and replace it completely
    method_start = content.find("async def _persist_custody_metrics_to_database")
    if method_start == -1:
        print("❌ Could not find _persist_custody_metrics_to_database method")
        return False
    
    # Find the end of the method
    method_end = content.find("async def _load_custody_metrics_from_database", method_start)
    if method_end == -1:
        method_end = content.find("class ", method_start)
    
    if method_end == -1:
        method_end = len(content)
    
    # Create the correct method with proper indentation
    correct_method = '''    async def _persist_custody_metrics_to_database(self, ai_type: str, metrics: Dict):
        """Persist custody metrics to the database"""
        try:
            session = get_session()
            async with session as s:
                from ..models.sql_models import AgentMetrics
                from sqlalchemy import select
                
                # Get or create agent metrics record
                result = await s.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == ai_type)
                )
                agent_metrics = result.scalar_one_or_none()
                
                if not agent_metrics:
                    # Create new agent metrics record
                    agent_metrics = AgentMetrics(
                        agent_id=f"{ai_type}_agent",
                        agent_type=ai_type,
                        learning_score=0.0,
                        success_rate=0.0,
                        failure_rate=0.0,
                        total_learning_cycles=0,
                        xp=metrics["custody_xp"],
                        level=metrics["custody_level"],
                        prestige=0,
                        status="active",
                        is_active=True,
                        priority="medium",
                    )
                    s.add(agent_metrics)
                    # Set custody test fields after adding
                    setattr(agent_metrics, 'total_tests_given', metrics["total_tests_given"])
                    setattr(agent_metrics, 'total_tests_passed', metrics["total_tests_passed"])
                    setattr(agent_metrics, 'total_tests_failed', metrics["total_tests_failed"])
                    setattr(agent_metrics, 'custody_level', metrics["custody_level"])
                    setattr(agent_metrics, 'custody_xp', metrics["custody_xp"])
                    setattr(agent_metrics, 'consecutive_successes', metrics["consecutive_successes"])
                    setattr(agent_metrics, 'consecutive_failures', metrics["consecutive_failures"])
                    setattr(agent_metrics, 'last_test_date', datetime.fromisoformat(metrics["last_test_date"].replace('Z', '+00:00')) if metrics["last_test_date"] else None)
                    setattr(agent_metrics, 'test_history', metrics["test_history"])
                else:
                    # Update existing record with custody metrics
                    setattr(agent_metrics, 'xp', metrics["custody_xp"])
                    setattr(agent_metrics, 'level', metrics["custody_level"])
                    # Custody test fields
                    setattr(agent_metrics, 'total_tests_given', metrics["total_tests_given"])
                    setattr(agent_metrics, 'total_tests_passed', metrics["total_tests_passed"])
                    setattr(agent_metrics, 'total_tests_failed', metrics["total_tests_failed"])
                    setattr(agent_metrics, 'custody_level', metrics["custody_level"])
                    setattr(agent_metrics, 'custody_xp', metrics["custody_xp"])
                    setattr(agent_metrics, 'consecutive_successes', metrics["consecutive_successes"])
                    setattr(agent_metrics, 'consecutive_failures', metrics["consecutive_failures"])
                    setattr(agent_metrics, 'last_test_date', datetime.fromisoformat(metrics["last_test_date"].replace('Z', '+00:00')) if metrics["last_test_date"] else None)
                    setattr(agent_metrics, 'test_history', metrics["test_history"])
                
                await s.commit()
                logger.info(f"Persisted custody metrics for {ai_type}: Tests={metrics['total_tests_given']}, Passed={metrics['total_tests_passed']}, Failed={metrics['total_tests_failed']}, XP={metrics['custody_xp']}, Level={metrics['custody_level']}")
                
        except Exception as e:
            logger.error(f"Error persisting custody metrics to database: {str(e)}")
    
    '''
    
    # Replace the method
    new_content = content[:method_start] + correct_method + content[method_end:]
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Fixed custody protocol service method")
    
    # Test the syntax
    try:
        import ast
        with open(file_path, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        print("✅ Syntax check passed!")
    except SyntaxError as e:
        print(f"❌ Syntax check failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_custody_complete() 
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
