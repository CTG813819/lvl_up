#!/usr/bin/env python3
"""
Fix for the specific malformed structure around line 1612
"""

def fix_custody_line_1612():
    """Fix the specific malformed structure around line 1612"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The exact problematic pattern from the current file
    old_pattern = '''        except AttributeError as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
        except Exception as e:'''
    
    # The corrected pattern
    new_pattern = '''        except AttributeError as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
        except Exception as e:'''
    
    # Apply the fix
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("Fixed malformed structure around line 1612")
    else:
        print("Pattern not found. Trying alternative approach...")
        
        # Alternative approach: find the specific lines and fix them manually
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Look for the problematic pattern: except AttributeError followed by nested except
            if ('except AttributeError as e:' in line and 
                i + 2 < len(lines) and 'except Exception as e:' in lines[i + 2]):
                
                # Found the problematic pattern, fix it
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Add the current except block
                fixed_lines.append(line)
                fixed_lines.append(lines[i + 1])  # The logger.warning line
                fixed_lines.append(lines[i + 2])  # The comment line
                
                # Skip the nested except block
                i += 3
                continue
            else:
                fixed_lines.append(line)
            
            i += 1
        
        # Write the fixed content back to the file
        with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print("Fixed malformed structure using line-by-line approach")
        return
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_custody_line_1612()