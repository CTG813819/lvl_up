#!/usr/bin/env python3
"""
Script to remove all malformed try-except blocks in custody_protocol_service.py
The file has malformed try-except blocks that are causing syntax errors.
"""

import re

def fix_custody_remove_blocks():
    """Remove all malformed try-except blocks in custody_protocol_service.py"""
    
    file_path = "app/services/custody_protocol_service.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match malformed try-except blocks
    # This matches: try:\n                pass\nexcept AttributeError as e:\n                logger.warning...\n            except Exception as e:\n                logger.warning...
    pattern = r'try:\s*\n\s*pass\s*\nexcept [^:]+ as e:\s*\n\s*logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s*# Continue with fallback behavior\s*\n\s*except Exception as e:\s*\n\s*logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s*# Continue with fallback behavior\s*\n'
    
    # Replace with just a pass statement
    content = re.sub(pattern, 'pass\n', content)
    
    # Also remove any remaining malformed try-except blocks
    pattern2 = r'try:\s*\n\s*pass\s*\nexcept [^:]+ as e:\s*\n\s*logger\.warning[^\n]*\n\s*# Continue with fallback behavior\s*\n\s*except Exception as e:\s*\n\s*logger\.warning[^\n]*\n\s*# Continue with fallback behavior\s*\n'
    content = re.sub(pattern2, 'pass\n', content)
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Removed all malformed try-except blocks in custody_protocol_service.py")

if __name__ == "__main__":
    fix_custody_remove_blocks()