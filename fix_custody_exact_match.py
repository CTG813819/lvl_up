#!/usr/bin/env python3
"""
Exact match fix for the syntax error around line 1449
"""

def fix_custody_exact_match():
    """Fix the exact structure around line 1449"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The exact problematic pattern from the current file
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
    
    # The corrected pattern
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
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("Fixed exact syntax error around line 1449")
    else:
        print("Pattern not found. Trying line-by-line approach...")
        
        # Line-by-line approach
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for the problematic pattern
            if 'try:' in line and i > 0 and 'except AttributeError as e:' in lines[i-1]:
                # Found the problematic try block, replace it
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Remove the previous except block and replace with proper try-except
                fixed_lines.pop()  # Remove the previous except line
                
                fixed_lines.append(f'{indent_str}try:')
                fixed_lines.append(f'{indent_str}    import re')
                fixed_lines.append(f'{indent_str}    score_match = re.search(r\'\\b(\\d{{1,2}}|100)\\b\', evaluation)')
                fixed_lines.append(f'{indent_str}    if score_match:')
                fixed_lines.append(f'{indent_str}        score = int(score_match.group(1))')
                fixed_lines.append(f'{indent_str}        return max(0, min(100, score))')
                fixed_lines.append(f'{indent_str}    else:')
                fixed_lines.append(f'{indent_str}        return 75')
                fixed_lines.append(f'{indent_str}except AttributeError as e:')
                fixed_lines.append(f'{indent_str}    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {{e}}")')
                fixed_lines.append(f'{indent_str}    # Continue with fallback behavior')
                fixed_lines.append(f'{indent_str}    return 75')
                fixed_lines.append(f'{indent_str}except Exception as e:')
                
                # Skip the problematic lines
                i += 15  # Skip the malformed block
                continue
            else:
                fixed_lines.append(line)
            
            i += 1
        
        # Write the fixed content back to the file
        with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print("Fixed syntax error using line-by-line approach")
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_custody_exact_match()