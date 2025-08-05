#!/usr/bin/env python3
"""
Final direct fix for the syntax error around lines 1443-1449
"""

def fix_custody_final_direct():
    """Fix the exact problematic structure around lines 1443-1449"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The exact problematic pattern from the current file
    old_pattern = '''            # Extract score from response
            try:
                pass
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
    
    # The corrected pattern
    new_pattern = '''            # Extract score from response
            try:
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
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("Fixed exact syntax error around lines 1443-1449")
    else:
        print("Pattern not found. Manual inspection needed.")
        return
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_custody_final_direct()