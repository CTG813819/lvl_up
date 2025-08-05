#!/usr/bin/env python3
"""
Comprehensive fix for custody_protocol_service.py indentation errors
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
    
    pattern = r'try:\s*\n\s+pass\s*\nexcept AttributeError as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\nexcept Exception as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+(.*?)(?=\n\s+except Exception as e:|$)'
    
    def fix_try_except_block(match):
        actual_code = match.group(1)
        # Remove the extra indentation from the actual code
        actual_code = re.sub(r'^\s+', '', actual_code, flags=re.MULTILINE)
        
        # Create the fixed try-except block
        fixed_block = f'''try:
    {actual_code}
except AttributeError as e:
    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {{e}}")
    # Continue with fallback behavior
except Exception as e:
    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {{e}}")
    # Continue with fallback behavior'''
        
        return fixed_block
    
    # Apply the fix multiple times to catch all occurrences
    old_content = None
    while old_content != content:
        old_content = content
        content = re.sub(pattern, fix_try_except_block, content, flags=re.DOTALL)
    
    # Write the fixed content back with UTF-8 encoding
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed all custody protocol service indentation errors")

if __name__ == "__main__":
    fix_custody_protocol_service()