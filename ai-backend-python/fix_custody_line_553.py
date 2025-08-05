#!/usr/bin/env python3
"""
Targeted fix for line 553 syntax error in custody_protocol_service.py
"""

def fix_custody_line_553():
    """Fix the specific syntax error on line 553"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the specific problematic section around lines 550-555
    old_pattern_553 = '''        except AttributeError as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            
        except Exception as e:'''
    
    new_pattern_553 = '''        except AttributeError as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
        except Exception as e:'''
    
    # Apply the fix
    content = content.replace(old_pattern_553, new_pattern_553)
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed syntax error on line 553 in custody_protocol_service.py")

if __name__ == "__main__":
    fix_custody_line_553()