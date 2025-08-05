#!/usr/bin/env python3
"""
Fix Custody Protocol Indentation Error
======================================

This script fixes the indentation error in custody_protocol_service.py that's
preventing the backend from starting.
"""

import re

def fix_custody_protocol_service():
    """Fix the indentation error in custody_protocol_service.py"""
    try:
        print("🔧 Fixing custody protocol service indentation...")
        
        service_path = "app/services/custody_protocol_service.py"
        with open(service_path, 'r') as f:
            content = f.read()
        
        # Find the problematic section - there are duplicate method definitions
        # Look for the _persist_custody_metrics_to_database method
        method_pattern = r'async def _persist_custody_metrics_to_database\(self, ai_type: str, metrics: Dict\):'
        matches = list(re.finditer(method_pattern, content))
        
        if len(matches) > 1:
            print(f"Found {len(matches)} duplicate method definitions")
            
            # Find the first occurrence and replace it with the correct implementation
            first_match = matches[0]
            second_match = matches[1]
            
            # Get the content before the first method
            before_first = content[:first_match.start()]
            
            # Get the content after the second method (find the end of the second method)
            after_second_start = second_match.start()
            
            # Find the end of the second method by looking for the next method or class
            next_method_match = re.search(r'\n    async def ', content[after_second_start:])
            if next_method_match:
                after_second_end = after_second_start + next_method_match.start()
            else:
                # If no next method, go to end of file
                after_second_end = len(content)
            
            after_second = content[after_second_end:]
            
            # Create the correct method implementation
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
                        # Custody test fields
                        total_tests_given=metrics["total_tests_given"],
                        total_tests_passed=metrics["total_tests_passed"],
                        total_tests_failed=metrics["total_tests_failed"],
                        custody_level=metrics["custody_level"],
                        custody_xp=metrics["custody_xp"],
                        consecutive_successes=metrics["consecutive_successes"],
                        consecutive_failures=metrics["consecutive_failures"],
                        last_test_date=datetime.fromisoformat(metrics["last_test_date"].replace('Z', '+00:00')) if metrics["last_test_date"] else None,
                        test_history=metrics["test_history"],
                        current_difficulty=metrics.get("current_difficulty", "basic")
                    )
                    s.add(agent_metrics)
                else:
                    # Update existing record with custody metrics
                    agent_metrics.xp = metrics["custody_xp"]
                    agent_metrics.level = metrics["custody_level"]
                    # Custody test fields
                    agent_metrics.total_tests_given = metrics["total_tests_given"]
                    agent_metrics.total_tests_passed = metrics["total_tests_passed"]
                    agent_metrics.total_tests_failed = metrics["total_tests_failed"]
                    agent_metrics.custody_level = metrics["custody_level"]
                    agent_metrics.custody_xp = metrics["custody_xp"]
                    agent_metrics.consecutive_successes = metrics["consecutive_successes"]
                    agent_metrics.consecutive_failures = metrics["consecutive_failures"]
                    agent_metrics.last_test_date = datetime.fromisoformat(metrics["last_test_date"].replace('Z', '+00:00')) if metrics["last_test_date"] else None
                    agent_metrics.test_history = metrics["test_history"]
                    agent_metrics.current_difficulty = metrics.get("current_difficulty", "basic")
                
                await s.commit()
                logger.info(f"Persisted custody metrics for {ai_type}: Tests={metrics['total_tests_given']}, Passed={metrics['total_tests_passed']}, Failed={metrics['total_tests_failed']}, XP={metrics['custody_xp']}, Level={metrics['custody_level']}")
                
        except Exception as e:
            logger.error(f"Error persisting custody metrics to database: {str(e)}")
'''
            
            # Reconstruct the file content
            new_content = before_first + correct_method + after_second
            
            # Write the fixed file
            with open(service_path, 'w') as f:
                f.write(new_content)
            
            print(f"✅ Fixed custody protocol service indentation in {service_path}")
            return True
        else:
            print("No duplicate method definitions found")
            return True
        
    except Exception as e:
        print(f"❌ Error fixing custody protocol service: {str(e)}")
        return False

def test_syntax():
    """Test that the file has correct syntax"""
    try:
        print("🧪 Testing syntax...")
        
        import subprocess
        result = subprocess.run(
            ["python", "-m", "py_compile", "app/services/custody_protocol_service.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Syntax check passed")
            return True
        else:
            print(f"❌ Syntax check failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing syntax: {str(e)}")
        return False

def main():
    """Main function to fix the indentation error"""
    
    print("🚀 Starting custody protocol indentation fix...")
    
    # Fix the service file
    if not fix_custody_protocol_service():
        print("❌ Failed to fix custody protocol service")
        return
    
    # Test syntax
    if not test_syntax():
        print("❌ Syntax test failed")
        return
    
    print("✅ Custody protocol indentation fix completed successfully!")
    print("🎯 The backend should now start without errors!")

if __name__ == "__main__":
    main() 