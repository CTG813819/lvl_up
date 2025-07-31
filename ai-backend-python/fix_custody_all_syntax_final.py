#!/usr/bin/env python3
"""
Comprehensive fix for all malformed try-except blocks in custody_protocol_service.py
"""

import re

def fix_custody_all_syntax_final():
    """Fix all malformed try-except blocks in the file"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Remove nested except blocks that are incorrectly indented
    # Pattern: except AttributeError/Exception followed by another except at the same level
    pattern1 = r'(\s+)except (AttributeError|Exception) as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+except (AttributeError|Exception) as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior'
    
    replacement1 = r'\1except \2 as e:\n\1    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n\1    # Continue with fallback behavior'
    
    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)
    
    # Fix 2: Remove orphaned except blocks that don't have a try block before them
    # Pattern: except ImportError/Exception without a preceding try block
    pattern2 = r'(\s+)(?<!try:)\s*\n\s+except (ImportError|Exception) as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+pass'
    
    replacement2 = r'\1try:\n\1    pass\n\1except \2 as e:\n\1    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n\1    # Continue with fallback behavior\n\1    pass'
    
    content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)
    
    # Fix 3: Fix orphaned except blocks that appear after code without a try block
    # Pattern: code followed by except without a try block
    pattern3 = r'(\s+)([^#\n]+)\s*\n\s+except (ImportError|Exception) as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+pass'
    
    replacement3 = r'\1try:\n\1    \2\n\1except \3 as e:\n\1    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n\1    # Continue with fallback behavior\n\1    pass'
    
    content = re.sub(pattern3, replacement3, content, flags=re.MULTILINE)
    
    # Fix 4: Remove duplicate except blocks
    # Pattern: except Exception as e: followed by another except Exception as e:
    pattern4 = r'(\s+)except Exception as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+except Exception as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior'
    
    replacement4 = r'\1except Exception as e:\n\1    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n\1    # Continue with fallback behavior'
    
    content = re.sub(pattern4, replacement4, content, flags=re.MULTILINE)
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Applied comprehensive fixes for all malformed try-except blocks")

if __name__ == "__main__":
    fix_custody_all_syntax_final()