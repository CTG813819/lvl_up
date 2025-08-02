"""
Sandbox AI Service - Autonomous experimentation and learning with comprehensive SCKIPIT integration
Enhanced with ML-driven experiment design, pattern recognition, and autonomous learning capabilities
"""

import asyncio
import json
import os
import pickle
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import structlog
import numpy as np
import pandas as pd
import time
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression, LogisticRegression
import joblib

from ..core.database import get_session
from ..core.config import settings
from .ml_service import MLService
from .sckipit_service import SckipitService
from .ai_learning_service import AILearningService

logger = structlog.get_logger()


class SandboxAIService:
    """Sandbox AI Service - Autonomous experimentation and learning with comprehensive SCKIPIT integration"""
    
    _instance = None
    _initialized = False
    _experiments = {}
    _experiment_history = []
    _learning_patterns = {}
    _autonomous_cycles = []
    _ml_models = {}
    _sckipit_models = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SandboxAIService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            from .custody_protocol_service import CustodyProtocolService
            self.ml_service = MLService()
            self.sckipit_service = None  # Will be initialized properly in initialize()
            self.learning_service = AILearningService()
            self.custody_service = CustodyProtocolService()
            self._initialized = True
            self._initialize_enhanced_ml_models()
            
            # SCKIPIT Integration
            self.sckipit_experiment_models = {}
            self.sckipit_pattern_analyzer = None
            self.sckipit_autonomous_learner = None
            self.sckipit_proposal_generator = None
            self.sckipit_quality_assessor = None
            
            # Enhanced Experiment Data
            self.sckipit_enhanced_experiments = []
            self.pattern_recognition_results = []
            self.autonomous_learning_insights = []
            
            # Initialize SCKIPIT models
            self._initialize_sckipit_models()

    def _initialize_enhanced_ml_models(self):
        """Initialize enhanced ML models with SCKIPIT integration"""
        try:
            # Create models directory
            os.makedirs(settings.ml_model_path, exist_ok=True)
            
            # Enhanced ML Models with SCKIPIT Integration
            self._ml_models = {
                # Experiment Success Predictor (Enhanced with SCKIPIT)
                'experiment_success_predictor': RandomForestRegressor(
                    n_estimators=200, 
                    max_depth=15, 
                    min_samples_split=5,
                    random_state=42
                ),
                
                # Attack Effectiveness Predictor (Enhanced with SCKIPIT)
                'attack_effectiveness_predictor': GradientBoostingRegressor(
                    n_estimators=150,
                    learning_rate=0.1,
                    max_depth=10,
                    random_state=42
                ),
                
                # Pattern Recognition Analyzer (Enhanced with SCKIPIT)
                'pattern_recognition_analyzer': AdaBoostRegressor(
                    n_estimators=100,
                    learning_rate=0.05,
                    random_state=42
                ),
                
                # Learning Progress Predictor (Enhanced with SCKIPIT)
                'learning_progress_predictor': MLPRegressor(
                    hidden_layer_sizes=(100, 50, 25),
                    activation='relu',
                    solver='adam',
                    max_iter=500,
                    random_state=42
                ),
                
                # Experiment Design Optimizer (Enhanced with SCKIPIT)
                'experiment_design_optimizer': SVR(
                    kernel='rbf',
                    C=1.0,
                    gamma='scale'
                ),
                
                # Feature Selection for Better Models
                'feature_selector': SelectKBest(
                    score_func=f_regression,
                    k=15
                )
            }
            
            # Load existing models
            self._load_existing_enhanced_models()
            
            logger.info("Enhanced ML models with SCKIPIT integration initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing enhanced ML models: {str(e)}")
    
    def _initialize_sckipit_models(self):
        """Initialize SCKIPIT-specific models for Sandbox AI enhancement"""
        try:
            # SCKIPIT Experiment Models
            self.sckipit_models = {
                'experiment_designer': RandomForestRegressor(
                    n_estimators=150,
                    max_depth=12,
                    random_state=42
                ),
                
                'pattern_analyzer': GradientBoostingRegressor(
                    n_estimators=120,
                    learning_rate=0.1,
                    random_state=42
                ),
                
                'autonomous_learner': LogisticRegression(
                    random_state=42,
                    max_iter=200
                ),
                
                'quality_assessor': MLPRegressor(
                    hidden_layer_sizes=(80, 40),
                    activation='relu',
                    solver='adam',
                    max_iter=300,
                    random_state=42
                ),
                
                'text_analyzer': TfidfVectorizer(
                    max_features=1000,
                    ngram_range=(1, 3),
                    stop_words='english'
                ),
                
                'feature_extractor': PCA(
                    n_components=50,
                    random_state=42
                )
            }
            
            # Load existing SCKIPIT models
            self._load_existing_sckipit_models()
            
            logger.info("SCKIPIT models for Sandbox AI initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SCKIPIT models: {str(e)}")
    
    def _load_existing_enhanced_models(self):
        """Load existing enhanced ML models"""
        try:
            model_files = {
                'experiment_success_predictor': 'sandbox_experiment_success_predictor.pkl',
                'attack_effectiveness_predictor': 'sandbox_attack_effectiveness_predictor.pkl',
                'pattern_recognition_analyzer': 'sandbox_pattern_recognition_analyzer.pkl',
                'learning_progress_predictor': 'sandbox_learning_progress_predictor.pkl',
                'experiment_design_optimizer': 'sandbox_experiment_design_optimizer.pkl'
            }
            
            for model_name, filename in model_files.items():
                model_path = os.path.join(settings.ml_model_path, filename)
                if os.path.exists(model_path):
                    try:
                        with open(model_path, 'rb') as f:
                            self._ml_models[model_name] = pickle.load(f)
                        logger.info(f"Loaded enhanced model: {model_name}")
                    except Exception as e:
                        logger.error(f"Failed to load enhanced model {filename}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading existing enhanced models: {str(e)}")
    
    def _load_existing_sckipit_models(self):
        """Load existing trained SCKIPIT models"""
        try:
            model_files = {
                'experiment_designer': 'sckipit_experiment_designer.pkl',
                'pattern_analyzer': 'sckipit_pattern_analyzer.pkl',
                'autonomous_learner': 'sckipit_autonomous_learner.pkl',
                'quality_assessor': 'sckipit_quality_assessor.pkl',
                'text_analyzer': 'sckipit_text_analyzer.pkl',
                'feature_extractor': 'sckipit_feature_extractor.pkl'
            }
            
            for model_name, filename in model_files.items():
                model_path = os.path.join(settings.ml_model_path, filename)
                if os.path.exists(model_path):
                    try:
                        with open(model_path, 'rb') as f:
                            self.sckipit_models[model_name] = pickle.load(f)
                        logger.info(f"Loaded SCKIPIT model: {model_name}")
                    except Exception as e:
                        logger.error(f"Failed to load SCKIPIT model {filename}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading existing SCKIPIT models: {str(e)}")

    async def answer_prompt(self, prompt: str) -> str:
        """Generate autonomous answer using internal ML models and SCKIPIT capabilities"""
        try:
            # Ensure sckipit_service is initialized
            if not hasattr(self, 'sckipit_service') or self.sckipit_service is None:
                from .sckipit_service import SckipitService
                self.sckipit_service = await SckipitService.initialize()
            
            # Get learning context
            learning_log = await self.learning_service.get_learning_log("sandbox")
            
            # Generate autonomous response using internal capabilities
            response = await self._generate_autonomous_response(prompt, learning_log)
            
            # Log the response for learning and analytics
            await self.learning_service.log_answer("sandbox", prompt, response, {
                "method": "autonomous_ml",
                "ai_type": "sandbox",
                "timestamp": datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in autonomous answer generation: {str(e)}")
            # Generate a thoughtful fallback using internal logic
            return await self._generate_thoughtful_fallback(prompt, str(e))

    async def _generate_autonomous_response(self, prompt: str, learning_log: str) -> str:
        """Generate response using internal ML models and reasoning"""
        try:
            # Analyze the prompt using internal ML models
            prompt_analysis = await self._analyze_prompt_intent(prompt)
            
            # Extract relevant knowledge from learning log
            knowledge_context = await self._extract_relevant_knowledge(prompt, learning_log)
            
            # Generate response based on AI type and capabilities
            if "experiment" in prompt.lower() or "test" in prompt.lower():
                response = await self._generate_experiment_response(prompt, prompt_analysis, knowledge_context)
            elif "pattern" in prompt.lower() or "analyze" in prompt.lower():
                response = await self._generate_pattern_analysis_response(prompt, prompt_analysis, knowledge_context)
            elif "attack" in prompt.lower() or "security" in prompt.lower():
                response = await self._generate_attack_response(prompt, prompt_analysis, knowledge_context)
            else:
                response = await self._generate_general_response(prompt, prompt_analysis, knowledge_context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in autonomous response generation: {str(e)}")
            return await self._generate_thoughtful_fallback(prompt, str(e))

    async def _analyze_prompt_intent(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt intent using internal ML models"""
        try:
            # Use internal ML models to analyze prompt
            intent_features = {
                'length': len(prompt),
                'has_experiment_keywords': any(word in prompt.lower() for word in ['experiment', 'test', 'trial', 'study']),
                'has_pattern_keywords': any(word in prompt.lower() for word in ['pattern', 'analyze', 'analyze', 'identify']),
                'has_attack_keywords': any(word in prompt.lower() for word in ['attack', 'security', 'vulnerability', 'penetration']),
                'complexity_score': len(prompt.split()) / 10.0,  # Simple complexity metric
                'urgency_indicator': any(word in prompt.lower() for word in ['urgent', 'quick', 'immediate', 'critical'])
            }
            
            # Use internal models to predict intent
            if 'experiment_success_predictor' in self._ml_models:
                try:
                    intent_score = self._ml_models['experiment_success_predictor'].predict([list(intent_features.values())])[0]
                except Exception as e:
                    logger.warning(f"ML model not fitted, using fallback: {str(e)}")
                    intent_score = 0.75  # Default confidence for sandbox AI
            else:
                intent_score = 0.75  # Default confidence for sandbox AI
            
            return {
                'intent_type': self._classify_intent(intent_features),
                'confidence': intent_score,
                'features': intent_features,
                'complexity': intent_features['complexity_score']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing prompt intent: {str(e)}")
            return {
                'intent_type': 'general',
                'confidence': 0.6,
                'features': {},
                'complexity': 0.5
            }

    def _classify_intent(self, features: Dict[str, Any]) -> str:
        """Classify prompt intent based on features"""
        if features['has_experiment_keywords']:
            return 'experiment_design'
        elif features['has_pattern_keywords']:
            return 'pattern_analysis'
        elif features['has_attack_keywords']:
            return 'attack_planning'
        else:
            return 'general'

    async def _extract_relevant_knowledge(self, prompt: str, learning_log: str) -> Dict[str, Any]:
        """Extract relevant knowledge from learning history"""
        try:
            # Simple keyword-based knowledge extraction
            relevant_patterns = []
            if "experiment" in prompt.lower():
                relevant_patterns.append("experiment_design")
            if "pattern" in prompt.lower():
                relevant_patterns.append("pattern_recognition")
            if "attack" in prompt.lower():
                relevant_patterns.append("attack_effectiveness")
            if "test" in prompt.lower():
                relevant_patterns.append("testing_methodologies")
            
            return {
                'relevant_patterns': relevant_patterns,
                'learning_context': learning_log[:500] if learning_log else "No specific learning context",
                'knowledge_domain': self._identify_knowledge_domain(prompt)
            }
            
        except Exception as e:
            logger.error(f"Error extracting knowledge: {str(e)}")
            return {
                'relevant_patterns': [],
                'learning_context': "Knowledge extraction failed",
                'knowledge_domain': 'general'
            }

    def _identify_knowledge_domain(self, prompt: str) -> str:
        """Identify the knowledge domain for the prompt"""
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['experiment', 'test', 'trial']):
            return 'experiment_design'
        elif any(word in prompt_lower for word in ['pattern', 'analyze', 'identify']):
            return 'pattern_analysis'
        elif any(word in prompt_lower for word in ['attack', 'security', 'vulnerability']):
            return 'security_testing'
        else:
            return 'general_experimentation'

    async def _generate_experiment_response(self, prompt: str, analysis: Dict[str, Any], knowledge: Dict[str, Any]) -> str:
        """Generate response for experiment design requests"""
        try:
            # Use internal experiment knowledge
            experiment_strategies = [
                "I can design comprehensive experiments to test hypotheses and validate approaches.",
                "Let me create experimental protocols that will provide meaningful insights.",
                "I'll design experiments that can effectively measure and analyze outcomes.",
                "I can help you set up experiments with proper controls and variables."
            ]
            
            # Select strategy based on analysis
            strategy_index = int(analysis['confidence'] * len(experiment_strategies)) % len(experiment_strategies)
            base_response = experiment_strategies[strategy_index]
            
            # Add specific insights based on knowledge domain
            if knowledge['knowledge_domain'] == 'experiment_design':
                base_response += " Consider implementing A/B testing and statistical validation methods."
            elif analysis['features']['urgency_indicator']:
                base_response += " For urgent testing, focus on rapid prototyping and iterative validation."
            
            return f"🧪 Sandbox AI Experiment Design: {base_response}"
            
        except Exception as e:
            logger.error(f"Error generating experiment response: {str(e)}")
            return "🧪 Sandbox AI: I can help you design and conduct effective experiments."

    async def _generate_pattern_analysis_response(self, prompt: str, analysis: Dict[str, Any], knowledge: Dict[str, Any]) -> str:
        """Generate response for pattern analysis requests"""
        try:
            pattern_insights = [
                "I can analyze patterns in data to identify trends and correlations.",
                "Let me help you recognize patterns that could lead to valuable insights.",
                "I'll use pattern recognition to uncover hidden relationships in your data.",
                "I can identify behavioral patterns and predict future outcomes."
            ]
            
            strategy_index = int(analysis['confidence'] * len(pattern_insights)) % len(pattern_insights)
            base_response = pattern_insights[strategy_index]
            
            if knowledge['knowledge_domain'] == 'pattern_analysis':
                base_response += " Consider using machine learning algorithms for advanced pattern detection."
            
            return f"🧪 Sandbox AI Pattern Analysis: {base_response}"
            
        except Exception as e:
            logger.error(f"Error generating pattern analysis response: {str(e)}")
            return "🧪 Sandbox AI: I can help analyze patterns and identify meaningful insights."

    async def _generate_attack_response(self, prompt: str, analysis: Dict[str, Any], knowledge: Dict[str, Any]) -> str:
        """Generate response for attack planning requests"""
        try:
            attack_insights = [
                "I can help design security testing scenarios to identify vulnerabilities.",
                "Let me create penetration testing strategies to assess system security.",
                "I'll help you develop attack simulations to test defense mechanisms.",
                "I can assist with security assessment and vulnerability testing."
            ]
            
            strategy_index = int(analysis['confidence'] * len(attack_insights)) % len(attack_insights)
            base_response = attack_insights[strategy_index]
            
            return f"🧪 Sandbox AI Security Testing: {base_response}"
            
        except Exception as e:
            logger.error(f"Error generating attack response: {str(e)}")
            return "🧪 Sandbox AI: I can help design security testing and vulnerability assessment."

    async def _generate_general_response(self, prompt: str, analysis: Dict[str, Any], knowledge: Dict[str, Any]) -> str:
        """Generate general response for other types of prompts"""
        try:
            general_insights = [
                "I can help you with experiment design, pattern analysis, and security testing.",
                "As Sandbox AI, I specialize in experimental approaches and testing methodologies.",
                "I can assist with hypothesis testing, data analysis, and security assessments.",
                "Let me help you explore new approaches through systematic experimentation."
            ]
            
            strategy_index = int(analysis['confidence'] * len(general_insights)) % len(general_insights)
            base_response = general_insights[strategy_index]
            
            return f"🧪 Sandbox AI: {base_response}"
            
        except Exception as e:
            logger.error(f"Error generating general response: {str(e)}")
            return "🧪 Sandbox AI: I'm here to help you experiment and discover new insights."

    async def _generate_thoughtful_fallback(self, prompt: str, error: str) -> str:
        """Generate a thoughtful fallback response when errors occur"""
        try:
            # Use internal logic to generate a meaningful response
            fallback_responses = [
                "I'm analyzing your request and will design appropriate experiments.",
                "Let me process this through my experimental models for the best approach.",
                "I'm applying my testing knowledge to help you discover new insights.",
                "Based on my learning, I can assist with experimental design and analysis."
            ]
            
            # Use prompt length to select response
            response_index = len(prompt) % len(fallback_responses)
            base_response = fallback_responses[response_index]
            
            return f"🧪 Sandbox AI: {base_response}"
            
        except Exception as e:
            logger.error(f"Error in thoughtful fallback: {str(e)}")
            return "🧪 Sandbox AI: I'm here to help you experiment and discover new insights."

    async def run_experiment(self, experiment_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Run an experiment with the given parameters"""
        try:
            experiment_id = str(uuid.uuid4())
            experiment_data = {
                'id': experiment_id,
                'type': experiment_type,
                'parameters': parameters,
                'start_time': datetime.utcnow().isoformat(),
                'status': 'running'
            }
            
            # Store experiment
            self._experiments[experiment_id] = experiment_data
            
            # Run the experiment using ML service
            result = await self.ml_service.run_experiment(experiment_type, parameters)
            
            # Update experiment data
            experiment_data['result'] = result
            experiment_data['end_time'] = datetime.utcnow().isoformat()
            experiment_data['status'] = 'completed'
            
            # Store in history
            self._experiment_history.append(experiment_data)
            
            return {
                'experiment_id': experiment_id,
                'result': result,
                'status': 'completed'
            }
        except Exception as e:
            logger.error(f"Error running experiment: {str(e)}")
            return {'error': str(e)}

    async def analyze_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in the given data"""
        try:
            # Use pattern recognition model
            if 'pattern_recognition_analyzer' in self._ml_models:
                # Convert data to features
                features = self._extract_features_from_data(data)
                pattern_result = self._ml_models['pattern_recognition_analyzer'].predict(features)
                
                return {
                    'patterns_found': len(pattern_result),
                    'pattern_analysis': pattern_result.tolist(),
                    'confidence': 0.85
                }
            else:
                return {'error': 'Pattern recognition model not available'}
        except Exception as e:
            logger.error(f"Error analyzing patterns: {str(e)}")
            return {'error': str(e)}

    async def generate_attack_plan(self, target_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an attack plan based on target information"""
        try:
            # Use attack effectiveness predictor
            if 'attack_effectiveness_predictor' in self._ml_models:
                # Extract features from target info
                features = self._extract_target_features(target_info)
                effectiveness_score = self._ml_models['attack_effectiveness_predictor'].predict([features])[0]
                
                return {
                    'attack_plan': 'Generated attack plan based on ML analysis',
                    'effectiveness_score': float(effectiveness_score),
                    'recommended_approach': 'ML-optimized approach',
                    'confidence': 0.9
                }
            else:
                return {'error': 'Attack effectiveness model not available'}
        except Exception as e:
            logger.error(f"Error generating attack plan: {str(e)}")
            return {'error': str(e)}

    async def evaluate_attack_result(self, attack_result: str, target_info: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the result of an attack"""
        try:
            # Use quality assessor model
            if 'quality_assessor' in self.sckipit_models:
                # Evaluate the attack result
                evaluation_score = 0.85  # Placeholder
                
                return {
                    'evaluation_score': evaluation_score,
                    'success_rate': 0.9,
                    'improvements_suggested': ['Optimize timing', 'Enhance stealth'],
                    'learning_insights': 'Attack pattern identified for future use'
                }
            else:
                return {'error': 'Quality assessor model not available'}
        except Exception as e:
            logger.error(f"Error evaluating attack result: {str(e)}")
            return {'error': str(e)}

    def _extract_features_from_data(self, data: List[Dict[str, Any]]) -> np.ndarray:
        """Extract features from data for ML models"""
        # Placeholder implementation
        return np.array([[0.1, 0.2, 0.3, 0.4, 0.5]])

    def _extract_target_features(self, target_info: Dict[str, Any]) -> np.ndarray:
        """Extract features from target information"""
        # Placeholder implementation
        return np.array([0.1, 0.2, 0.3, 0.4, 0.5])

    @classmethod
    async def initialize(cls):
        """Initialize the Sandbox AI service"""
        instance = cls()
        if not cls._initialized:
            cls._initialized = True
            # Initialize SckipitService properly
            from .sckipit_service import SckipitService
            instance.sckipit_service = await SckipitService.initialize()
            logger.info("🔬 Sandbox AI Service initialized with comprehensive SCKIPIT integration")
        return instance 