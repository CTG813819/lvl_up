#!/usr/bin/env python3
"""
Regex-based fix for the syntax error on line 1452 in custody_protocol_service.py
"""

import re

def fix_custody_regex_final():
    """Fix the syntax error using regex to handle variations"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Use regex to find and fix the malformed try-except blocks
    # This pattern matches the problematic structure with flexible spacing
    pattern = r'(\s+)except AttributeError as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+except Exception as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+except Exception as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+import re\s*\n\s+score_match = re\.search\(r\'\\b\(\\d\{1,2\}\|100\)\\b\', evaluation\)\s*\n\s+if score_match:\s*\n\s+score = int\(score_match\.group\(1\)\)\s*\n\s+return max\(0, min\(100, score\)\)\s*\n\s+else:\s*\n\s+return 75\s*\n\s+except:\s*\n\s+return 75\s*\n\s+\s*\n\s+except Exception as e:'
    
    # The replacement pattern
    replacement = r'\1try:\n\1    import re\n\1    score_match = re.search(r\'\\b(\\d{1,2}|100)\\b\', evaluation)\n\1    if score_match:\n\1        score = int(score_match.group(1))\n\1        return max(0, min(100, score))\n\1    else:\n\1        return 75\n\1except AttributeError as e:\n\1    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n\1    # Continue with fallback behavior\n\1    return 75\n\1except Exception as e:'
    
    # Apply the regex replacement
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if new_content != content:
        # Write the fixed content back to the file
        with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Fixed syntax error using regex pattern")
    else:
        print("Pattern not found. Trying alternative approach...")
        
        # Alternative approach: find the specific lines and fix them manually
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for the problematic pattern
            if 'except AttributeError as e:' in line and i + 1 < len(lines):
                # Check if the next few lines match our problematic pattern
                if (i + 2 < len(lines) and 'logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")' in lines[i + 1] and
                    i + 3 < len(lines) and '# Continue with fallback behavior' in lines[i + 2] and
                    i + 4 < len(lines) and 'except Exception as e:' in lines[i + 3]):
                    
                    # Found the problematic pattern, replace it
                    indent = len(line) - len(line.lstrip())
                    indent_str = ' ' * indent
                    
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
            else:
                fixed_lines.append(line)
            
            i += 1
        
        # Write the fixed content back to the file
        with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print("Fixed syntax error using line-by-line approach")

if __name__ == "__main__":
    fix_custody_regex_final()