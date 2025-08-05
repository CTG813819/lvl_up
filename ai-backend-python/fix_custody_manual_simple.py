#!/usr/bin/env python3
"""
Simple manual fix for the orphaned try block on line 1449
"""

def fix_custody_manual_simple():
    """Fix the orphaned try block on line 1449"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the problematic section
    old_pattern = '''                pass
            except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
        try:

            import re

            score_match = re.search(r\'\b(\d{1,2}|100)\b\', evaluation)

            if score_match:

                score = int(score_match.group(1))

                return max(0, min(100, score))

            else:

                return 75

        except AttributeError as e:

            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")

            # Continue with fallback behavior

            return 75

        except Exception as e:'''
    
    new_pattern = '''        try:
            import re
            score_match = re.search(r'\b(\d{1,2}|100)\b', evaluation)
            if score_match:
                score = int(score_match.group(1))
                return max(0, min(100, score))
            else:
                return 75
        except AttributeError as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
            return 75
        except Exception as e:'''
    
    # Apply the fix
    content = content.replace(old_pattern, new_pattern)
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed orphaned try block on line 1449")

if __name__ == "__main__":
    fix_custody_manual_simple()