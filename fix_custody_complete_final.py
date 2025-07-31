#!/usr/bin/env python3
"""
Complete fix for all malformed try-except blocks in custody_protocol_service.py
"""

import re

def fix_custody_complete_final():
    """Fix all malformed try-except blocks in the file"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Remove orphaned try: pass blocks that don't have proper except blocks
    # Pattern: try: followed by pass and then code without except
    pattern1 = r'(\s+)try:\s*\n\s+pass\s*\n\s+except AttributeError as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+([^#\n]+)'
    
    replacement1 = r'\1try:\n\1    \2\n\1except AttributeError as e:\n\1    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n\1    # Continue with fallback behavior'
    
    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)
    
    # Fix 2: Remove orphaned try: pass blocks that appear before code
    # Pattern: try: pass followed by code without except
    pattern2 = r'(\s+)try:\s*\n\s+pass\s*\n\s+([^#\n]+)'
    
    replacement2 = r'\1try:\n\1    \2'
    
    content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)
    
    # Fix 3: Remove orphaned except blocks that don't have a try block before them
    # Pattern: except without a preceding try block
    pattern3 = r'(\s+)(?<!try:)\s*\n\s+except (AttributeError|Exception) as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+pass'
    
    replacement3 = r'\1try:\n\1    pass\n\1except \2 as e:\n\1    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n\1    # Continue with fallback behavior\n\1    pass'
    
    content = re.sub(pattern3, replacement3, content, flags=re.MULTILINE)
    
    # Fix 4: Remove nested except blocks
    # Pattern: except followed by another except at the same level
    pattern4 = r'(\s+)except (AttributeError|Exception) as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+except (AttributeError|Exception) as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior'
    
    replacement4 = r'\1except \2 as e:\n\1    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n\1    # Continue with fallback behavior'
    
    content = re.sub(pattern4, replacement4, content, flags=re.MULTILINE)
    
    # Fix 5: Remove orphaned else blocks that don't have a proper if/elif structure
    # Pattern: else: without a preceding if/elif
    pattern5 = r'(\s+)(?<!if:)(?<!elif:)\s*\n\s+else:\s*\n\s+([^#\n]+)'
    
    replacement5 = r'\1# Removed orphaned else block\n\1\2'
    
    content = re.sub(pattern5, replacement5, content, flags=re.MULTILINE)
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Applied complete fixes for all malformed try-except blocks")

if __name__ == "__main__":
    fix_custody_complete_final()