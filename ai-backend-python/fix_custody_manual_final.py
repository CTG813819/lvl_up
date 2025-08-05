#!/usr/bin/env python3
"""
Manual fix for custody_protocol_service.py indentation errors
"""

def fix_custody_manual():
    """Manually fix the malformed try-except blocks in custody_protocol_service.py"""
    
    # Read the file
    with open('app/services/custody_protocol_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the specific problematic sections by replacing malformed patterns
    
    # Pattern 1: _initialize_custody_tracking method
    old_pattern_1 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            # Initialize custody metrics for all AI types using AgentMetricsService'''
    
    new_pattern_1 = '''        try:
            # Initialize custody metrics for all AI types using AgentMetricsService'''
    
    # Pattern 2: administer_custody_test method
    old_pattern_2 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            logger.info(f"[ADMINISTER TEST] Starting custody test for {ai_type}")'''
    
    new_pattern_2 = '''        try:
            logger.info(f"[ADMINISTER TEST] Starting custody test for {ai_type}")'''
    
    # Pattern 3: _get_ai_level method
    old_pattern_3 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            # Use the agent_metrics_service to get the level instead of creating a new session'''
    
    new_pattern_3 = '''        try:
            # Use the agent_metrics_service to get the level instead of creating a new session'''
    
    # Pattern 4: _generate_knowledge_test method
    old_pattern_4 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            # Analyze learning patterns and knowledge gaps'''
    
    new_pattern_4 = '''        try:
            # Analyze learning patterns and knowledge gaps'''
    
    # Pattern 5: _analyze_ai_knowledge method
    old_pattern_5 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            # Extract topics and subjects from learning history'''
    
    new_pattern_5 = '''        try:
            # Extract topics and subjects from learning history'''
    
    # Pattern 6: _analyze_learning_patterns method
    old_pattern_6 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            if not learning_history:'''
    
    new_pattern_6 = '''        try:
            if not learning_history:'''
    
    # Pattern 7: _identify_knowledge_gaps method
    old_pattern_7 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            # Define expected knowledge areas for each AI type'''
    
    new_pattern_7 = '''        try:
            # Define expected knowledge areas for each AI type'''
    
    # Pattern 8: _analyze_learning_depth method
    old_pattern_8 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            if not content_analysis:'''
    
    new_pattern_8 = '''        try:
            if not content_analysis:'''
    
    # Pattern 9: _generate_ml_scenario method
    old_pattern_9 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            # Get AI learning history and analytics'''
    
    new_pattern_9 = '''        try:
            # Get AI learning history and analytics'''
    
    # Pattern 10: _identify_ai_strengths method
    old_pattern_10 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            strengths = []'''
    
    new_pattern_10 = '''        try:
            strengths = []'''
    
    # Pattern 11: _generate_scenario_from_patterns method
    old_pattern_11 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            difficulty = features['difficulty']'''
    
    new_pattern_11 = '''        try:
            difficulty = features['difficulty']'''
    
    # Pattern 12: _build_dynamic_scenario_components method
    old_pattern_12 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            # Get learning history to understand what the AI has encountered'''
    
    new_pattern_12 = '''        try:
            # Get learning history to understand what the AI has encountered'''
    
    # Pattern 13: _create_adaptive_scenario method
    old_pattern_13 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            # Base scenario structure'''
    
    new_pattern_13 = '''        try:
            # Base scenario structure'''
    
    # Pattern 14: _add_learning_based_complexity method
    old_pattern_14 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            # Get recent test results to understand current capabilities'''
    
    new_pattern_14 = '''        try:
            # Get recent test results to understand current capabilities'''
    
    # Pattern 15: _evaluate_attack_with_ml method
    old_pattern_15 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            # Extract features from scenario and attack'''
    
    new_pattern_15 = '''        try:
            # Extract features from scenario and attack'''
    
    # Pattern 16: _persist_olympic_event_to_database method
    old_pattern_16 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            session = get_session()'''
    
    new_pattern_16 = '''        try:
            session = get_session()'''
    
    # Pattern 17: _detect_ood method
    old_pattern_17 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            ood_prompt = f"Is the following text out-of-distribution (OOD) for the {ai_type} AI? Analyze for distributional shift, novelty, or unexpected content. Return a JSON with 'is_ood' (true/false), 'confidence', and 'reason'.\nText: {text}"'''
    
    new_pattern_17 = '''        try:
            ood_prompt = f"Is the following text out-of-distribution (OOD) for the {ai_type} AI? Analyze for distributional shift, novelty, or unexpected content. Return a JSON with 'is_ood' (true/false), 'confidence', and 'reason'.\nText: {text}"'''
    
    # Pattern 18: _load_test_models method
    old_pattern_18 = '''        try:
            model_path = f"{settings.ml_model_path}/custody"
            
            for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
                for difficulty in TestDifficulty:
                    model_file = f"{model_path}/{ai_type}_{difficulty.value}_test_model.pkl"
                    if os.path.exists(model_file):
                        self.test_models[f"{ai_type}_{difficulty.value}"] = joblib.load(model_file)
                        logger.info(f"Loaded test model for {ai_type} {difficulty.value}")
        except AttributeError as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
        except Exception as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
        except Exception as e:
            logger.error(f"Error loading test models: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading test models: {str(e)}")'''
    
    new_pattern_18 = '''        try:
            model_path = f"{settings.ml_model_path}/custody"
            
            for ai_type in ["imperium", "guardian", "sandbox", "conquest"]:
                for difficulty in TestDifficulty:
                    model_file = f"{model_path}/{ai_type}_{difficulty.value}_test_model.pkl"
                    if os.path.exists(model_file):
                        self.test_models[f"{ai_type}_{difficulty.value}"] = joblib.load(model_file)
                        logger.info(f"Loaded test model for {ai_type} {difficulty.value}")
        except AttributeError as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
        except Exception as e:
            logger.error(f"Error loading test models: {str(e)}")'''
    
    # Pattern 19: _initialize_custody_tracking method
    old_pattern_19 = '''        try:
                pass
        except AttributeError as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            except Exception as e:
                logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
                # Continue with fallback behavior
            # Initialize custody metrics for all AI types using AgentMetricsService
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            for ai_type in ai_types:
                # Check if metrics exist, if not create default ones
                existing_metrics = await self.agent_metrics_service.get_custody_metrics(ai_type)
                if not existing_metrics:
                    default_metrics = {
                        "total_tests_given": 0,
                        "total_tests_passed": 0,
                        "total_tests_failed": 0,
                        "current_difficulty": TestDifficulty.BASIC.value,
                        "last_test_date": None,
                        "consecutive_failures": 0,
                        "consecutive_successes": 0,
                        "test_history": [],
                        "custody_level": 1,
                        "custody_xp": 0
                    }
                    await self.agent_metrics_service.create_or_update_agent_metrics(ai_type, default_metrics)
            
            logger.info("Custody protocol tracking initialized")
                
        except Exception as e:'''
    
    new_pattern_19 = '''        try:
            # Initialize custody metrics for all AI types using AgentMetricsService
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            for ai_type in ai_types:
                # Check if metrics exist, if not create default ones
                existing_metrics = await self.agent_metrics_service.get_custody_metrics(ai_type)
                if not existing_metrics:
                    default_metrics = {
                        "total_tests_given": 0,
                        "total_tests_passed": 0,
                        "total_tests_failed": 0,
                        "current_difficulty": TestDifficulty.BASIC.value,
                        "last_test_date": None,
                        "consecutive_failures": 0,
                        "consecutive_successes": 0,
                        "test_history": [],
                        "custody_level": 1,
                        "custody_xp": 0
                    }
                    await self.agent_metrics_service.create_or_update_agent_metrics(ai_type, default_metrics)
            
            logger.info("Custody protocol tracking initialized")
        except AttributeError as e:
            logger.warning(f"⚠️ EnhancedTestGenerator method not available: {e}")
            # Continue with fallback behavior
        except Exception as e:'''
    
    # Apply all replacements
    replacements = [
        (old_pattern_1, new_pattern_1),
        (old_pattern_2, new_pattern_2),
        (old_pattern_3, new_pattern_3),
        (old_pattern_4, new_pattern_4),
        (old_pattern_5, new_pattern_5),
        (old_pattern_6, new_pattern_6),
        (old_pattern_7, new_pattern_7),
        (old_pattern_8, new_pattern_8),
        (old_pattern_9, new_pattern_9),
        (old_pattern_10, new_pattern_10),
        (old_pattern_11, new_pattern_11),
        (old_pattern_12, new_pattern_12),
        (old_pattern_13, new_pattern_13),
        (old_pattern_14, new_pattern_14),
        (old_pattern_15, new_pattern_15),
        (old_pattern_16, new_pattern_16),
        (old_pattern_17, new_pattern_17),
        (old_pattern_18, new_pattern_18),
        (old_pattern_19, new_pattern_19),
    ]
    
    for old_pattern, new_pattern in replacements:
        content = content.replace(old_pattern, new_pattern)
    
    # Write the fixed content back to the file
    with open('app/services/custody_protocol_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed malformed try-except blocks in custody_protocol_service.py")

if __name__ == "__main__":
    fix_custody_manual()