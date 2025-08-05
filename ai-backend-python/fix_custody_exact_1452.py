#!/usr/bin/env python3
"""
Exact fix for the syntax error on line 1452 in custody_protocol_service.py
"""

def fix_custody_exact_1452():
    """Fix the exact malformed structure around line 1452"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The exact problematic pattern from the file
    old_pattern = '''            # Extract score from response
            try:
                pass
            except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
        except AttributeError as e:
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
    
    # The corrected pattern
    new_pattern = '''            # Extract score from response
            try:
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
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("Fixed syntax error on line 1452 in custody_protocol_service.py")
    else:
        print("Pattern not found. Checking for alternative pattern...")
        
        # Alternative pattern with different indentation
        alt_old_pattern = '''            try:
                pass
            except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
        except AttributeError as e:
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
        
        if alt_old_pattern in content:
            content = content.replace(alt_old_pattern, new_pattern)
            print("Fixed syntax error on line 1452 using alternative pattern")
        else:
            print("Neither pattern found. Manual inspection needed.")
            return
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_custody_exact_1452()