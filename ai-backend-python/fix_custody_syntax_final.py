#!/usr/bin/env python3
"""
Targeted fix for custody_protocol_service.py syntax errors
"""

def fix_custody_syntax_final():
    """Fix the specific syntax errors in custody_protocol_service.py"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the specific problematic section around lines 469-488
    old_pattern_469 = '''        try:
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
            # Fallback: use empty list if method not present
            if hasattr(self.learning_service, 'identify_knowledge_gaps'):
                knowledge_gaps = await self.learning_service.identify_knowledge_gaps(ai_type)
            else:
                knowledge_gaps = []
        except:
            knowledge_gaps = []'''
    
    new_pattern_469 = '''        try:
            # Fallback: use empty list if method not present
            if hasattr(self.learning_service, 'identify_knowledge_gaps'):
                knowledge_gaps = await self.learning_service.identify_knowledge_gaps(ai_type)
            else:
                knowledge_gaps = []
        except AttributeError as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
            knowledge_gaps = []
        except Exception as e:
            knowledge_gaps = []'''
    
    # Fix the problematic section around lines 5526-5540
    old_pattern_5526 = '''        try:
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
            # Local import to avoid circular import'''
    
    new_pattern_5526 = '''        try:
            # Local import to avoid circular import'''
    
    # Fix the problematic section around lines 5531-5540
    old_pattern_5531 = '''            except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior'''
    
    new_pattern_5531 = '''        except AttributeError as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
        except Exception as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior'''
    
    # Apply the fixes
    content = content.replace(old_pattern_469, new_pattern_469)
    content = content.replace(old_pattern_5526, new_pattern_5526)
    content = content.replace(old_pattern_5531, new_pattern_5531)
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed syntax errors in custody_protocol_service.py")

if __name__ == "__main__":
    fix_custody_syntax_final()