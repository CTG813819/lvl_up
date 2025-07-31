#!/usr/bin/env python3
"""
Comprehensive fix for all malformed try-except blocks in custody_protocol_service.py
"""

import re

def fix_all_custody_blocks():
    """Fix all malformed try-except blocks in custody_protocol_service.py"""
    
    # Read the file
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
    
    print("Fixed all malformed try-except blocks in custody_protocol_service.py")

if __name__ == "__main__":
    fix_all_custody_blocks()