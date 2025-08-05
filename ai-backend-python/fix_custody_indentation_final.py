#!/usr/bin/env python3
"""
Final script to fix all indentation issues in custody_protocol_service.py
The file has malformed try-except blocks with incorrect indentation and duplicate except statements.
"""

def fix_custody_indentation_final():
    """Fix all indentation issues in custody_protocol_service.py"""
    
    file_path = "app/services/custody_protocol_service.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all malformed try-except blocks with properly structured ones
    # Pattern 1: try:\n                pass\nexcept AttributeError as e:\n                logger.warning...\n            except Exception as e:\n
    content = content.replace(
        "try:\n                pass\nexcept AttributeError as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior\n            except Exception as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior",
        "try:\n                pass\n            except AttributeError as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior\n            except Exception as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior"
    )
    
    # Pattern 2: try:\n                pass\nexcept Exception as e:\n                logger.warning...\n            except Exception as e:\n
    content = content.replace(
        "try:\n                pass\nexcept Exception as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior\n            except Exception as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior",
        "try:\n                pass\n            except Exception as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior\n            except Exception as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior"
    )
    
    # Pattern 3: try:\n                pass\nexcept KeyError as e:\n                logger.warning...\n            except Exception as e:\n
    content = content.replace(
        "try:\n                pass\nexcept KeyError as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior\n            except Exception as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior",
        "try:\n                pass\n            except KeyError as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior\n            except Exception as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior"
    )
    
    # Pattern 4: try:\n                pass\nexcept ValueError as e:\n                logger.warning...\n            except Exception as e:\n
    content = content.replace(
        "try:\n                pass\nexcept ValueError as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior\n            except Exception as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior",
        "try:\n                pass\n            except ValueError as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior\n            except Exception as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior"
    )
    
    # Pattern 5: try:\n                pass\nexcept TypeError as e:\n                logger.warning...\n            except Exception as e:\n
    content = content.replace(
        "try:\n                pass\nexcept TypeError as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior\n            except Exception as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior",
        "try:\n                pass\n            except TypeError as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior\n            except Exception as e:\n                logger.warning(f\"⚠️ EnhancedTestGenerator method not available: {e}\")\n                # Continue with fallback behavior"
    )
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed all indentation issues in custody_protocol_service.py")

if __name__ == "__main__":
    fix_custody_indentation_final()