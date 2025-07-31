#!/usr/bin/env python3
"""
Comprehensive script to fix all syntax errors in custody_protocol_service.py
The file has malformed try-except blocks with multiple except statements.
"""

import re

def fix_custody_syntax():
    """Fix all malformed try-except blocks in custody_protocol_service.py"""
    
    file_path = "app/services/custody_protocol_service.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match malformed try-except blocks
    # This matches: try:\n                pass\n        except AttributeError as e:\n        except AttributeError as e:\n
    pattern = r'try:\s*\n\s*pass\s*\n\s*except AttributeError as e:\s*\n\s*logger\.warning.*?\n\s*# Continue with fallback behavior\s*\n\s*except AttributeError as e:\s*\n\s*logger\.warning.*?\n\s*# Continue with fallback behavior\s*\n'
    
    # Replace with properly structured try-except
    replacement = '''try:
                pass
            except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
'''
    
    # Apply the fix
    fixed_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"Fixed comprehensive syntax errors in {file_path}")

if __name__ == "__main__":
    fix_custody_syntax()