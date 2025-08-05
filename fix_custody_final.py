#!/usr/bin/env python3
"""
<<<<<<< HEAD
Final comprehensive fix for custody_protocol_service.py indentation errors
"""

import re

def fix_custody_protocol_service():
    """Fix all malformed try-except blocks in custody_protocol_service.py"""
    
    # Read the file with UTF-8 encoding
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find all malformed try-except blocks
    # This pattern matches:
    # try:
    #         pass
    # except AttributeError as e:
    #         logger.warning(...)
    #         # Continue with fallback behavior
    #     except Exception as e:
    #         logger.warning(...)
    #         # Continue with fallback behavior
    #     actual_code_here
    
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
Final fix for custody_protocol_service.py indentation error
"""

def fix_custody_final():
    """Fix the specific indentation error on lines 1105-1106"""
    file_path = "ai-backend-python/app/services/custody_protocol_service.py"
    
    print(f"🔧 Final fix for {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check the specific lines around 1105-1106
    print("Checking lines around 1105-1106...")
    for i in range(max(0, 1100), min(len(lines), 1110)):
        print(f"Line {i+1}: {repr(lines[i])}")
    
    # Fix the specific issue
    fixed_lines = []
    for i, line in enumerate(lines):
        # Line 1105: Function definition - ensure it has colon and proper indentation
        if i == 1104:  # 0-indexed, so line 1105
            if 'async def _persist_custody_metrics_to_database' in line:
                if not line.strip().endswith(':'):
                    # Add colon if missing
                    fixed_line = line.rstrip() + ':\n'
                    fixed_lines.append(fixed_line)
                    print(f"Fixed line {i+1}: Added colon")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        # Line 1106: Docstring - ensure proper indentation
        elif i == 1105:  # 0-indexed, so line 1106
            if '"""Persist custody metrics to the database"""' in line:
                # Ensure proper indentation (8 spaces)
                if not line.startswith('        """'):
                    fixed_line = '        """Persist custody metrics to the database"""\n'
                    fixed_lines.append(fixed_line)
                    print(f"Fixed line {i+1}: Fixed docstring indentation")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ Fixed custody protocol service")
    
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
    fix_custody_final() 
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
