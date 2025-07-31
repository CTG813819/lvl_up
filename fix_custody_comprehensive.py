#!/usr/bin/env python3
"""
Comprehensive fix for custody_protocol_service.py
"""

def fix_custody_comprehensive():
    """Comprehensive fix for custody protocol service"""
    file_path = "ai-backend-python/app/services/custody_protocol_service.py"
    
    print(f"🔧 Comprehensive fix for {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic section and replace it with a correct version
    # Look for the _persist_custody_metrics_to_database method
    method_start = content.find("async def _persist_custody_metrics_to_database")
    if method_start == -1:
        print("❌ Could not find _persist_custody_metrics_to_database method")
        return False
    
    # Find the end of the method (next method or end of class)
    method_end = content.find("async def _load_custody_metrics_from_database", method_start)
    if method_end == -1:
        method_end = content.find("class ", method_start)
    
    if method_end == -1:
        method_end = len(content)
    
    # Extract the problematic method
    old_method = content[method_start:method_end]
    print(f"Found method from position {method_start} to {method_end}")
    
    # Create the correct method
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
    fix_custody_comprehensive() 