#!/usr/bin/env python3
"""
Comprehensive fix for all malformed try-except blocks in custody_protocol_service.py
"""

import re

def fix_custody_comprehensive_all():
    """Fix all malformed try-except blocks in the file"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: The orphaned try block around line 1449
    pattern1 = r'(\s+)# Extract score from response\s*\n\s+try:\s*\n\s+pass\s*\n\s+except AttributeError as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+try:\s*\n\s+import re\s*\n\s+score_match = re\.search\(r\'\\b\(\\d\{1,2\}\|100\)\\b\', evaluation\)\s*\n\s+if score_match:\s*\n\s+score = int\(score_match\.group\(1\)\)\s*\n\s+return max\(0, min\(100, score\)\)\s*\n\s+else:\s*\n\s+return 75\s*\n\s+except AttributeError as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+return 75\s*\n\s+except Exception as e:'
    
    replacement1 = r'\1# Extract score from response\n\1try:\n\1    import re\n\1    score_match = re.search(r\'\\b(\\d{1,2}|100)\\b\', evaluation)\n\1    if score_match:\n\1        score = int(score_match.group(1))\n\1        return max(0, min(100, score))\n\1    else:\n\1        return 75\n\1except AttributeError as e:\n\1    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n\1    # Continue with fallback behavior\n\1    return 75\n\1except Exception as e:'
    
    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)
    
    # Fix 2: The malformed try-except blocks around line 1612
    pattern2 = r'(\s+)except AttributeError as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+except Exception as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+except Exception as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+from smart_fallback_testing import SmartFallbackTesting'
    
    replacement2 = r'\1except AttributeError as e:\n\1    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n\1    # Continue with fallback behavior\n\1    from smart_fallback_testing import SmartFallbackTesting'
    
    content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)
    
    # Fix 3: Another malformed pattern around line 1642
    pattern3 = r'(\s+)try:\s*\n\s+pass\s*\n\s+except AttributeError as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+except AttributeError as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+except Exception as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior\s*\n\s+except Exception as e:\s*\n\s+logger\.warning\(f"⚠️ EnhancedTestGenerator method not available: \{e\}"\)\s*\n\s+# Continue with fallback behavior'
    
    replacement3 = r'\1try:\n\1    pass\n\1except AttributeError as e:\n\1    logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")\n\1    # Continue with fallback behavior'
    
    content = re.sub(pattern3, replacement3, content, flags=re.MULTILINE)
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Applied comprehensive fixes for all malformed try-except blocks")

if __name__ == "__main__":
    fix_custody_comprehensive_all()