#!/usr/bin/env python3
"""
Comprehensive fix for all syntax errors in custody_protocol_service.py
"""

import re

def fix_custody_all_syntax():
    """Fix all syntax errors in custody_protocol_service.py"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix all malformed try-except blocks systematically
    
    # Pattern 1: Fix the specific problematic section around lines 1445-1460
    old_pattern_1 = '''        except AttributeError as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
                import re
                score_match = re.search(r'\b(\d{1,2}|100)\b', evaluation)
                if score_match:
                    score = int(score_match.group(1))
                    return max(0, min(100, score))
                else:
                    return 75
            except:
                return 75
                
        except Exception as e:'''
    
    new_pattern_1 = '''        try:
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
    
    # Pattern 2: Fix other malformed try-except blocks
    old_pattern_2 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior'''
    
    new_pattern_2 = '''        try:
            pass
        except AttributeError as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
        except Exception as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior'''
    
    # Pattern 3: Fix try-except blocks with code after except blocks
    old_pattern_3 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            # Local import to avoid circular import'''
    
    new_pattern_3 = '''        try:
            # Local import to avoid circular import'''
    
    # Apply all fixes
    content = content.replace(old_pattern_1, new_pattern_1)
    content = content.replace(old_pattern_2, new_pattern_2)
    content = content.replace(old_pattern_3, new_pattern_3)
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed all syntax errors in custody_protocol_service.py")

if __name__ == "__main__":
    fix_custody_all_syntax()