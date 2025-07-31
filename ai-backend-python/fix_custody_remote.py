#!/usr/bin/env python3
"""
Fix for the specific syntax error on line 1452 in custody_protocol_service.py
"""

def fix_custody_remote():
    """Fix the specific syntax error on line 1452"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the specific problematic section around lines 1445-1460
    # This pattern matches the exact malformed structure that's causing the error
    old_pattern = '''        except AttributeError as e:
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
    
    new_pattern = '''        try:
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
    
    # Apply the fix
    content = content.replace(old_pattern, new_pattern)
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed syntax error on line 1452 in custody_protocol_service.py")

if __name__ == "__main__":
    fix_custody_remote()