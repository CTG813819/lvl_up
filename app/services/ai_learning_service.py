"""
AI Learning service with ENHANCED ML integration using scikit-learn for PRODUCTION IMPROVEMENT
Enhanced with comprehensive SCKIPIT integration for advanced learning patterns and knowledge validation
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
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
import joblib

from ..core.database import get_session
from ..core.config import settings
from .ml_service import MLService
from .sckipit_service import SckipitService
from .enhanced_ml_learning_service import EnhancedMLLearningService
from app.services.anthropic_service import call_claude, anthropic_rate_limited_call

logger = structlog.get_logger()


class AILearningService:
    """AI Learning service with ENHANCED ML integration using scikit-learn for PRODUCTION IMPROVEMENT"""
    
    _instance = None
    _initialized = False
    _learning_states = {}
    _periodic_task_running = False
    _last_periodic_learning = None
    _latest_learning_results = {}
    _ml_models = {}
    _learning_data = []
    _proposal_improvement_history = []
    _productivity_metrics = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AILearningService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ml_service = MLService()
            self.sckipit_service = None  # Will be initialized properly in initialize()
            self.enhanced_ml_service = EnhancedMLLearningService()
            self._initialized = True
            self._initialize_enhanced_ml_models()
            
            # SCKIPIT Integration
            self.sckipit_models = {}
            self.sckipit_knowledge_patterns = {}
            self.sckipit_learning_insights = {}
            self.sckipit_validation_results = {}
            
            # Enhanced Learning Patterns
            self.learning_pattern_analyzer = None
            self.knowledge_validator = None
            self.pattern_clusterer = None
            self.quality_assessor = None
            
            # SCKIPIT-Enhanced Learning Data
            self.sckipit_enhanced_data = []
            self.pattern_recognition_results = []
            self.knowledge_validation_history = []
            
            # Initialize SCKIPIT models
            self._initialize_sckipit_models()
    
    @classmethod
    async def initialize(cls):
        """Initialize the AI Learning service"""
        instance = cls()
        # Initialize SckipitService
        try:
            from .sckipit_service import SckipitService
            instance.sckipit_service = await SckipitService.initialize()
            logger.info("SckipitService initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize SckipitService: {e}")
            instance.sckipit_service = None
        logger.info("AI Learning Service initialized with ENHANCED ML capabilities")
        return instance
    
    def _initialize_enhanced_ml_models(self):
        """Initialize enhanced ML models with SCKIPIT integration"""
        try:
            # Create models directory
            os.makedirs(settings.ml_model_path, exist_ok=True)
            
            # Enhanced ML Models with SCKIPIT Integration
            self._ml_models = {
                # Proposal Quality Prediction (Enhanced with SCKIPIT)
                'proposal_quality_predictor': RandomForestClassifier(
                    n_estimators=200, 
                    max_depth=15, 
                    min_samples_split=5,
                    random_state=42
                ),
                
                # Failure Prediction (Enhanced with SCKIPIT)
                'failure_predictor': GradientBoostingClassifier(
                    n_estimators=150,
                    learning_rate=0.1,
                    max_depth=10,
                    random_state=42
                ),
                
                # Improvement Recommendation Engine (Enhanced with SCKIPIT)
                'improvement_recommender': AdaBoostClassifier(
                    n_estimators=100,
                    learning_rate=0.05,
                    random_state=42
                ),
                
                # Code Quality Analyzer (Enhanced with SCKIPIT)
                'code_quality_analyzer': MLPClassifier(
                    hidden_layer_sizes=(100, 50, 25),
                    activation='relu',
                    solver='adam',
                    max_iter=500,
                    random_state=42
                ),
                
                # Productivity Predictor (Enhanced with SCKIPIT)
                'productivity_predictor': SVC(
                    kernel='rbf',
                    C=1.0,
                    gamma='scale',
                    probability=True,
                    random_state=42
                ),
                
                # Learning Pattern Analyzer (SCKIPIT-Enhanced)
                'learning_pattern_analyzer': KMeans(
                    n_clusters=8,
                    random_state=42
                ),
                
                # Knowledge Validator (SCKIPIT-Enhanced)
                'knowledge_validator': LogisticRegression(
                    random_state=42,
                    max_iter=300
                ),
                
                # Pattern Clusterer (SCKIPIT-Enhanced)
                'pattern_clusterer': DBSCAN(
                    eps=0.5,
                    min_samples=5
                ),
                
                # Quality Assessor (SCKIPIT-Enhanced)
                'quality_assessor': RandomForestClassifier(
                    n_estimators=150,
                    max_depth=12,
                    random_state=42
                ),
                
                # Feature Selection for Better Models
                'feature_selector': SelectKBest(
                    score_func=f_classif,
                    k=15
                )
            }
            
            # Load existing models
            self._load_existing_models()
            
            logger.info("Enhanced ML models with SCKIPIT integration initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing enhanced ML models: {str(e)}")
    
    def _initialize_sckipit_models(self):
        """Initialize SCKIPIT-specific models for AI learning enhancement"""
        try:
            # SCKIPIT Learning Pattern Models
            self.sckipit_models = {
                'learning_pattern_analyzer': KMeans(
                    n_clusters=6,
                    random_state=42
                ),
                
                'knowledge_validator': LogisticRegression(
                    random_state=42,
                    max_iter=200
                ),
                
                'pattern_clusterer': DBSCAN(
                    eps=0.3,
                    min_samples=3
                ),
                
                'quality_assessor': RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
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
            
            logger.info("SCKIPIT models for AI learning initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SCKIPIT models: {str(e)}")
    
    def _load_existing_sckipit_models(self):
        """Load existing trained SCKIPIT models"""
        try:
            model_files = {
                'learning_pattern_analyzer': 'sckipit_learning_pattern_analyzer.pkl',
                'knowledge_validator': 'sckipit_knowledge_validator.pkl',
                'pattern_clusterer': 'sckipit_pattern_clusterer.pkl',
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
    
    async def _save_sckipit_model(self, model_name: str):
        """Save a trained SCKIPIT model"""
        try:
            model_path = os.path.join(settings.ml_model_path, f"sckipit_{model_name}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(self.sckipit_models[model_name], f)
            logger.info(f"Saved SCKIPIT model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to save SCKIPIT model {model_name}: {str(e)}")
    
    # ==================== SCKIPIT-ENHANCED LEARNING METHODS ====================
    
    async def learn_from_failure_with_sckipit(self, proposal_id: str, test_summary: str, ai_type: str, proposal_data: Dict):
        """Learn from test failures using SCKIPIT-enhanced ML for better proposal improvement"""
        try:
            logger.info(f"Learning from failure with SCKIPIT for proposal {proposal_id}")
            
            # Extract enhanced features with SCKIPIT analysis
            failure_features = await self._extract_enhanced_failure_features(proposal_data, test_summary, ai_type)
            
            # SCKIPIT Pattern Analysis
            pattern_analysis = await self._analyze_learning_patterns_with_sckipit(failure_features, ai_type)
            
            # SCKIPIT Knowledge Validation
            knowledge_validation = await self._validate_knowledge_with_sckipit(test_summary, proposal_data)
            
            # SCKIPIT Quality Assessment
            quality_assessment = await self._assess_quality_with_sckipit(proposal_data, failure_features)
            
            # Enhanced learning record with SCKIPIT insights
            learning_record = {
                'timestamp': datetime.now().isoformat(),
                'proposal_id': proposal_id,
                'ai_type': ai_type,
                'failure_type': await self._classify_failure_type(test_summary),
                'features': failure_features,
                'test_summary': test_summary,
                'outcome': 'failure',
                'sckipit_patterns': pattern_analysis,
                'sckipit_validation': knowledge_validation,
                'sckipit_quality': quality_assessment,
                'productivity_impact': await self._calculate_productivity_impact(failure_features, ai_type),
                'ml_confidence': await self._calculate_ml_confidence(failure_features),
                'learning_value': await self._calculate_learning_value_from_failure(failure_features, ai_type)
            }
            
            self._learning_data.append(learning_record)
            
            # Train enhanced failure prediction model with SCKIPIT
            await self._train_enhanced_failure_predictor_with_sckipit()
            
            # Update SCKIPIT learning insights
            await self._update_sckipit_learning_insights(learning_record)
            
            # Generate SCKIPIT-enhanced improvements
            improvements = await self._generate_sckipit_enhanced_improvements(failure_features, pattern_analysis, knowledge_validation)
            
            # Update AI learning state with SCKIPIT insights
            await self._update_enhanced_ai_learning_state_with_sckipit(ai_type, 'failure_learning', improvements, failure_features, pattern_analysis)
            
            logger.info(f"SCKIPIT-enhanced learning from failure completed for {ai_type}")
            
        except Exception as e:
            logger.error(f"Error in SCKIPIT-enhanced failure learning: {str(e)}")
    
    async def _analyze_learning_patterns_with_sckipit(self, features: Dict, ai_type: str) -> Dict[str, Any]:
        """Analyze learning patterns using SCKIPIT models"""
        try:
            # Extract pattern features
            pattern_features = await self._extract_pattern_features(features, ai_type)
            
            # Use SCKIPIT pattern analyzer
            if 'learning_pattern_analyzer' in self.sckipit_models:
                X = np.array([list(pattern_features.values())])
                pattern_cluster = self.sckipit_models['learning_pattern_analyzer'].predict(X)[0]
                
                # Analyze pattern characteristics
                pattern_analysis = {
                    'cluster_id': int(pattern_cluster),
                    'pattern_type': await self._classify_pattern_type(pattern_cluster, pattern_features),
                    'complexity_level': await self._assess_pattern_complexity(pattern_features),
                    'learning_potential': await self._calculate_learning_potential(pattern_features),
                    'improvement_areas': await self._identify_improvement_areas(pattern_features),
                    'recommendations': await self._generate_pattern_recommendations(pattern_cluster, pattern_features)
                }
            else:
                pattern_analysis = {
                    'cluster_id': 0,
                    'pattern_type': 'unknown',
                    'complexity_level': 'medium',
                    'learning_potential': 0.5,
                    'improvement_areas': [],
                    'recommendations': []
                }
            
            return pattern_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing learning patterns with SCKIPIT: {str(e)}")
            return {'cluster_id': 0, 'pattern_type': 'error', 'learning_potential': 0.0}
    
    async def _validate_knowledge_with_sckipit(self, test_summary: str, proposal_data: Dict) -> Dict[str, Any]:
        """Validate knowledge using SCKIPIT models"""
        try:
            # Extract validation features
            validation_features = await self._extract_validation_features(test_summary, proposal_data)
            
            # Use SCKIPIT knowledge validator
            if 'knowledge_validator' in self.sckipit_models:
                X = np.array([list(validation_features.values())])
                validation_score = self.sckipit_models['knowledge_validator'].predict_proba(X)[0][1]
                
                validation_result = {
                    'is_valid': validation_score > 0.7,
                    'validation_score': float(validation_score),
                    'confidence': await self._calculate_validation_confidence(validation_features),
                    'knowledge_gaps': await self._identify_knowledge_gaps(validation_features),
                    'recommendations': await self._generate_validation_recommendations(validation_score, test_summary)
                }
            else:
                validation_result = {
                    'is_valid': True,
                    'validation_score': 0.8,
                    'confidence': 0.7,
                    'knowledge_gaps': [],
                    'recommendations': []
                }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating knowledge with SCKIPIT: {str(e)}")
            return {'is_valid': False, 'validation_score': 0.0, 'confidence': 0.0}
    
    async def _assess_quality_with_sckipit(self, proposal_data: Dict, features: Dict) -> Dict[str, Any]:
        """Assess quality using SCKIPIT models"""
        try:
            # Extract quality features
            quality_features = await self._extract_quality_features(proposal_data, features)
            
            # Use SCKIPIT quality assessor
            if 'quality_assessor' in self.sckipit_models:
                X = np.array([list(quality_features.values())])
                quality_score = self.sckipit_models['quality_assessor'].predict_proba(X)[0][1]
                
                quality_assessment = {
                    'quality_score': float(quality_score),
                    'quality_level': await self._classify_quality_level(quality_score),
                    'strengths': await self._identify_quality_strengths(quality_features),
                    'weaknesses': await self._identify_quality_weaknesses(quality_features),
                    'improvement_suggestions': await self._generate_quality_improvements(quality_score, quality_features)
                }
            else:
                quality_assessment = {
                    'quality_score': 0.7,
                    'quality_level': 'medium',
                    'strengths': [],
                    'weaknesses': [],
                    'improvement_suggestions': []
                }
            
            return quality_assessment
            
        except Exception as e:
            logger.error(f"Error assessing quality with SCKIPIT: {str(e)}")
            return {'quality_score': 0.5, 'quality_level': 'unknown'}
    
    async def _extract_pattern_features(self, features: Dict, ai_type: str) -> Dict[str, float]:
        """Extract features for pattern analysis"""
        try:
            return {
                'feature_count': len(features),
                'complexity_score': features.get('complexity', 0.0),
                'error_frequency': features.get('error_count', 0) / max(1, features.get('total_attempts', 1)),
                'learning_rate': features.get('learning_rate', 0.0),
                'improvement_potential': features.get('improvement_potential', 0.0),
                'ai_type_encoded': hash(ai_type) % 10 / 10.0,
                'code_quality': features.get('code_quality', 0.0),
                'test_coverage': features.get('test_coverage', 0.0),
                'documentation_quality': features.get('documentation_quality', 0.0),
                'performance_score': features.get('performance_score', 0.0)
            }
        except Exception as e:
            logger.error(f"Error extracting pattern features: {str(e)}")
            return {'feature_count': 0.0, 'complexity_score': 0.0, 'error_frequency': 0.0}
    
    async def _extract_validation_features(self, test_summary: str, proposal_data: Dict) -> Dict[str, float]:
        """Extract features for knowledge validation"""
        try:
            return {
                'summary_length': len(test_summary),
                'error_count': test_summary.lower().count('error'),
                'warning_count': test_summary.lower().count('warning'),
                'success_indicators': test_summary.lower().count('success') + test_summary.lower().count('pass'),
                'code_complexity': proposal_data.get('complexity', 0.0),
                'test_coverage': proposal_data.get('test_coverage', 0.0),
                'documentation_score': proposal_data.get('documentation_quality', 0.0),
                'performance_metrics': proposal_data.get('performance_score', 0.0),
                'security_score': proposal_data.get('security_score', 0.0),
                'maintainability_score': proposal_data.get('maintainability_score', 0.0)
            }
        except Exception as e:
            logger.error(f"Error extracting validation features: {str(e)}")
            return {'summary_length': 0.0, 'error_count': 0.0, 'warning_count': 0.0}
    
    async def _extract_quality_features(self, proposal_data: Dict, features: Dict) -> Dict[str, float]:
        """Extract features for quality assessment"""
        try:
            return {
                'code_quality': features.get('code_quality', 0.0),
                'test_coverage': features.get('test_coverage', 0.0),
                'documentation_quality': features.get('documentation_quality', 0.0),
                'performance_score': features.get('performance_score', 0.0),
                'security_score': features.get('security_score', 0.0),
                'maintainability_score': features.get('maintainability_score', 0.0),
                'complexity_score': features.get('complexity', 0.0),
                'error_rate': features.get('error_count', 0) / max(1, features.get('total_attempts', 1)),
                'improvement_potential': features.get('improvement_potential', 0.0),
                'learning_efficiency': features.get('learning_rate', 0.0)
            }
        except Exception as e:
            logger.error(f"Error extracting quality features: {str(e)}")
            return {'code_quality': 0.0, 'test_coverage': 0.0, 'documentation_quality': 0.0}
    
    async def _generate_sckipit_enhanced_improvements(self, features: Dict, pattern_analysis: Dict, knowledge_validation: Dict) -> List[str]:
        """Generate SCKIPIT-enhanced improvement suggestions"""
        try:
            improvements = []
            
            # Pattern-based improvements
            if pattern_analysis.get('improvement_areas'):
                improvements.extend(pattern_analysis['improvement_areas'])
            
            # Knowledge validation improvements
            if not knowledge_validation.get('is_valid', True):
                improvements.append("Address knowledge gaps identified in validation")
            
            # Quality-based improvements
            if knowledge_validation.get('validation_score', 1.0) < 0.8:
                improvements.append("Improve code quality and testing coverage")
            
            # SCKIPIT-specific recommendations
            if pattern_analysis.get('recommendations'):
                improvements.extend(pattern_analysis['recommendations'])
            
            # Add general SCKIPIT improvements
            improvements.extend([
                "Implement SCKIPIT best practices for code quality",
                "Use SCKIPIT pattern recognition for better learning",
                "Apply SCKIPIT knowledge validation techniques",
                "Follow SCKIPIT quality assessment guidelines"
            ])
            
            return list(set(improvements))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error generating SCKIPIT-enhanced improvements: {str(e)}")
            return ["Apply general improvement practices"]
    
    async def _update_sckipit_learning_insights(self, learning_record: Dict):
        """Update SCKIPIT learning insights with new data"""
        try:
            # Add to SCKIPIT-enhanced data
            self.sckipit_enhanced_data.append(learning_record)
            
            # Update pattern recognition results
            if learning_record.get('sckipit_patterns'):
                self.pattern_recognition_results.append(learning_record['sckipit_patterns'])
            
            # Update knowledge validation history
            if learning_record.get('sckipit_validation'):
                self.knowledge_validation_history.append(learning_record['sckipit_validation'])
            
            # Keep only recent data to prevent memory issues
            max_records = 100
            if len(self.sckipit_enhanced_data) > max_records:
                self.sckipit_enhanced_data = self.sckipit_enhanced_data[-max_records:]
                self.pattern_recognition_results = self.pattern_recognition_results[-max_records:]
                self.knowledge_validation_history = self.knowledge_validation_history[-max_records:]
            
        except Exception as e:
            logger.error(f"Error updating SCKIPIT learning insights: {str(e)}")
    
    async def _train_enhanced_failure_predictor_with_sckipit(self):
        """Train enhanced failure predictor with SCKIPIT integration"""
        try:
            if len(self._learning_data) < 10:
                return
            
            # Prepare training data with SCKIPIT features
            X = []
            y = []
            
            for record in self._learning_data:
                features = record.get('features', {})
                sckipit_patterns = record.get('sckipit_patterns', {})
                sckipit_validation = record.get('sckipit_validation', {})
                sckipit_quality = record.get('sckipit_quality', {})
                
                # Combine regular features with SCKIPIT features
                combined_features = list(features.values())
                combined_features.extend([
                    sckipit_patterns.get('learning_potential', 0.0),
                    sckipit_validation.get('validation_score', 0.0),
                    sckipit_quality.get('quality_score', 0.0),
                    sckipit_patterns.get('complexity_level', 0.5)
                ])
                
                X.append(combined_features)
                y.append(1 if record.get('outcome') == 'failure' else 0)
            
            if len(X) >= 10:
                # Train the enhanced model
                self._ml_models['failure_predictor'].fit(X, y)
                logger.info("Enhanced failure predictor with SCKIPIT trained successfully")
                
        except Exception as e:
            logger.error(f"Error training enhanced failure predictor with SCKIPIT: {str(e)}")
    
    async def _update_enhanced_ai_learning_state_with_sckipit(self, ai_type: str, learning_event: str, improvements: List[str], failure_features: Dict, pattern_analysis: Dict):
        """Update AI learning state with SCKIPIT insights"""
        try:
            if ai_type not in self._learning_states:
                self._learning_states[ai_type] = {
                    'learning_events': [],
                    'improvements_learned': [],
                    'failure_patterns': [],
                    'success_patterns': [],
                    'productivity_metrics': {},
                    'sckipit_insights': {},
                    'last_learning': None
                }
            
            # Calculate enhanced productivity metrics with SCKIPIT
            productivity_score = await self._calculate_improvement_productivity_score(improvements)
            ml_confidence = await self._calculate_ml_confidence(failure_features)
            sckipit_confidence = pattern_analysis.get('learning_potential', 0.0)
            
            # Enhanced learning event with SCKIPIT data
            learning_event_data = {
                'timestamp': datetime.now().isoformat(),
                'event': learning_event,
                'improvements': improvements,
                'productivity_score': productivity_score,
                'ml_confidence': ml_confidence,
                'sckipit_confidence': sckipit_confidence,
                'pattern_analysis': pattern_analysis,
                'enhanced_learning': True
            }
            
            self._learning_states[ai_type]['learning_events'].append(learning_event_data)
            self._learning_states[ai_type]['improvements_learned'].extend(improvements)
            self._learning_states[ai_type]['sckipit_insights'] = pattern_analysis
            self._learning_states[ai_type]['last_learning'] = datetime.now().isoformat()
            
            logger.info(f"Enhanced AI learning state updated with SCKIPIT for {ai_type}")
            
        except Exception as e:
            logger.error(f"Error updating enhanced AI learning state with SCKIPIT: {str(e)}")
    
    # ==================== SCKIPIT HELPER METHODS ====================
    
    async def _classify_pattern_type(self, cluster_id: int, features: Dict) -> str:
        """Classify pattern type based on cluster and features"""
        try:
            pattern_types = {
                0: "simple_learning",
                1: "complex_learning", 
                2: "error_recovery",
                3: "quality_improvement",
                4: "performance_optimization",
                5: "knowledge_gap_filling"
            }
            return pattern_types.get(int(cluster_id), "unknown_pattern")
        except Exception as e:
            logger.error(f"Error classifying pattern type: {str(e)}")
            return "unknown_pattern"
    
    async def _assess_pattern_complexity(self, features: Dict) -> str:
        """Assess pattern complexity level"""
        try:
            complexity_score = features.get('complexity_score', 0.0)
            if complexity_score > 0.8:
                return "high"
            elif complexity_score > 0.5:
                return "medium"
            else:
                return "low"
        except Exception as e:
            logger.error(f"Error assessing pattern complexity: {str(e)}")
            return "medium"
    
    async def _calculate_learning_potential(self, features: Dict) -> float:
        """Calculate learning potential based on features"""
        try:
            # Weighted combination of features
            weights = {
                'improvement_potential': 0.3,
                'learning_rate': 0.25,
                'error_frequency': 0.2,
                'complexity_score': 0.15,
                'feature_count': 0.1
            }
            
            potential = 0.0
            for feature, weight in weights.items():
                potential += features.get(feature, 0.0) * weight
            
            return min(1.0, max(0.0, potential))
        except Exception as e:
            logger.error(f"Error calculating learning potential: {str(e)}")
            return 0.5
    
    async def _identify_improvement_areas(self, features: Dict) -> List[str]:
        """Identify areas for improvement based on features"""
        try:
            improvements = []
            
            if features.get('error_frequency', 0.0) > 0.3:
                improvements.append("Reduce error frequency through better testing")
            
            if features.get('complexity_score', 0.0) > 0.8:
                improvements.append("Simplify code complexity for better maintainability")
            
            if features.get('learning_rate', 0.0) < 0.3:
                improvements.append("Improve learning rate through better documentation")
            
            if features.get('improvement_potential', 0.0) > 0.7:
                improvements.append("Focus on high-potential improvement areas")
            
            return improvements
        except Exception as e:
            logger.error(f"Error identifying improvement areas: {str(e)}")
            return ["Apply general improvement practices"]
    
    async def _generate_pattern_recommendations(self, cluster_id: int, features: Dict) -> List[str]:
        """Generate recommendations based on pattern cluster"""
        try:
            recommendations = []
            
            if cluster_id == 0:  # Simple learning
                recommendations.extend([
                    "Focus on basic concepts and fundamentals",
                    "Build strong foundation before advanced topics",
                    "Use step-by-step learning approach"
                ])
            elif cluster_id == 1:  # Complex learning
                recommendations.extend([
                    "Break down complex problems into smaller parts",
                    "Use systematic problem-solving approach",
                    "Apply design patterns and best practices"
                ])
            elif cluster_id == 2:  # Error recovery
                recommendations.extend([
                    "Implement comprehensive error handling",
                    "Add logging and debugging capabilities",
                    "Use defensive programming techniques"
                ])
            elif cluster_id == 3:  # Quality improvement
                recommendations.extend([
                    "Focus on code quality and readability",
                    "Implement comprehensive testing",
                    "Follow coding standards and conventions"
                ])
            elif cluster_id == 4:  # Performance optimization
                recommendations.extend([
                    "Profile and identify performance bottlenecks",
                    "Optimize algorithms and data structures",
                    "Use caching and efficient resource management"
                ])
            elif cluster_id == 5:  # Knowledge gap filling
                recommendations.extend([
                    "Identify and fill knowledge gaps",
                    "Study related concepts and technologies",
                    "Practice with real-world examples"
                ])
            
            return recommendations
        except Exception as e:
            logger.error(f"Error generating pattern recommendations: {str(e)}")
            return ["Apply general best practices"]
    
    async def _identify_knowledge_gaps(self, features: Dict) -> List[str]:
        """Identify knowledge gaps based on validation features"""
        try:
            gaps = []
            
            if features.get('error_count', 0) > 5:
                gaps.append("Error handling and debugging knowledge")
            
            if features.get('test_coverage', 0.0) < 0.7:
                gaps.append("Testing and quality assurance knowledge")
            
            if features.get('documentation_score', 0.0) < 0.6:
                gaps.append("Documentation and communication skills")
            
            if features.get('security_score', 0.0) < 0.8:
                gaps.append("Security best practices knowledge")
            
            if features.get('maintainability_score', 0.0) < 0.7:
                gaps.append("Code maintainability and architecture knowledge")
            
            return gaps
        except Exception as e:
            logger.error(f"Error identifying knowledge gaps: {str(e)}")
            return ["General knowledge gaps"]
    
    async def _generate_validation_recommendations(self, validation_score: float, test_summary: str) -> List[str]:
        """Generate recommendations based on validation score"""
        try:
            recommendations = []
            
            if validation_score < 0.5:
                recommendations.extend([
                    "Review and improve code quality",
                    "Add comprehensive testing",
                    "Improve documentation and comments",
                    "Follow coding standards"
                ])
            elif validation_score < 0.8:
                recommendations.extend([
                    "Minor improvements to code quality",
                    "Add more test coverage",
                    "Improve error handling"
                ])
            else:
                recommendations.extend([
                    "Maintain current quality standards",
                    "Continue with best practices",
                    "Share knowledge with team"
                ])
            
            return recommendations
        except Exception as e:
            logger.error(f"Error generating validation recommendations: {str(e)}")
            return ["Apply general improvement practices"]
    
    async def _classify_quality_level(self, quality_score: float) -> str:
        """Classify quality level based on score"""
        try:
            if quality_score >= 0.9:
                return "excellent"
            elif quality_score >= 0.8:
                return "good"
            elif quality_score >= 0.7:
                return "acceptable"
            elif quality_score >= 0.6:
                return "needs_improvement"
            else:
                return "poor"
        except Exception as e:
            logger.error(f"Error classifying quality level: {str(e)}")
            return "unknown"
    
    async def _identify_quality_strengths(self, features: Dict) -> List[str]:
        """Identify quality strengths based on features"""
        try:
            strengths = []
            
            if features.get('code_quality', 0.0) > 0.8:
                strengths.append("High code quality")
            
            if features.get('test_coverage', 0.0) > 0.8:
                strengths.append("Comprehensive test coverage")
            
            if features.get('documentation_quality', 0.0) > 0.8:
                strengths.append("Excellent documentation")
            
            if features.get('performance_score', 0.0) > 0.8:
                strengths.append("Good performance")
            
            if features.get('security_score', 0.0) > 0.8:
                strengths.append("Strong security practices")
            
            return strengths
        except Exception as e:
            logger.error(f"Error identifying quality strengths: {str(e)}")
            return []
    
    async def _identify_quality_weaknesses(self, features: Dict) -> List[str]:
        """Identify quality weaknesses based on features"""
        try:
            weaknesses = []
            
            if features.get('code_quality', 0.0) < 0.7:
                weaknesses.append("Code quality needs improvement")
            
            if features.get('test_coverage', 0.0) < 0.7:
                weaknesses.append("Insufficient test coverage")
            
            if features.get('documentation_quality', 0.0) < 0.7:
                weaknesses.append("Documentation needs improvement")
            
            if features.get('performance_score', 0.0) < 0.7:
                weaknesses.append("Performance optimization needed")
            
            if features.get('security_score', 0.0) < 0.7:
                weaknesses.append("Security practices need improvement")
            
            return weaknesses
        except Exception as e:
            logger.error(f"Error identifying quality weaknesses: {str(e)}")
            return []
    
    async def _generate_quality_improvements(self, quality_score: float, features: Dict) -> List[str]:
        """Generate quality improvement suggestions"""
        try:
            improvements = []
            
            if quality_score < 0.8:
                improvements.extend([
                    "Implement code review process",
                    "Add automated testing",
                    "Improve documentation standards",
                    "Follow coding conventions",
                    "Add performance monitoring"
                ])
            
            if features.get('code_quality', 0.0) < 0.8:
                improvements.append("Refactor code for better quality")
            
            if features.get('test_coverage', 0.0) < 0.8:
                improvements.append("Increase test coverage")
            
            if features.get('documentation_quality', 0.0) < 0.8:
                improvements.append("Improve documentation")
            
            return improvements
        except Exception as e:
            logger.error(f"Error generating quality improvements: {str(e)}")
            return ["Apply general quality improvement practices"]
    
    async def _calculate_validation_confidence(self, features: Dict) -> float:
        """Calculate validation confidence based on features"""
        try:
            # Weighted combination of validation features
            weights = {
                'summary_length': 0.1,
                'error_count': 0.2,
                'warning_count': 0.15,
                'success_indicators': 0.25,
                'code_complexity': 0.1,
                'test_coverage': 0.2
            }
            
            confidence = 0.0
            for feature, weight in weights.items():
                normalized_value = min(1.0, features.get(feature, 0.0) / 100.0)  # Normalize to 0-1
                confidence += normalized_value * weight
            
            return min(1.0, max(0.0, confidence))
        except Exception as e:
            logger.error(f"Error calculating validation confidence: {str(e)}")
            return 0.5
    
    def _load_existing_models(self):
        """Load existing trained models"""
        model_files = {
            'proposal_quality_predictor': 'ai_proposal_quality_predictor.pkl',
            'failure_predictor': 'ai_failure_predictor.pkl',
            'improvement_recommender': 'ai_improvement_recommender.pkl',
            'code_quality_analyzer': 'ai_code_quality_analyzer.pkl',
            'productivity_predictor': 'ai_productivity_predictor.pkl',
            'proposal_clusterer': 'ai_proposal_clusterer.pkl'
        }
        
        for model_name, filename in model_files.items():
            model_path = os.path.join(settings.ml_model_path, filename)
            if os.path.exists(model_path):
                try:
                    with open(model_path, 'rb') as f:
                        self._ml_models[model_name] = pickle.load(f)
                    logger.info(f"Loaded ENHANCED AI learning model: {model_name}")
                except Exception as e:
                    logger.error(f"Failed to load model {filename}: {str(e)}")
    
    async def _save_learning_model(self, model_name: str):
        """Save a trained learning model"""
        try:
            model_path = os.path.join(settings.ml_model_path, f"ai_{model_name}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(self._ml_models[model_name], f)
            logger.info(f"Saved ENHANCED AI learning model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to save model {model_name}: {str(e)}")
    
    async def learn_from_failure(self, proposal_id: str, test_summary: str, ai_type: str, proposal_data: Dict):
        """Learn from test failures using ENHANCED scikit-learn for better proposal improvement"""
        try:
            logger.info(f"Learning from failure for proposal {proposal_id} with ENHANCED ML")
            
            # Extract ENHANCED features from the failure
            failure_features = await self._extract_enhanced_failure_features(proposal_data, test_summary, ai_type)
            
            # Add to learning data with productivity tracking
            learning_record = {
                'timestamp': datetime.now().isoformat(),
                'proposal_id': proposal_id,
                'ai_type': ai_type,
                'failure_type': await self._classify_failure_type(test_summary),
                'features': failure_features,
                'test_summary': test_summary,
                'outcome': 'failure',
                'productivity_impact': await self._calculate_productivity_impact(failure_features, ai_type),
                'ml_confidence': await self._calculate_ml_confidence(failure_features),
                'learning_value': await self._calculate_learning_value_from_failure(failure_features, ai_type)
            }
            
            self._learning_data.append(learning_record)
            
            # Train ENHANCED failure prediction model
            await self._train_enhanced_failure_predictor()
            
            # Generate ENHANCED improvements based on ML analysis
            improvements = await self._generate_enhanced_ml_improvements(failure_features, ai_type, proposal_data)
            
            # Track proposal improvement history
            await self._track_proposal_improvement(proposal_id, improvements, ai_type)
            
            # Update AI learning state with productivity metrics
            await self._update_enhanced_ai_learning_state(ai_type, 'failure_learned', improvements, failure_features)
            
            # Update analytics with failure learning
            await self._update_failure_learning_analytics(ai_type, failure_features, improvements)
            
            # Save learning model after failure
            await self._save_learning_model('failure_predictor')
            
            # After learning, ask Claude for verification and new sources
            try:
                verification = await anthropic_rate_limited_call(
                    f"{ai_type} AI learned from failure in proposal {proposal_id}. Test summary: {test_summary}. What is your feedback? Where else should this AI learn from to improve in its area?",
                    ai_name=ai_type.lower()
                )
                # If Claude suggests new sources, add them (simple keyword check)
                if "learn from" in verification.lower() or "source" in verification.lower():
                    # Extract sources (very basic, real code should parse more robustly)
                    new_sources = []
                    for line in verification.split('\n'):
                        if "http" in line or "source" in line.lower():
                            new_sources.append(line.strip())
                    if new_sources:
                        # Assume a method self.add_learning_sources exists
                        await self.add_learning_sources(ai_type, new_sources)
            except Exception as e:
                verification = f"Claude verification error: {str(e)}"
            return {"status": "success", "verification": verification}
        except Exception as e:
            logger.error(f"Error in learn_from_failure: {str(e)}")
            # Claude failure analysis
            try:
                advice = await anthropic_rate_limited_call(
                    f"{ai_type} AI failed to learn from failure in proposal {proposal_id}. Error: {str(e)}. Please analyze and suggest how to improve.",
                    ai_name=ai_type.lower()
                )
            except Exception as ce:
                advice = f"Claude error: {str(ce)}"
            return {"status": "error", "message": str(e), "claude_advice": advice}
    
    async def _extract_enhanced_failure_features(self, proposal_data: Dict, test_summary: str, ai_type: str) -> Dict[str, Any]:
        """Extract ENHANCED features from failure for better ML analysis"""
        features = {}
        
        # Code-based features (Enhanced)
        code_after = proposal_data.get('code_after', '')
        code_before = proposal_data.get('code_before', '')
        
        features['code_length'] = len(code_after)
        features['code_changes'] = len(code_after) - len(code_before)
        features['change_ratio'] = features['code_changes'] / max(len(code_before), 1)
        features['file_type'] = proposal_data.get('file_path', '').split('.')[-1] if '.' in proposal_data.get('file_path', '') else 'unknown'
        
        # Enhanced code quality features
        features['complexity_score'] = await self._calculate_code_complexity(code_after)
        features['readability_score'] = await self._calculate_readability_score(code_after)
        features['maintainability_score'] = await self._calculate_maintainability_score(code_after)
        
        # AI type encoding (Enhanced)
        ai_type_encoding = {'imperium': 0, 'guardian': 1, 'sandbox': 2, 'conquest': 3}
        features['ai_type_encoded'] = ai_type_encoding.get(ai_type.lower(), 0)
        
        # Enhanced test failure analysis
        features['failure_keywords'] = await self._extract_failure_keywords(test_summary)
        features['failure_severity'] = await self._calculate_failure_severity(test_summary)
        features['failure_complexity'] = await self._calculate_failure_complexity(test_summary)
        
        # Time-based features (Enhanced)
        features['hour_of_day'] = datetime.now().hour
        features['day_of_week'] = datetime.now().weekday()
        features['time_since_last_failure'] = await self._get_time_since_last_failure(ai_type)
        
        # Productivity features
        features['proposal_quality_score'] = await self._calculate_proposal_quality_score(proposal_data)
        features['improvement_potential'] = await self._calculate_improvement_potential(proposal_data)
        
        return features
    
    async def _calculate_code_complexity(self, code: str) -> float:
        """Calculate code complexity score"""
        if not code:
            return 0.0
        
        lines = code.split('\n')
        complexity_score = 0.0
        
        for line in lines:
            line = line.strip()
            if line:
                # Count complexity indicators
                if any(keyword in line for keyword in ['if ', 'for ', 'while ', 'try:', 'except:', 'class ', 'def ']):
                    complexity_score += 1
                if line.count('(') > 2 or line.count(')') > 2:
                    complexity_score += 0.5
                if len(line) > 80:
                    complexity_score += 0.3
        
        return min(10.0, complexity_score / max(len(lines), 1))
    
    async def _calculate_readability_score(self, code: str) -> float:
        """Calculate code readability score"""
        if not code:
            return 0.0
        
        lines = code.split('\n')
        readability_score = 10.0  # Start with perfect score
        
        for line in lines:
            line = line.strip()
            if line:
                # Penalize for poor readability
                if len(line) > 120:
                    readability_score -= 0.5
                if line.count('_') > 5:
                    readability_score -= 0.3
                if any(keyword in line for keyword in ['TODO', 'FIXME', 'HACK']):
                    readability_score -= 0.2
        
        return max(0.0, readability_score)
    
    async def _calculate_maintainability_score(self, code: str) -> float:
        """Calculate code maintainability score"""
        if not code:
            return 0.0
        
        maintainability_score = 10.0
        
        # Check for maintainability issues
        if 'TODO' in code or 'FIXME' in code:
            maintainability_score -= 2.0
        if code.count('import *') > 0:
            maintainability_score -= 1.0
        if code.count('global ') > 2:
            maintainability_score -= 1.5
        
        return max(0.0, maintainability_score)
    
    async def _classify_failure_type(self, test_summary: str) -> str:
        """Classify the type of failure using ML"""
        failure_keywords = {
            'syntax': ['syntax', 'parse', 'indentation', 'missing'],
            'runtime': ['runtime', 'exception', 'error', 'crash'],
            'logic': ['logic', 'incorrect', 'wrong', 'bug'],
            'performance': ['timeout', 'slow', 'performance', 'memory'],
            'security': ['security', 'vulnerability', 'unsafe', 'injection']
        }
        
        test_lower = test_summary.lower()
        for failure_type, keywords in failure_keywords.items():
            if any(keyword in test_lower for keyword in keywords):
                return failure_type
        
        return 'unknown'
    
    async def _extract_failure_keywords(self, test_summary: str) -> int:
        """Extract number of failure-related keywords"""
        failure_keywords = ['error', 'fail', 'exception', 'timeout', 'crash', 'bug', 'invalid']
        test_lower = test_summary.lower()
        return sum(1 for keyword in failure_keywords if keyword in test_lower)
    
    async def _calculate_failure_severity(self, test_summary: str) -> float:
        """Calculate failure severity score"""
        severity_keywords = {
            'critical': ['critical', 'fatal', 'crash', 'timeout'],
            'high': ['error', 'exception', 'fail'],
            'medium': ['warning', 'deprecated'],
            'low': ['info', 'note']
        }
        
        test_lower = test_summary.lower()
        severity_score = 0.0
        
        for level, keywords in severity_keywords.items():
            if any(keyword in test_lower for keyword in keywords):
                if level == 'critical':
                    severity_score = 1.0
                elif level == 'high':
                    severity_score = 0.8
                elif level == 'medium':
                    severity_score = 0.5
                elif level == 'low':
                    severity_score = 0.2
        
        return severity_score
    
    async def _calculate_failure_complexity(self, test_summary: str) -> float:
        """Calculate failure complexity score"""
        complexity_indicators = [
            'stack trace', 'traceback', 'exception', 'error', 'failed',
            'timeout', 'memory', 'performance', 'deadlock', 'race condition'
        ]
        
        test_lower = test_summary.lower()
        complexity_score = 0.0
        
        for indicator in complexity_indicators:
            if indicator in test_lower:
                complexity_score += 1.0
        
        return min(10.0, complexity_score)
    
    async def _get_time_since_last_failure(self, ai_type: str) -> float:
        """Get time since last failure for this AI type"""
        try:
            # Find last failure for this AI type
            recent_failures = [record for record in self._learning_data[-50:] 
                             if record.get('ai_type') == ai_type and record.get('outcome') == 'failure']
            
            if recent_failures:
                last_failure_time = datetime.fromisoformat(recent_failures[-1]['timestamp'])
                time_diff = (datetime.now() - last_failure_time).total_seconds()
                return time_diff / 3600  # Return hours
            else:
                return 24.0  # Default to 24 hours
        except Exception:
            return 24.0
    
    async def _calculate_proposal_quality_score(self, proposal_data: Dict) -> float:
        """Calculate proposal quality score"""
        quality_score = 5.0  # Base score
        
        code_after = proposal_data.get('code_after', '')
        code_before = proposal_data.get('code_before', '')
        
        # Quality indicators
        if len(code_after) > len(code_before):
            quality_score += 1.0  # Code addition is good
        
        if 'TODO' not in code_after and 'FIXME' not in code_after:
            quality_score += 1.0  # No incomplete code
        
        if code_after.count('def ') > 0 or code_after.count('class ') > 0:
            quality_score += 1.0  # Has structure
        
        if code_after.count('import ') > 0:
            quality_score += 0.5  # Has imports
        
        return min(10.0, quality_score)
    
    async def _calculate_improvement_potential(self, proposal_data: Dict) -> float:
        """Calculate improvement potential score"""
        potential_score = 0.0
        
        code_after = proposal_data.get('code_after', '')
        
        # Improvement opportunities
        if 'TODO' in code_after or 'FIXME' in code_after:
            potential_score += 2.0
        
        if code_after.count('print(') > 3:
            potential_score += 1.0  # Too many prints
        
        if len(code_after.split('\n')) > 50:
            potential_score += 1.0  # Long function
        
        if code_after.count('global ') > 0:
            potential_score += 1.0  # Global variables
        
        return min(10.0, potential_score)
    
    async def _calculate_productivity_impact(self, failure_features: Dict, ai_type: str) -> float:
        """Calculate productivity impact of the failure"""
        impact_score = 0.0
        
        # Factors affecting productivity
        severity = failure_features.get('failure_severity', 0)
        complexity = failure_features.get('failure_complexity', 0)
        time_since_last = failure_features.get('time_since_last_failure', 24)
        
        # Higher severity and complexity = higher impact
        impact_score += severity * 3.0
        impact_score += complexity * 2.0
        
        # Recent failures have higher impact
        if time_since_last < 1:  # Less than 1 hour
            impact_score += 2.0
        elif time_since_last < 6:  # Less than 6 hours
            impact_score += 1.0
        
        return min(10.0, impact_score)
    
    async def _calculate_ml_confidence(self, failure_features: Dict) -> float:
        """Calculate ML model confidence for the prediction"""
        try:
            # Use feature quality to estimate confidence
            feature_quality = 0.0
            
            # More features = higher confidence
            non_zero_features = sum(1 for v in failure_features.values() if v != 0)
            feature_quality += min(1.0, non_zero_features / 10.0)
            
            # Higher severity = more confident prediction
            severity = failure_features.get('failure_severity', 0)
            feature_quality += severity * 0.3
            
            # Recent data = higher confidence
            if len(self._learning_data) > 50:
                feature_quality += 0.2
            
            return min(1.0, feature_quality)
        except Exception:
            return 0.5  # Default confidence
    
    async def _train_enhanced_failure_predictor(self):
        """Train the ENHANCED failure prediction model using scikit-learn"""
        if len(self._learning_data) < 20:  # Need more data for enhanced model
            logger.info("Insufficient data for training ENHANCED failure predictor")
            return
        
        try:
            # Prepare training data
            df = pd.DataFrame(self._learning_data)
            
            # Extract ENHANCED features
            feature_columns = [
                'code_length', 'code_changes', 'change_ratio', 'ai_type_encoded',
                'failure_keywords', 'failure_severity', 'failure_complexity',
                'hour_of_day', 'day_of_week', 'time_since_last_failure',
                'complexity_score', 'readability_score', 'maintainability_score',
                'proposal_quality_score', 'improvement_potential'
            ]
            
            # Handle missing values
            X = df[feature_columns].fillna(0)
            y = (df['outcome'] == 'failure').astype(int)
            
            # Feature scaling for better performance
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
            
            # Train ENHANCED model with cross-validation
            model = self._ml_models['failure_predictor']
            
            # Use GridSearchCV for hyperparameter tuning
            param_grid = {
                'n_estimators': [100, 150, 200],
                'learning_rate': [0.05, 0.1, 0.15],
                'max_depth': [6, 8, 10]
            }
            
            grid_search = GridSearchCV(model, param_grid, cv=3, scoring='neg_mean_squared_error')
            grid_search.fit(X_train, y_train)
            
            # Use best model
            self._ml_models['failure_predictor'] = grid_search.best_estimator_
            
            # Evaluate
            y_pred = self._ml_models['failure_predictor'].predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Calculate precision, recall, F1
            y_pred_binary = (y_pred > 0.5).astype(int)
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred_binary, average='binary')
            
            logger.info(f"Trained ENHANCED failure predictor", 
                       mse=mse, r2=r2, precision=precision, recall=recall, f1=f1,
                       training_samples=len(X_train), best_params=grid_search.best_params_)
            
            # Save model
            await self._save_learning_model('failure_predictor')
            
        except Exception as e:
            logger.error(f"Error training ENHANCED failure predictor: {str(e)}")
    
    async def _generate_enhanced_ml_improvements(self, failure_features: Dict, ai_type: str, proposal_data: Dict) -> List[str]:
        """Generate ENHANCED improvements based on advanced ML analysis"""
        improvements = []
        
        try:
            # Analyze failure patterns with ML insights
            severity = failure_features.get('failure_severity', 0)
            complexity = failure_features.get('failure_complexity', 0)
            code_quality = failure_features.get('maintainability_score', 0)
            readability = failure_features.get('readability_score', 0)
            
            # High severity failures
            if severity > 0.8:
                improvements.append("CRITICAL: Implement comprehensive error handling and validation")
                improvements.append("Add defensive programming practices to prevent similar failures")
            
            # Code quality improvements
            if code_quality < 7.0:
                improvements.append("Improve code maintainability by reducing complexity and adding documentation")
                improvements.append("Refactor code to follow SOLID principles")
            
            if readability < 7.0:
                improvements.append("Enhance code readability with better variable names and structure")
                improvements.append("Break down complex functions into smaller, focused methods")
            
            # AI-specific ENHANCED improvements
            if ai_type.lower() == 'imperium':
                improvements.append("Imperium: Implement system-level error recovery and monitoring")
                improvements.append("Add comprehensive logging and metrics collection")
                improvements.append("Enhance orchestration capabilities with better error handling")
            elif ai_type.lower() == 'guardian':
                improvements.append("Guardian: Strengthen security validation and input sanitization")
                improvements.append("Implement comprehensive security testing and vulnerability scanning")
                improvements.append("Add code quality gates and automated security checks")
            elif ai_type.lower() == 'sandbox':
                improvements.append("Sandbox: Improve experimental approach with better error isolation")
                improvements.append("Add comprehensive testing framework for experimental features")
                improvements.append("Implement rollback mechanisms for failed experiments")
            elif ai_type.lower() == 'conquest':
                improvements.append("Conquest: Enhance app development patterns and user experience")
                improvements.append("Implement comprehensive UI/UX testing and validation")
                improvements.append("Add performance monitoring and optimization")
            
            # Code-specific ENHANCED improvements
            if failure_features.get('code_changes', 0) > 100:
                improvements.append("Large changes detected: Implement incremental development approach")
                improvements.append("Add comprehensive testing for large code changes")
            
            if failure_features.get('file_type') in ['py', 'dart', 'js']:
                improvements.append(f"Language-specific improvements for {failure_features.get('file_type')} files")
                improvements.append(f"Follow {failure_features.get('file_type')} best practices and conventions")
            
            # ML-based recommendations
            if complexity > 5.0:
                improvements.append("High complexity detected: Simplify code structure and logic")
                improvements.append("Break down complex operations into smaller, testable functions")
            
            if failure_features.get('failure_keywords', 0) > 3:
                improvements.append("Multiple failure indicators: Implement comprehensive debugging approach")
                improvements.append("Add detailed logging and error tracking")
            
        except Exception as e:
            logger.error(f"Error generating ENHANCED ML-based improvements: {str(e)}")
            improvements.append("Apply standard debugging and testing practices")
        
        return improvements
    
    async def _track_proposal_improvement(self, proposal_id: str, improvements: List[str], ai_type: str):
        """Track proposal improvement history for productivity analysis"""
        improvement_record = {
            'proposal_id': proposal_id,
            'ai_type': ai_type,
            'improvements': improvements,
            'timestamp': datetime.now().isoformat(),
            'improvement_count': len(improvements),
            'productivity_score': await self._calculate_improvement_productivity_score(improvements)
        }
        
        self._proposal_improvement_history.append(improvement_record)
        
        # Keep only recent history
        if len(self._proposal_improvement_history) > 1000:
            self._proposal_improvement_history = self._proposal_improvement_history[-500:]
    
    async def _calculate_improvement_productivity_score(self, improvements: List[str]) -> float:
        """Calculate productivity score for improvements"""
        productivity_score = 0.0
        
        for improvement in improvements:
            # Score based on improvement type
            if 'CRITICAL' in improvement:
                productivity_score += 3.0
            elif 'Implement' in improvement:
                productivity_score += 2.0
            elif 'Add' in improvement or 'Enhance' in improvement:
                productivity_score += 1.5
            elif 'Improve' in improvement:
                productivity_score += 1.0
            else:
                productivity_score += 0.5
        
        return min(10.0, productivity_score)
    
    async def _update_enhanced_ai_learning_state(self, ai_type: str, learning_event: str, improvements: List[str], failure_features: Dict):
        """Update AI learning state with ENHANCED productivity tracking"""
        if ai_type not in self._learning_states:
            self._learning_states[ai_type] = {
                'learning_events': [],
                'improvements_learned': [],
                'failure_patterns': [],
                'success_patterns': [],
                'productivity_metrics': {},
                'last_learning': None
            }
        
        # Calculate productivity metrics
        productivity_score = await self._calculate_improvement_productivity_score(improvements)
        ml_confidence = await self._calculate_ml_confidence(failure_features)
        
        self._learning_states[ai_type]['learning_events'].append({
            'timestamp': datetime.now().isoformat(),
            'event': learning_event,
            'improvements': improvements,
            'productivity_score': productivity_score,
            'ml_confidence': ml_confidence
        })
        
        self._learning_states[ai_type]['improvements_learned'].extend(improvements)
        self._learning_states[ai_type]['last_learning'] = datetime.now().isoformat()
        
        # Update productivity metrics
        if 'productivity_metrics' not in self._learning_states[ai_type]:
            self._learning_states[ai_type]['productivity_metrics'] = {}
        
        metrics = self._learning_states[ai_type]['productivity_metrics']
        metrics['total_improvements'] = metrics.get('total_improvements', 0) + len(improvements)
        metrics['average_productivity_score'] = (
            (metrics.get('average_productivity_score', 0) * metrics.get('learning_events_count', 0) + productivity_score) /
            (metrics.get('learning_events_count', 0) + 1)
        )
        metrics['learning_events_count'] = metrics.get('learning_events_count', 0) + 1
        metrics['ml_confidence_average'] = (
            (metrics.get('ml_confidence_average', 0) * (metrics.get('learning_events_count', 0) - 1) + ml_confidence) /
            metrics.get('learning_events_count', 0)
        )
        
        logger.info(f"Updated ENHANCED learning state for {ai_type}", 
                   event=learning_event,
                   improvements_count=len(improvements),
                   productivity_score=productivity_score,
                   ml_confidence=ml_confidence)
    
    async def _analyze_enhanced_failure_pattern(self, test_summary: str) -> Dict[str, Any]:
        """Analyze ENHANCED failure patterns using ML"""
        pattern_analysis = {
            'failure_type': await self._classify_failure_type(test_summary),
            'severity': await self._calculate_failure_severity(test_summary),
            'complexity': await self._calculate_failure_complexity(test_summary),
            'keywords_found': await self._extract_failure_keywords(test_summary),
            'recommended_actions': [],
            'ml_insights': []
        }
        
        # Generate ENHANCED recommended actions based on pattern
        if pattern_analysis['severity'] > 0.8:
            pattern_analysis['recommended_actions'].append("CRITICAL: Immediate code review and comprehensive testing")
            pattern_analysis['ml_insights'].append("High severity failures require immediate attention and systematic fixes")
        
        if pattern_analysis['complexity'] > 5.0:
            pattern_analysis['recommended_actions'].append("Complex failure detected - implement systematic debugging approach")
            pattern_analysis['ml_insights'].append("Complex failures benefit from structured debugging and root cause analysis")
        
        if pattern_analysis['keywords_found'] > 3:
            pattern_analysis['recommended_actions'].append("Multiple failure indicators - implement comprehensive debugging session")
            pattern_analysis['ml_insights'].append("Multiple failure indicators suggest systemic issues requiring comprehensive review")
        
        return pattern_analysis
    
    async def _predict_enhanced_next_actions(self, failure_features: Dict, ai_type: str) -> List[str]:
        """Predict ENHANCED next actions using ML models"""
        actions = []
        
        try:
            # Use trained model to predict next actions
            if 'failure_predictor' in self._ml_models:
                # Prepare features for prediction
                feature_vector = np.array([
                    failure_features.get('code_length', 0),
                    failure_features.get('code_changes', 0),
                    failure_features.get('change_ratio', 0),
                    failure_features.get('ai_type_encoded', 0),
                    failure_features.get('failure_keywords', 0),
                    failure_features.get('failure_severity', 0),
                    failure_features.get('failure_complexity', 0),
                    failure_features.get('hour_of_day', 0),
                    failure_features.get('day_of_week', 0),
                    failure_features.get('time_since_last_failure', 24),
                    failure_features.get('complexity_score', 0),
                    failure_features.get('readability_score', 0),
                    failure_features.get('maintainability_score', 0),
                    failure_features.get('proposal_quality_score', 0),
                    failure_features.get('improvement_potential', 0)
                ]).reshape(1, -1)
                
                # Scale features
                scaler = StandardScaler()
                feature_vector_scaled = scaler.fit_transform(feature_vector)
                
                # Predict failure probability
                failure_prob = self._ml_models['failure_predictor'].predict(feature_vector_scaled)[0]
                
                if failure_prob > 0.8:
                    actions.append("HIGH RISK: Implement comprehensive preventive measures and monitoring")
                    actions.append("Schedule immediate code review and testing session")
                elif failure_prob > 0.6:
                    actions.append("MODERATE RISK: Enhance testing coverage and error handling")
                    actions.append("Implement additional validation and logging")
                elif failure_prob > 0.4:
                    actions.append("LOW-MODERATE RISK: Continue with enhanced monitoring")
                    actions.append("Add basic error handling and validation")
                else:
                    actions.append("LOW RISK: Continue with normal development practices")
                    actions.append("Maintain current testing and validation approach")
            
        except Exception as e:
            logger.error(f"Error predicting ENHANCED next actions: {str(e)}")
            actions.append("Apply standard development practices")
        
        return actions
    
    async def _update_ai_learning_state(self, ai_type: str, learning_event: str, improvements: List[str]):
        """Update AI learning state with new knowledge"""
        if ai_type not in self._learning_states:
            self._learning_states[ai_type] = {
                'learning_events': [],
                'improvements_learned': [],
                'failure_patterns': [],
                'success_patterns': [],
                'last_learning': None
            }
        
        self._learning_states[ai_type]['learning_events'].append({
            'timestamp': datetime.now().isoformat(),
            'event': learning_event,
            'improvements': improvements
        })
        
        self._learning_states[ai_type]['improvements_learned'].extend(improvements)
        self._learning_states[ai_type]['last_learning'] = datetime.now().isoformat()
        
        logger.info(f"Updated learning state for {ai_type}", 
                   event=learning_event,
                   improvements_count=len(improvements))
    
    async def get_learning_insights(self, ai_type: str) -> Dict[str, Any]:
        """Get learning insights for a specific AI type"""
        try:
            # Get learning stats
            stats = await self.get_learning_stats(ai_type)
            
            # Get recent learning patterns
            recent_patterns = await self._get_recent_learning_patterns(ai_type)
            
            # Get failure analysis
            failure_analytics = await self.get_failure_learning_analytics(ai_type)
            
            # Get explainability analytics
            explainability = await self.get_explainability_analytics(ai_type)
            
            return {
                "learning_stats": stats,
                "recent_patterns": recent_patterns,
                "failure_analytics": failure_analytics,
                "explainability": explainability,
                "ai_type": ai_type,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting learning insights for {ai_type}: {str(e)}")
            return {
                "learning_stats": {},
                "recent_patterns": [],
                "failure_analytics": {},
                "explainability": {},
                "ai_type": ai_type,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    async def get_learning_log(self, ai_type: str) -> str:
        """Get learning log as a string for AI services"""
        try:
            # Get learning insights
            insights = await self.get_learning_insights(ai_type)
            
            # Convert insights to a readable string format
            learning_log = f"""
AI Type: {ai_type}
Learning Stats: {insights.get('learning_stats', {})}
Recent Patterns: {insights.get('recent_patterns', [])}
Failure Analytics: {insights.get('failure_analytics', {})}
Explainability: {insights.get('explainability', {})}
Timestamp: {insights.get('timestamp', '')}
"""
            return learning_log
        except Exception as e:
            logger.error(f"Error getting learning log for {ai_type}: {str(e)}")
            return f"AI Type: {ai_type}\nLearning data unavailable due to error: {str(e)}"

    async def _get_recent_learning_patterns(self, ai_type: str) -> List[Dict[str, Any]]:
        """Get recent learning patterns for an AI type"""
        try:
            # This is a placeholder implementation
            # In a real implementation, you would query the database for recent learning patterns
            return [
                {
                    "pattern": "code_optimization",
                    "frequency": 5,
                    "last_occurrence": datetime.now().isoformat(),
                    "success_rate": 0.8
                },
                {
                    "pattern": "security_analysis", 
                    "frequency": 3,
                    "last_occurrence": datetime.now().isoformat(),
                    "success_rate": 0.7
                }
            ]
        except Exception as e:
            logger.error(f"Error getting recent learning patterns for {ai_type}: {str(e)}")
            return []
    
    async def learn_from_proposal(self, proposal_id: str, status: str, feedback_reason: str = None) -> Dict[str, Any]:
        """Learn from a proposal's outcome"""
        try:
            from ..models.sql_models import Proposal, Learning
            from sqlalchemy import select
            from datetime import datetime
            
            async with get_session() as session:
                # Get the proposal
                stmt = select(Proposal).where(Proposal.id == proposal_id)
                result = await session.execute(stmt)
                proposal = result.scalar_one_or_none()
                
                if not proposal:
                    logger.warning("Proposal not found for learning", proposal_id=proposal_id)
                    return {"status": "error", "message": "Proposal not found"}
                
                # Create learning pattern
                pattern = f"proposal_{status}_{proposal.ai_type}_{proposal.improvement_type}"
                
                # Check if we already have this learning pattern
                existing_learning = await session.execute(
                    select(Learning).where(
                        Learning.ai_type == proposal.ai_type,
                        Learning.learning_type == "proposal_outcome"
                    )
                )
                existing = existing_learning.scalar_one_or_none()
                
                if existing:
                    # Update existing learning
                    learning_data = existing.learning_data or {}
                    applied_count = learning_data.get('applied_count', 0) + 1
                    current_success_rate = learning_data.get('success_rate', 0.0)
                    new_success_rate = (current_success_rate + (1.0 if status == "approved" else 0.0)) / 2.0
                    
                    existing.learning_data = {
                        **learning_data,
                        'pattern': pattern,
                        'context': f"Proposal {proposal_id} outcome: {status}",
                        'feedback': feedback_reason or f"Proposal {status}",
                        'confidence': 0.8,
                        'applied_count': applied_count,
                        'success_rate': new_success_rate
                    }
                    existing.updated_at = datetime.utcnow()  # type: ignore
                    logger.info(
                        f"Updated existing learning pattern: pattern={pattern}, success_rate={new_success_rate}, applied_count={applied_count}"
                    )
                else:
                    # Create new learning entry
                    new_learning = Learning(
                        ai_type=proposal.ai_type,
                        learning_type="proposal_outcome",
                        learning_data={
                            'pattern': pattern,
                            'context': f"Proposal {proposal_id} outcome: {status}",
                            'feedback': feedback_reason or f"Proposal {status}",
                            'confidence': 0.8,
                            'applied_count': 1,
                            'success_rate': 1.0 if status == "approved" else 0.0
                        }
                    )
                    session.add(new_learning)
                    logger.info("Created new learning pattern", 
                               pattern=pattern, 
                               ai_type=proposal.ai_type)
                
                # Update proposal with learning applied
                proposal.ai_learning_applied = True  # type: ignore
                proposal.updated_at = datetime.utcnow()  # type: ignore
                
                await session.commit()
                
                return {
                    "status": "success",
                    "pattern": pattern,
                    "ai_type": proposal.ai_type,
                    "learning_applied": True
                }
                
        except Exception as e:
            logger.error(f"Error learning from proposal: {str(e)} | proposal_id={proposal_id}")
            return {"status": "error", "message": str(e)}

    async def get_learning_stats(self, ai_type: str = None) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        try:
            from ..models.sql_models import Learning, Proposal
            from sqlalchemy import select, func
            from datetime import datetime, timedelta
            
            async with get_session() as session:
                # Get learning patterns
                query = select(Learning)
                if ai_type:
                    query = query.where(Learning.ai_type == ai_type)
                
                result = await session.execute(query)
                learning_entries = result.scalars().all()
                
                # Calculate statistics
                total_patterns = len(learning_entries)
                total_applied = sum(entry.learning_data.get('applied_count', 0) if entry.learning_data else 0 for entry in learning_entries)
                avg_success_rate = sum(entry.learning_data.get('success_rate', 0.0) if entry.learning_data else 0.0 for entry in learning_entries) / total_patterns if total_patterns > 0 else 0.0
                
                # Get recent learning activity
                recent_learning = await session.execute(
                    select(Learning)
                    .where(Learning.updated_at >= datetime.utcnow() - timedelta(days=7))
                    .order_by(Learning.updated_at.desc())
                    .limit(10)
                )
                recent_entries = recent_learning.scalars().all()
                
                # Get proposal statistics
                proposal_query = select(func.count(Proposal.id))
                if ai_type:
                    proposal_query = proposal_query.where(Proposal.ai_type == ai_type)
                
                total_proposals = await session.execute(proposal_query)
                proposal_count = total_proposals.scalar()
                
                # Get successful proposals
                success_query = select(func.count(Proposal.id)).where(
                    Proposal.status == "test-passed",
                    Proposal.test_status == "passed"
                )
                if ai_type:
                    success_query = success_query.where(Proposal.ai_type == ai_type)
                
                success_result = await session.execute(success_query)
                success_count = success_result.scalar() or 0
                
                success_rate = (success_count / proposal_count * 100) if proposal_count and proposal_count > 0 else 0.0
                
                # Get last activity timestamp
                last_activity = datetime.utcnow().isoformat()
                
                return {
                    "total_patterns": total_patterns,
                    "total_applied": total_applied,
                    "average_success_rate": avg_success_rate,
                    "recent_learning": [
                        {
                            "pattern": getattr(entry, 'pattern', ''),
                            "ai_type": entry.ai_type,
                            "success_rate": getattr(entry, 'success_rate', 0.0),
                            "applied_count": getattr(entry, 'applied_count', 0),
                            "updated_at": entry.updated_at.isoformat() if entry.updated_at else None
                        }
                        for entry in recent_entries
                    ],
                    "total_proposals": proposal_count,
                    "successful_proposals": success_count,
                    "success_rate": success_rate,
                    "last_activity": last_activity,
                    "timestamp": datetime.utcnow().isoformat(),
                    # Add learning progress calculations
                    "learning_progress": min((total_patterns * 0.1 + avg_success_rate * 0.5) * 100, 100.0),
                    "internet_learning_progress": 0.0  # Will be calculated separately if needed
                }
                
        except Exception as e:
            logger.error(f"Error getting learning stats: {str(e)}")
            return {
                "total_patterns": 0,
                "total_applied": 0,
                "average_success_rate": 0.0,
                "recent_learning": [],
                "proposal_stats": {"total": 0, "successful": 0, "success_rate": 0.0},
                "learning_progress": 0.0,
                "last_updated": datetime.utcnow().isoformat()
            }

    async def apply_learning_to_proposal(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply learned patterns to improve proposal quality"""
        try:
            from ..models.sql_models import Learning
            from sqlalchemy import select
            
            async with get_session() as session:
                # Get relevant learning patterns
                stmt = select(Learning).where(
                    Learning.ai_type == proposal_data.get("ai_type"),
                    Learning.learning_type == "proposal_outcome"
                )
                
                result = await session.execute(stmt)
                learning_patterns = result.scalars().all()
                
                improvements = []
                confidence_boost = 0.0
                
                for pattern in learning_patterns:
                    # Get pattern data from learning_data
                    pattern_data = pattern.learning_data or {}
                    pattern_text = pattern_data.get('pattern', '')
                    success_rate = pattern_data.get('success_rate', 0.0)
                    
                    # Only apply high-confidence patterns
                    if success_rate > 0.7:
                        # Apply pattern-based improvements
                        if "security" in pattern_text and proposal_data.get("improvement_type") == "security":
                            confidence_boost += 0.1
                            improvements.append("Applied security learning pattern")
                        
                        elif "performance" in pattern_text and proposal_data.get("improvement_type") == "performance":
                            confidence_boost += 0.1
                            improvements.append("Applied performance learning pattern")
                        
                        elif "quality" in pattern_text and proposal_data.get("improvement_type") == "quality":
                            confidence_boost += 0.1
                            improvements.append("Applied quality learning pattern")
                
                # Update proposal confidence
                original_confidence = proposal_data.get("confidence", 0.5)
                new_confidence = min(original_confidence + confidence_boost, 1.0)
                
                return {
                    "original_confidence": original_confidence,
                    "new_confidence": new_confidence,
                    "confidence_boost": confidence_boost,
                    "improvements_applied": improvements,
                    "patterns_used": len(learning_patterns)
                }
                
        except Exception as e:
            logger.error(f"Error applying learning to proposal: {str(e)}")
            return {
                "original_confidence": proposal_data.get("confidence", 0.5),
                "new_confidence": proposal_data.get("confidence", 0.5),
                "confidence_boost": 0.0,
                "improvements_applied": [],
                "patterns_used": 0
            }
    
    async def save_internet_learning_result(self, agent_id: str, topic: str, result: Dict[str, Any]) -> bool:
        """Save internet learning result to the learning system"""
        try:
            logger.info(f"Saving internet learning result for agent {agent_id}, topic: {topic}")
            
            # Create learning record
            learning_record = {
                'timestamp': datetime.now().isoformat(),
                'agent_id': agent_id,
                'topic': topic,
                'source': result.get('source', 'unknown'),
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'summary': result.get('summary', ''),
                'relevance_score': result.get('score', 0),
                'learning_value': await self._calculate_learning_value(result, topic),
                'insights': await self._extract_insights_from_result(result, topic)
            }
            
            # Add to learning data
            self._learning_data.append(learning_record)
            
            # Update learning state for the agent
            if agent_id not in self._learning_states:
                self._learning_states[agent_id] = {
                    'learning_events': [],
                    'improvements_learned': [],
                    'internet_learning_results': [],
                    'last_learning': None
                }
            
            self._learning_states[agent_id]['internet_learning_results'].append(learning_record)
            self._learning_states[agent_id]['last_learning'] = datetime.now().isoformat()
            
            logger.info(f"Successfully saved internet learning result for {agent_id}", 
                       topic=topic,
                       title=result.get('title', 'Unknown'))
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving internet learning result: {str(e)}")
            return False
    
    async def _calculate_learning_value(self, result: Dict[str, Any], topic: str) -> float:
        """Calculate the learning value of an internet result"""
        try:
            value = 0.0
            
            # Base value from relevance score
            value += result.get('score', 0) * 0.3
            
            # Topic relevance bonus
            title = result.get('title', '').lower()
            summary = result.get('summary', '').lower()
            topic_lower = topic.lower()
            
            if topic_lower in title or topic_lower in summary:
                value += 0.4
            
            # Source quality bonus
            source = result.get('source', '').lower()
            trusted_sources = ['stackoverflow', 'github', 'arxiv', 'medium']
            if any(trusted in source for trusted in trusted_sources):
                value += 0.2
            
            # Content length bonus
            content_length = len(result.get('summary', ''))
            if content_length > 500:
                value += 0.1
            
            return min(value, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating learning value: {str(e)}")
            return 0.5  # Default value
    
    async def _extract_insights_from_result(self, result: Dict[str, Any], topic: str) -> List[str]:
        """Extract insights from an internet learning result"""
        insights = []
        
        try:
            title = result.get('title', '')
            summary = result.get('summary', '')
            
            # Extract key phrases and concepts
            content = f"{title} {summary}".lower()
            
            # Look for technical terms and patterns
            technical_terms = ['api', 'framework', 'library', 'algorithm', 'pattern', 'best practice']
            for term in technical_terms:
                if term in content:
                    insights.append(f"Technical insight: {term} usage patterns")
            
            # Look for problem-solving patterns
            problem_indicators = ['error', 'issue', 'problem', 'solution', 'fix', 'bug']
            if any(indicator in content for indicator in problem_indicators):
                insights.append("Problem-solving approach identified")
            
            # Look for performance insights
            performance_terms = ['performance', 'optimization', 'efficiency', 'speed', 'memory']
            if any(term in content for term in performance_terms):
                insights.append("Performance optimization insight")
            
            # Look for security insights
            security_terms = ['security', 'vulnerability', 'authentication', 'authorization', 'encryption']
            if any(term in content for term in security_terms):
                insights.append("Security best practice identified")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error extracting insights: {str(e)}")
            return ["General learning insight"] 

    async def _perform_periodic_internet_learning(self) -> Dict[str, Any]:
        """Perform periodic internet-augmented learning for all AIs"""
        start_time = time.time()
        results = {
            "timestamp": datetime.now().isoformat(),
            "ai_learning_results": {},
            "total_learning_value": 0.0,
            "search_results_count": 0,
            "processing_time": 0
        }
        # Define learning topics for each AI
        learning_topics = {
            "imperium": [
                "system architecture patterns",
                "strategic planning methodologies",
                "complex problem solving techniques",
                "enterprise software design",
                "scalability best practices",
                "machine learning fundamentals",
                "deep learning architectures",
                "AI model deployment",
                "data science workflows",
                "reinforcement learning",
                "natural language processing",
                "computer vision",
                "microservices architecture",
                "API security best practices",
                "database optimization (SQL/NoSQL)",
                "asynchronous programming in Python",
                "DevOps and CI/CD pipelines",
                "cloud-native design patterns",
                "RESTful API design",
                "GraphQL APIs",
                "distributed systems",
                "observability and monitoring",
                "error handling and resilience",
                "scalability and load balancing",
                "containerization (Docker, Kubernetes)",
                "automated testing strategies",
                "code review and static analysis"
            ],
            "guardian": [
                "security best practices",
                "code quality standards",
                "testing methodologies",
                "performance optimization",
                "code review techniques"
            ],
            "sandbox": [
                "experimental programming",
                "rapid prototyping",
                "creative problem solving",
                "new technology trends",
                "innovation methodologies"
            ],
            "conquest": [
                "app development frameworks",
                "mobile app design patterns",
                "user experience design",
                "app store optimization",
                "cross-platform development"
            ]
        }
        total_learning_value = 0.0
        total_search_results = 0
        # Process each AI
        for ai_type, topics in learning_topics.items():
            ai_results = {
                "topics_learned": [],
                "learning_score": 0.0,
                "search_results": [],
                "insights_gained": []
            }
            # Learn from each topic with internet search
            for topic in topics[:2]:  # Limit to 2 topics per AI per cycle
                try:
                    # Perform internet search for the topic
                    search_results = await self._search_internet(topic, [ai_type], [topic])
                    total_search_results += len(search_results)
                    # Simulate AI learning with internet data
                    ai_response = await self._simulate_ai_learning(
                        ai_type=ai_type,
                        subject=topic,
                        description=f"Periodic learning about {topic}",
                        code=None,
                        tags=[ai_type, "periodic_learning"],
                        keywords=[topic],
                        search_results=search_results,
                        weight=1.0
                    )
                    ai_results["topics_learned"].append(topic)
                    ai_results["learning_score"] += ai_response.get("learning_score", 0.0)
                    ai_results["search_results"].extend(search_results)
                    ai_results["insights_gained"].append(ai_response.get("insights", ""))
                except Exception as e:
                    logger.error(f"Error learning topic {topic} for {ai_type}: {str(e)}")
            # Calculate average learning score for this AI
            if ai_results["topics_learned"]:
                ai_results["learning_score"] = ai_results["learning_score"] / len(ai_results["topics_learned"])
                total_learning_value += ai_results["learning_score"]
            results["ai_learning_results"][ai_type.title()] = ai_results
        # Calculate overall metrics
        results["total_learning_value"] = total_learning_value / len(learning_topics) if learning_topics else 0.0
        results["search_results_count"] = total_search_results
        results["processing_time"] = time.time() - start_time
        return results

    def get_last_periodic_learning_info(self) -> Dict[str, Any]:
        """Get information about the last periodic learning cycle"""
        return {
            "last_learning_time": self._last_periodic_learning.isoformat() if self._last_periodic_learning else None,
            "is_periodic_learning_active": self._periodic_task_running,
            "next_learning_in_minutes": self._get_next_learning_countdown()
        }

    def _get_next_learning_countdown(self) -> Optional[int]:
        """Calculate minutes until next learning cycle"""
        if not self._last_periodic_learning:
            return None
        next_learning = self._last_periodic_learning + timedelta(hours=1)
        now = datetime.now()
        if next_learning > now:
            return int((next_learning - now).total_seconds() / 60)
        else:
            return 0  # Due now

    async def _calculate_learning_value_from_failure(self, failure_features: Dict, ai_type: str) -> float:
        """Calculate learning value specifically from failure analysis"""
        try:
            # Extract failure learning indicators
            failure_type = failure_features.get('failure_type', '')
            failure_severity = failure_features.get('failure_severity', 0.0)
            failure_complexity = failure_features.get('failure_complexity', 0.0)
            
            # Learning value from failure (higher severity/complexity = more learning potential)
            severity_learning = min(1.0, failure_severity * 1.5)  # Higher severity = more learning
            complexity_learning = min(1.0, failure_complexity * 1.2)  # Higher complexity = more learning
            
            # Time-based learning (recent failures are more valuable)
            time_since_last = failure_features.get('time_since_last_failure', 0.0)
            time_learning = max(0.1, 1.0 - (time_since_last / 3600))  # Decay over time
            
            # AI-specific learning factors
            ai_learning_factors = {
                'imperium': 1.2,  # AI governance learns more from failures
                'guardian': 1.1,  # Security learns from failures
                'sandbox': 1.0,   # Standard learning
                'conquest': 0.9   # App development learns less from failures
            }
            
            ai_factor = ai_learning_factors.get(ai_type, 1.0)
            
            # Calculate final learning value
            learning_value = (severity_learning * 0.4 + complexity_learning * 0.3 + time_learning * 0.3) * ai_factor
            return min(1.0, max(0.0, learning_value))
            
        except Exception as e:
            logger.error(f"Error calculating learning value from failure: {e}")
            return 0.5

    async def _update_failure_learning_analytics(self, ai_type: str, failure_features: Dict, improvements: List[str]):
        """Update analytics with failure learning data"""
        try:
            if 'failure_learning_analytics' not in self._productivity_metrics:
                self._productivity_metrics['failure_learning_analytics'] = {}
            
            if ai_type not in self._productivity_metrics['failure_learning_analytics']:
                self._productivity_metrics['failure_learning_analytics'][ai_type] = {
                    'total_failures': 0,
                    'learning_value_sum': 0.0,
                    'improvements_generated': 0,
                    'failure_patterns': {},
                    'learning_trends': [],
                    'last_updated': datetime.now().isoformat()
                }
            
            analytics = self._productivity_metrics['failure_learning_analytics'][ai_type]
            analytics['total_failures'] += 1
            analytics['learning_value_sum'] += failure_features.get('learning_value', 0.0)
            analytics['improvements_generated'] += len(improvements)
            
            # Track failure patterns
            failure_type = failure_features.get('failure_type', 'unknown')
            if failure_type not in analytics['failure_patterns']:
                analytics['failure_patterns'][failure_type] = 0
            analytics['failure_patterns'][failure_type] += 1
            
            # Track learning trends
            trend_data = {
                'timestamp': datetime.now().isoformat(),
                'learning_value': failure_features.get('learning_value', 0.0),
                'improvements_count': len(improvements),
                'failure_severity': failure_features.get('failure_severity', 0.0)
            }
            analytics['learning_trends'].append(trend_data)
            
            # Keep only recent trends
            if len(analytics['learning_trends']) > 100:
                analytics['learning_trends'] = analytics['learning_trends'][-50:]
            
            analytics['last_updated'] = datetime.now().isoformat()
            
            logger.info(f"Updated failure learning analytics for {ai_type}")
            
        except Exception as e:
            logger.error(f"Error updating failure learning analytics: {e}")

    async def get_failure_learning_analytics(self, ai_type: str = None) -> Dict[str, Any]:
        """Get comprehensive failure learning analytics"""
        try:
            if 'failure_learning_analytics' not in self._productivity_metrics:
                return {}
            
            if ai_type:
                return self._productivity_metrics['failure_learning_analytics'].get(ai_type, {})
            
            return self._productivity_metrics['failure_learning_analytics']
            
        except Exception as e:
            logger.error(f"Error getting failure learning analytics: {e}")
            return {}

    async def get_enhanced_learning_analytics(self) -> Dict[str, Any]:
        """Get comprehensive enhanced learning analytics with ML insights"""
        try:
            analytics = {
                'learning_data_summary': {
                    'total_learning_records': len(self._learning_data),
                    'failure_learning_records': len([r for r in self._learning_data if r.get('outcome') == 'failure']),
                    'success_learning_records': len([r for r in self._learning_data if r.get('outcome') == 'success']),
                    'ml_models_trained': len(self._ml_models),
                    'last_updated': datetime.now().isoformat()
                },
                'ai_learning_performance': {},
                'ml_model_performance': {},
                'productivity_metrics': self._productivity_metrics,
                'failure_learning_analytics': await self.get_failure_learning_analytics()
            }
            
            # Calculate AI-specific performance metrics
            for ai_type in ['imperium', 'guardian', 'sandbox', 'conquest']:
                ai_records = [r for r in self._learning_data if r.get('ai_type') == ai_type]
                if ai_records:
                    analytics['ai_learning_performance'][ai_type] = {
                        'total_learning_events': len(ai_records),
                        'average_learning_value': np.mean([r.get('learning_value', 0.0) for r in ai_records]),
                        'average_ml_confidence': np.mean([r.get('ml_confidence', 0.0) for r in ai_records]),
                        'improvements_generated': sum(len(r.get('improvements', [])) for r in ai_records),
                        'failure_learning_rate': len([r for r in ai_records if r.get('outcome') == 'failure']) / len(ai_records)
                    }
            
            # Calculate ML model performance
            for model_name, model in self._ml_models.items():
                if hasattr(model, 'score') and hasattr(model, 'feature_importances_'):
                    analytics['ml_model_performance'][model_name] = {
                        'model_type': type(model).__name__,
                        'feature_importance_count': len(model.feature_importances_) if hasattr(model, 'feature_importances_') else 0,
                        'is_trained': hasattr(model, 'feature_importances_') or hasattr(model, 'coef_')
                    }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting enhanced learning analytics: {e}")
            return {} 

    def anthropic_enhanced_learning(self, prompt: str) -> str:
        """Use Anthropic Claude for advanced learning, code review, or proposal improvement."""
        try:
            return call_claude(prompt)
        except Exception as e:
            return f"Anthropic error: {str(e)}" 

    async def add_learning_sources(self, ai_type: str, sources: list):
        # Dummy implementation, should update persistent learning sources
        logger.info(f"Adding new learning sources for {ai_type}: {sources}")
        # TODO: Implement persistent storage for learning sources 

    async def process_enhanced_oath_paper(
        self,
        oath_paper_id: str,
        subject: str,
        tags: List[str],
        description: Optional[str] = None,
        code: Optional[str] = None,
        target_ai: Optional[str] = None,
        ai_weights: Optional[Dict[str, float]] = None,
        extract_keywords: bool = True,
        internet_search: bool = True,  # Always enabled for enhanced learning
        git_integration: bool = True,
        learning_instructions: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """Process enhanced oath paper with advanced learning capabilities"""
        start_time = time.time()
        
        try:
            logger.info("Processing enhanced oath paper", 
                       oath_paper_id=oath_paper_id,
                       subject=subject,
                       target_ai=target_ai)
            
            # Initialize result structure
            result = {
                "ai_insights": {},
                "learning_value": 0.0,
                "ai_responses": {},
                "improvement_suggestions": "",
                "processing_time": 0,
                "keywords_extracted": [],
                "search_results": [],
                "git_operations": []
            }
            
            # Extract keywords if enabled
            if extract_keywords:
                keywords = await self._extract_keywords(subject, description, code, tags)
                result["keywords_extracted"] = keywords
                logger.info("Keywords extracted", keywords=keywords)
            
            # Perform internet search if enabled
            if internet_search:
                search_results = await self._search_internet(subject, tags, keywords if extract_keywords else [])
                result["search_results"] = search_results
                logger.info("Internet search completed", results_count=len(search_results))
            
            # Process with AI learning
            ai_responses = {}
            learning_value = 0.0
            
            # Determine which AIs to process
            if target_ai and target_ai != "All AIs":
                ai_types = [target_ai.lower()]
            else:
                ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            # Process each AI
            for ai_type in ai_types:
                ai_weight = ai_weights.get(ai_type.title(), 1.0) if ai_weights else 1.0
                
                # Simulate AI learning process
                ai_response = await self._simulate_ai_learning(
                    ai_type=ai_type,
                    subject=subject,
                    description=description,
                    code=code,
                    tags=tags,
                    keywords=result.get("keywords_extracted", []),
                    search_results=result.get("search_results", []),
                    weight=ai_weight
                )
                
                ai_responses[ai_type.title()] = ai_response
                learning_value += ai_response.get("learning_score", 0.0) * ai_weight
            
            # Calculate average learning value
            if ai_responses:
                learning_value = learning_value / len(ai_responses)
            
            # Generate improvement suggestions
            improvement_suggestions = await self._generate_improvement_suggestions(
                subject, description, code, tags, result.get("search_results", [])
            )
            
            # Git integration if enabled
            if git_integration:
                git_ops = await self._perform_git_operations(oath_paper_id, subject, description, code)
                result["git_operations"] = git_ops
            
            # Update result
            result.update({
                "ai_responses": ai_responses,
                "learning_value": learning_value,
                "improvement_suggestions": improvement_suggestions,
                "processing_time": time.time() - start_time
            })
            
            logger.info("Enhanced oath paper processing completed",
                       oath_paper_id=oath_paper_id,
                       processing_time=result["processing_time"],
                       learning_value=learning_value)
            
            return result
            
        except Exception as e:
            logger.error("Error processing enhanced oath paper", 
                        error=str(e),
                        oath_paper_id=oath_paper_id)
            return {
                "ai_insights": {},
                "learning_value": 0.0,
                "ai_responses": {},
                "improvement_suggestions": "",
                "processing_time": time.time() - start_time,
                "error": str(e)
            }

    async def _extract_keywords(self, subject: str, description: Optional[str], code: Optional[str], tags: List[str]) -> List[str]:
        """Extract keywords from oath paper content"""
        keywords = set()
        
        # Add tags as keywords
        keywords.update(tags)
        
        # Extract from subject
        subject_words = subject.lower().split()
        keywords.update([word for word in subject_words if len(word) > 3])
        
        # Extract from description
        if description:
            desc_words = description.lower().split()
            keywords.update([word for word in desc_words if len(word) > 3])
        
        # Extract from code (basic keyword extraction)
        if code:
            code_keywords = ['function', 'class', 'method', 'api', 'database', 'server', 'client', 'config', 'error', 'exception']
            code_lower = code.lower()
            for keyword in code_keywords:
                if keyword in code_lower:
                    keywords.add(keyword)
        
        return list(keywords)[:20]  # Limit to 20 keywords

    async def _search_internet(self, subject: str, tags: List[str], keywords: List[str]) -> List[Dict[str, Any]]:
        """Simulate internet search for oath paper content"""
        # This is a simulation - in production, you'd integrate with real search APIs
        search_results = []
        
        # Simulate search results based on subject and keywords
        search_terms = [subject] + tags + keywords[:5]
        
        for i, term in enumerate(search_terms[:3]):  # Limit to 3 search results
            search_results.append({
                "title": f"Search result for {term}",
                "url": f"https://example.com/search/{term}",
                "snippet": f"This is a simulated search result for {term}. In a real implementation, this would contain actual search results from the internet.",
                "relevance_score": 0.8 - (i * 0.1)
            })
        
        return search_results

    async def _simulate_ai_learning(self, ai_type: str, subject: str, description: Optional[str], code: Optional[str], 
                                  tags: List[str], keywords: List[str], search_results: List[Dict[str, Any]], weight: float) -> Dict[str, Any]:
        """Simulate AI learning process"""
        # Calculate learning score based on content quality
        content_length = len(subject) + len(description or "") + len(code or "")
        learning_score = min(1.0, content_length / 1000) * weight
        
        # Simulate AI response
        ai_response = {
            "learning_score": learning_score,
            "knowledge_acquired": f"Learned about {subject}",
            "improvements_suggested": f"Enhanced understanding of {', '.join(tags)}",
            "confidence": 0.8,
            "processing_time": 0.5
        }
        
        return ai_response

    async def _generate_improvement_suggestions(self, subject: str, description: Optional[str], code: Optional[str], 
                                             tags: List[str], search_results: List[Dict[str, Any]]) -> str:
        """Generate improvement suggestions based on oath paper content"""
        suggestions = []
        
        # Basic suggestions based on content
        if description and len(description) < 100:
            suggestions.append("Consider adding more detailed description")
        
        if code and len(code) < 50:
            suggestions.append("Consider adding more code examples")
        
        if len(tags) < 3:
            suggestions.append("Consider adding more specific tags")
        
        if not suggestions:
            suggestions.append("Content looks good! Consider sharing with other AIs for broader learning.")
        
        return "; ".join(suggestions)

    async def _perform_git_operations(self, oath_paper_id: str, subject: str, description: Optional[str], code: Optional[str]) -> List[Dict[str, Any]]:
        """Simulate git operations for oath paper"""
        git_ops = []
        
        # Simulate git operations
        git_ops.append({
            "operation": "commit",
            "message": f"Add oath paper: {subject}",
            "files_changed": 1,
            "status": "success"
        })
        
        if code:
            git_ops.append({
                "operation": "tag",
                "message": f"oath-paper-{oath_paper_id}",
                "status": "success"
            })
        
        return git_ops 

    async def store_internet_learning(self, ai_type: str, topics: List[str], timestamp: datetime) -> bool:
        """Store internet learning results for an AI type"""
        try:
            learning_record = {
                'ai_type': ai_type,
                'topics': topics,
                'timestamp': timestamp.isoformat(),
                'learning_type': 'internet',
                'status': 'completed'
            }
            
            # Store in learning data
            self._learning_data.append(learning_record)
            
            # Update learning state
            if ai_type not in self._learning_states:
                self._learning_states[ai_type] = {}
            
            self._learning_states[ai_type]['last_internet_learning'] = timestamp.isoformat()
            self._learning_states[ai_type]['internet_learning_topics'] = topics
            
            logger.info(f"Stored internet learning for {ai_type}", topics=len(topics))
            return True
            
        except Exception as e:
            logger.error(f"Error storing internet learning for {ai_type}: {str(e)}")
            return False
    
    async def store_internet_insight(self, ai_type: str, topic: str, source: str, insights: List[str], timestamp: datetime) -> bool:
        """Store individual internet insights"""
        try:
            insight_record = {
                'ai_type': ai_type,
                'topic': topic,
                'source': source,
                'insights': insights,
                'timestamp': timestamp.isoformat(),
                'learning_type': 'internet_insight'
            }
            
            # Store in learning data
            self._learning_data.append(insight_record)
            
            logger.info(f"Stored internet insight for {ai_type}", topic=topic, source=source, insights_count=len(insights))
            return True
            
        except Exception as e:
            logger.error(f"Error storing internet insight for {ai_type}: {str(e)}")
            return False
    
    async def get_internet_insights(self, ai_type: str, improvement_type: str = None) -> List[Dict]:
        """Get recent internet learning insights for an AI type"""
        try:
            # Filter learning data for internet insights
            internet_insights = []
            
            for record in self._learning_data:
                if (record.get('ai_type') == ai_type and 
                    record.get('learning_type') in ['internet', 'internet_insight']):
                    
                    # Filter by improvement type if specified
                    if improvement_type:
                        topic = record.get('topic', '')
                        if improvement_type.lower() in topic.lower():
                            internet_insights.append(record)
                    else:
                        internet_insights.append(record)
            
            # Sort by timestamp (most recent first)
            internet_insights.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Return recent insights (last 30 days)
            recent_insights = []
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for insight in internet_insights:
                try:
                    insight_timestamp = datetime.fromisoformat(insight.get('timestamp', ''))
                    if insight_timestamp >= cutoff_date:
                        recent_insights.append(insight)
                except:
                    continue
            
            logger.info(f"Retrieved {len(recent_insights)} internet insights for {ai_type}")
            return recent_insights
            
        except Exception as e:
            logger.error(f"Error getting internet insights for {ai_type}: {str(e)}")
            return []
    
    async def get_internet_learning_progress(self, ai_type: str) -> float:
        """Get internet learning progress for an AI type"""
        try:
            # Get recent internet learning activity
            recent_insights = await self.get_internet_insights(ai_type)
            
            if not recent_insights:
                return 0.0
            
            # Calculate progress based on:
            # 1. Number of insights (max 50 for full progress)
            # 2. Recency of learning (more recent = higher progress)
            # 3. Diversity of topics
            
            insight_count = len(recent_insights)
            topics = set()
            recent_activity = 0
            
            for insight in recent_insights:
                topics.add(insight.get('topic', ''))
                
                # Check if learning was recent (last 7 days)
                try:
                    insight_timestamp = datetime.fromisoformat(insight.get('timestamp', ''))
                    if (datetime.now() - insight_timestamp).days <= 7:
                        recent_activity += 1
                except:
                    continue
            
            # Calculate progress score
            insight_score = min(insight_count / 50.0, 1.0) * 0.4  # 40% weight
            recency_score = min(recent_activity / max(insight_count, 1), 1.0) * 0.3  # 30% weight
            diversity_score = min(len(topics) / 10.0, 1.0) * 0.3  # 30% weight
            
            total_progress = (insight_score + recency_score + diversity_score) * 100
            
            return min(total_progress, 100.0)
            
        except Exception as e:
            logger.error(f"Error getting internet learning progress for {ai_type}: {str(e)}")
            return 0.0
    
    def get_ai_level(self, ai_type: str) -> int:
        """Get the current level of an AI based on its learning progress"""
        try:
            # Get learning stats for this AI
            learning_stats = self._learning_states.get(ai_type, {})
            
            # Calculate learning score based on various factors
            total_events = len(learning_stats.get('learning_events', []))
            total_improvements = len(learning_stats.get('improvements_learned', []))
            productivity_score = learning_stats.get('productivity_metrics', {}).get('average_productivity_score', 0.0)
            
            # Calculate base score
            base_score = total_events * 10 + total_improvements * 20 + productivity_score * 100
            
            # Determine level based on score thresholds
            if base_score < 100:
                return 1
            elif base_score < 300:
                return 2
            elif base_score < 600:
                return 3
            elif base_score < 1000:
                return 4
            elif base_score < 1500:
                return 5
            elif base_score < 2200:
                return 6
            elif base_score < 3000:
                return 7
            elif base_score < 4000:
                return 8
            elif base_score < 5000:
                return 9
            else:
                return 10
                
        except Exception as e:
            logger.error(f"Error getting AI level for {ai_type}: {str(e)}")
            return 1  # Default to level 1

    async def trigger_internet_learning(self, ai_type: str, topics: List[str] = None) -> bool:
        """Trigger internet learning for an AI type"""
        try:
            if not topics:
                # Default topics based on AI type
                if ai_type.lower() == "imperium":
                    topics = [
                        "system architecture best practices",
                        "performance optimization techniques",
                        "scalability patterns"
                    ]
                elif ai_type.lower() == "guardian":
                    topics = [
                        "security best practices",
                        "input validation techniques",
                        "authentication patterns"
                    ]
                elif ai_type.lower() == "sandbox":
                    topics = [
                        "experimental development patterns",
                        "A/B testing methodologies",
                        "rapid prototyping techniques"
                    ]
                elif ai_type.lower() == "conquest":
                    topics = [
                        "user experience design",
                        "frontend optimization",
                        "mobile app development"
                    ]
                else:
                    topics = [
                        "software development best practices",
                        "code quality improvement",
                        "testing methodologies"
                    ]
            
            # Store learning trigger
            await self.store_internet_learning(ai_type, topics, datetime.now())
            
            logger.info(f"Triggered internet learning for {ai_type}", topics=len(topics))
            return True
            
        except Exception as e:
            logger.error(f"Error triggering internet learning for {ai_type}: {str(e)}")
            return False 

    def _get_level_thresholds(self, learning_score: float, ai_type: str) -> dict:
        # Match frontend logic for level thresholds - updated for higher requirements
        # New thresholds: 50k, 200k, 500k, 1M, 2M, 5M, 10M, 15M, 20M
        thresholds = [0, 50000, 200000, 500000, 1000000, 2000000, 5000000, 10000000, 15000000, 20000000]
        
        for i, threshold in enumerate(thresholds):
            if learning_score < threshold:
                return {
                    'level': i + 1,
                    'current': thresholds[i - 1] if i > 0 else 0,
                    'next': threshold
                }
        return {
            'level': len(thresholds) + 1,
            'current': thresholds[-1],
            'next': thresholds[-1] * 1.5  # Next level is 50% more than current max
        }

    def _calculate_level_and_progress(self, learning_score: float, ai_type: str) -> dict:
        thresholds = self._get_level_thresholds(learning_score, ai_type)
        level = thresholds['level']
        current_level_min = thresholds['current']
        next_level_min = thresholds['next']
        progress = learning_score - current_level_min
        progress = max(0, progress)
        progress_to_next = next_level_min - current_level_min
        progress_percent = progress / progress_to_next if progress_to_next > 0 else 1.0
        return {
            'level': level,
            'progress': progress,
            'progress_percent': progress_percent,
            'next_level_threshold': next_level_min
        }

    async def get_ai_level_status(self, ai_type: str) -> dict:
        # Get the current learning score for the AI
        from ..models.sql_models import AgentMetrics
        from sqlalchemy import select
        async with get_session() as session:
            stmt = select(AgentMetrics).where(AgentMetrics.agent_id == ai_type)
            result = await session.execute(stmt)
            metrics = result.scalar_one_or_none()
            learning_score = metrics.learning_score if metrics else 0.0
            level_info = self._calculate_level_and_progress(learning_score, ai_type)
            return {
                'ai_type': ai_type,
                'learning_score': learning_score,
                'level': level_info['level'],
                'progress': level_info['progress'],
                'progress_percent': level_info['progress_percent'],
                'next_level_threshold': level_info['next_level_threshold']
            }

    async def _append_learning_pattern_and_persist(self, ai_type: str, pattern: str):
        """Append a learning pattern to the agent's metrics and persist to DB."""
        try:
            from app.services.imperium_learning_controller import ImperiumLearningController
            controller = ImperiumLearningController()
            if ai_type not in controller._agent_metrics:
                logger.warning(f"[LEARNING] No in-memory metrics for {ai_type}, cannot append pattern.")
                return
            metrics = controller._agent_metrics[ai_type]
            if pattern not in metrics.learning_patterns:
                metrics.learning_patterns.append(pattern)
                await controller.persist_agent_metrics(ai_type)
                logger.info(f"[LEARNING] Appended pattern and persisted metrics for {ai_type}: {pattern}")
        except Exception as e:
            logger.error(f"[LEARNING] Error appending pattern and persisting for {ai_type}: {str(e)}")

    async def active_learning_cycle(self, ai_type: str):
        """AI generates self-queries for its own knowledge gaps and learns from them live."""
        knowledge_gaps = await self.identify_knowledge_gaps(ai_type)
        for gap in knowledge_gaps:
            # Generate a self-query and answer it using SCKIPIT/LLM
            self_query = f"What do I (as {ai_type}) not know about: {gap}?"
            answer = await self.sckipit_service.generate_answer_with_llm(self_query, await self.get_learning_log(ai_type))
            await self.log_answer(ai_type, self_query, answer)
            # Optionally, trigger internet learning for the gap
            await self.trigger_internet_learning(ai_type, topics=[gap])

    async def reinforcement_learning_update(self, ai_type: str, prompt: str, answer: str, evaluation: Dict):
        """Update AI's model with reward/penalty based on answer quality and evaluation."""
        score = evaluation.get("score", 0)
        reward = 1 if score >= 99 else -1
        # Update ML model with reward/penalty
        await self.enhanced_ml_service.update_model_with_feedback(ai_type, prompt, answer, reward)
        # Log the learning event
        await self.log_answer(ai_type, prompt, answer)

    async def meta_learning_reflection(self, ai_type: str):
        """AI reflects on its own performance, adapts strategies, and optimizes learning."""
        insights = await self.get_learning_insights(ai_type)
        # Analyze performance trends and adapt learning strategy
        await self.enhanced_ml_service.optimize_learning_strategy(ai_type, insights)
        # Persist meta-learning event
        await self._append_learning_pattern_and_persist(ai_type, "Meta-learning reflection and strategy update.")

    async def log_answer(self, ai_type: str, prompt: str, answer: str, structured_response: Dict[str, Any] = None):
        """
        Log an AI's answer with full explainability data including reasoning trace, self-assessment, and confidence.
        Now persists data to the Neon database for permanent storage.
        
        Args:
            ai_type: The type of AI (imperium, guardian, sandbox, conquest)
            prompt: The original prompt/question
            answer: The AI's answer
            structured_response: Full structured response with explainability features
        """
        try:
            # Create learning record with explainability data
            learning_record = {
                'timestamp': datetime.now().isoformat(),
                'ai_type': ai_type,
                'prompt': prompt,
                'answer': answer,
                'explainability_data': {
                    'reasoning_trace': structured_response.get('reasoning_trace', 'No reasoning provided') if structured_response else 'No structured response',
                    'self_assessment': structured_response.get('self_assessment', {}) if structured_response else {},
                    'confidence_score': structured_response.get('confidence_score', 50) if structured_response else 50,
                    'uncertainty_areas': structured_response.get('uncertainty_areas', []) if structured_response else [],
                    'reasoning_quality': structured_response.get('reasoning_quality', 'unknown') if structured_response else 'unknown',
                    'knowledge_applied': structured_response.get('knowledge_applied', []) if structured_response else [],
                    'is_fallback': structured_response.get('is_fallback', False) if structured_response else True,
                    'error_analysis': structured_response.get('error_analysis') if structured_response else None,
                    'uncertainty_quantification': structured_response.get('uncertainty_quantification') if structured_response else None,
                    'model_provenance': structured_response.get('model_provenance') if structured_response else None,
                    'peer_review_feedback': structured_response.get('peer_review_feedback') if structured_response else None,
                },
                'learning_context_used': structured_response.get('learning_context_used', False) if structured_response else False,
                'prompt_length': len(prompt),
                'answer_length': len(answer),
                'source': 'ai_answer'
            }
            
            # Add to learning data (in-memory)
            self._learning_data.append(learning_record)
            
            # PERSIST TO DATABASE - Store AI answer with explainability data
            await self._persist_ai_answer_to_database(ai_type, prompt, answer, structured_response)
            
            # Update learning state with explainability insights
            if ai_type not in self._learning_states:
                self._learning_states[ai_type] = {
                    'learning_events': [],
                    'improvements_learned': [],
                    'failure_patterns': [],
                    'success_patterns': [],
                    'explainability_metrics': {},
                    'last_learning': None
                }
            
            # Track explainability metrics
            explainability_metrics = self._learning_states[ai_type].get('explainability_metrics', {})
            
            # Update confidence tracking
            confidence_scores = explainability_metrics.get('confidence_scores', [])
            confidence_scores.append(structured_response.get('confidence_score', 50) if structured_response else 50)
            if len(confidence_scores) > 100:  # Keep last 100 scores
                confidence_scores = confidence_scores[-100:]
            explainability_metrics['confidence_scores'] = confidence_scores
            
            # Track reasoning quality
            reasoning_quality = structured_response.get('reasoning_quality', 'unknown') if structured_response else 'unknown'
            quality_counts = explainability_metrics.get('reasoning_quality_counts', {})
            quality_counts[reasoning_quality] = quality_counts.get(reasoning_quality, 0) + 1
            explainability_metrics['reasoning_quality_counts'] = quality_counts
            
            # Track uncertainty patterns
            uncertainty_areas = structured_response.get('uncertainty_areas', []) if structured_response else []
            uncertainty_patterns = explainability_metrics.get('uncertainty_patterns', {})
            for area in uncertainty_areas:
                uncertainty_patterns[area] = uncertainty_patterns.get(area, 0) + 1
            explainability_metrics['uncertainty_patterns'] = uncertainty_patterns
            
            # Calculate average confidence
            if confidence_scores:
                explainability_metrics['average_confidence'] = sum(confidence_scores) / len(confidence_scores)
            
            # Update learning state
            self._learning_states[ai_type]['explainability_metrics'] = explainability_metrics
            self._learning_states[ai_type]['last_learning'] = datetime.now().isoformat()
            
            # Add learning event
            self._learning_states[ai_type]['learning_events'].append({
                'timestamp': datetime.now().isoformat(),
                'event': 'ai_answer_logged',
                'prompt_length': len(prompt),
                'confidence_score': structured_response.get('confidence_score', 50) if structured_response else 50,
                'reasoning_quality': reasoning_quality,
                'has_uncertainty': len(uncertainty_areas) > 0
            })
            
            # PERSIST LEARNING RECORD TO DATABASE
            await self._persist_learning_record_to_database(ai_type, 'ai_answer_logged', learning_record, structured_response)
            
            # PERSIST EXPLAINABILITY METRICS TO DATABASE
            await self._persist_explainability_metrics_to_database(ai_type, explainability_metrics)
            
            # Keep only last 1000 learning events
            if len(self._learning_states[ai_type]['learning_events']) > 1000:
                self._learning_states[ai_type]['learning_events'] = self._learning_states[ai_type]['learning_events'][-1000:]
            
            # Keep only last 1000 learning records
            if len(self._learning_data) > 1000:
                self._learning_data = self._learning_data[-1000:]
            
            logger.info(f"Logged AI answer with explainability data for {ai_type} (persisted to database)", 
                       confidence_score=structured_response.get('confidence_score', 50) if structured_response else 50,
                       reasoning_quality=reasoning_quality,
                       uncertainty_count=len(uncertainty_areas))
            
        except Exception as e:
            logger.error(f"Error logging AI answer for {ai_type}: {str(e)}")

    async def _persist_ai_answer_to_database(self, ai_type: str, prompt: str, answer: str, structured_response: Dict[str, Any] = None):
        """Persist AI answer with explainability data to the database"""
        try:
            session = get_session()
            async with session as s:
                from ..models.sql_models import AIAnswer
                
                # Create AI answer record
                ai_answer = AIAnswer(
                    ai_type=ai_type,
                    prompt=prompt,
                    answer=answer,
                    reasoning_trace=structured_response.get('reasoning_trace') if structured_response else None,
                    confidence_score=structured_response.get('confidence_score', 50.0) if structured_response else 50.0,
                    reasoning_quality=structured_response.get('reasoning_quality') if structured_response else None,
                    uncertainty_areas=structured_response.get('uncertainty_areas', []) if structured_response else [],
                    knowledge_applied=structured_response.get('knowledge_applied', []) if structured_response else [],
                    is_fallback=structured_response.get('is_fallback', False) if structured_response else True,
                    self_assessment=structured_response.get('self_assessment') if structured_response else None,
                    learning_context_used=structured_response.get('learning_context_used', False) if structured_response else False,
                    learning_log=structured_response.get('learning_log') if structured_response else None,
                    error_analysis=structured_response.get('error_analysis') if structured_response else None,
                    uncertainty_quantification=structured_response.get('uncertainty_quantification') if structured_response else None,
                    model_provenance=structured_response.get('model_provenance') if structured_response else None,
                    peer_review_feedback=structured_response.get('peer_review_feedback') if structured_response else None,
                    prompt_length=len(prompt),
                    answer_length=len(answer),
                    source='ai_answer'
                )
                
                s.add(ai_answer)
                await s.commit()
                
                logger.info(f"Persisted AI answer to database for {ai_type}")
                
        except Exception as e:
            logger.error(f"Error persisting AI answer to database for {ai_type}: {str(e)}")

    async def _persist_learning_record_to_database(self, ai_type: str, learning_event: str, learning_data: Dict, structured_response: Dict[str, Any] = None):
        """Persist learning record to the database"""
        try:
            session = get_session()
            async with session as s:
                from ..models.sql_models import LearningRecord
                
                # Create learning record
                learning_record = LearningRecord(
                    ai_type=ai_type,
                    learning_event=learning_event,
                    learning_data=learning_data,
                    impact_score=structured_response.get('confidence_score', 50.0) if structured_response else 50.0,
                    explainability_data=structured_response,
                    confidence_score=structured_response.get('confidence_score', 50.0) if structured_response else 50.0,
                    reasoning_quality=structured_response.get('reasoning_quality') if structured_response else None,
                    has_uncertainty=len(structured_response.get('uncertainty_areas', [])) > 0 if structured_response else False,
                    prompt_length=learning_data.get('prompt_length', 0),
                    learning_context_used=learning_data.get('learning_context_used', False)
                )
                
                s.add(learning_record)
                await s.commit()
                
                logger.info(f"Persisted learning record to database for {ai_type}")
                
        except Exception as e:
            logger.error(f"Error persisting learning record to database for {ai_type}: {str(e)}")

    async def _persist_explainability_metrics_to_database(self, ai_type: str, explainability_metrics: Dict):
        """Persist explainability metrics to the database"""
        try:
            session = get_session()
            async with session as s:
                from ..models.sql_models import ExplainabilityMetrics
                from sqlalchemy import select
                
                # Get or create explainability metrics record
                result = await s.execute(
                    select(ExplainabilityMetrics).where(ExplainabilityMetrics.ai_type == ai_type)
                )
                metrics_record = result.scalar_one_or_none()
                
                if not metrics_record:
                    # Create new record
                    metrics_record = ExplainabilityMetrics(
                        ai_type=ai_type,
                        average_confidence=explainability_metrics.get('average_confidence', 0.0),
                        confidence_scores=explainability_metrics.get('confidence_scores', []),
                        confidence_trend=explainability_metrics.get('confidence_scores', [])[-10:] if explainability_metrics.get('confidence_scores') else [],
                        reasoning_quality_counts=explainability_metrics.get('reasoning_quality_counts', {}),
                        uncertainty_patterns=explainability_metrics.get('uncertainty_patterns', {}),
                        top_uncertainty_areas=sorted(
                            explainability_metrics.get('uncertainty_patterns', {}).items(),
                            key=lambda x: x[1],
                            reverse=True
                        )[:5],
                        total_answers_logged=len([r for r in self._learning_data if r.get('ai_type') == ai_type]),
                        answers_with_uncertainty=len([r for r in self._learning_data if r.get('ai_type') == ai_type and r.get('explainability_data', {}).get('uncertainty_areas')]),
                        answers_with_high_confidence=len([r for r in self._learning_data if r.get('ai_type') == ai_type and r.get('explainability_data', {}).get('confidence_score', 0) >= 80])
                    )
                    s.add(metrics_record)
                else:
                    # Update existing record
                    metrics_record.average_confidence = explainability_metrics.get('average_confidence', 0.0)
                    metrics_record.confidence_scores = explainability_metrics.get('confidence_scores', [])
                    metrics_record.confidence_trend = explainability_metrics.get('confidence_scores', [])[-10:] if explainability_metrics.get('confidence_scores') else []
                    metrics_record.reasoning_quality_counts = explainability_metrics.get('reasoning_quality_counts', {})
                    metrics_record.uncertainty_patterns = explainability_metrics.get('uncertainty_patterns', {})
                    metrics_record.top_uncertainty_areas = sorted(
                        explainability_metrics.get('uncertainty_patterns', {}).items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5]
                    metrics_record.total_answers_logged = len([r for r in self._learning_data if r.get('ai_type') == ai_type])
                    metrics_record.answers_with_uncertainty = len([r for r in self._learning_data if r.get('ai_type') == ai_type and r.get('explainability_data', {}).get('uncertainty_areas')])
                    metrics_record.answers_with_high_confidence = len([r for r in self._learning_data if r.get('ai_type') == ai_type and r.get('explainability_data', {}).get('confidence_score', 0) >= 80])
                
                await s.commit()
                
                logger.info(f"Persisted explainability metrics to database for {ai_type}")
                
        except Exception as e:
            logger.error(f"Error persisting explainability metrics to database for {ai_type}: {str(e)}")

    async def get_explainability_analytics(self, ai_type: str = None) -> Dict[str, Any]:
        """
        Get analytics about AI explainability and transparency.
        Now loads data from both memory and database for comprehensive analytics.
        
        Args:
            ai_type: Optional specific AI type, otherwise returns data for all AIs
            
        Returns:
            Dictionary containing explainability analytics
        """
        try:
            analytics = {}
            
            if ai_type:
                # Single AI analytics - combine memory and database data
                analytics[ai_type] = await self._get_ai_explainability_analytics(ai_type)
            else:
                # All AIs analytics
                for ai in ['imperium', 'guardian', 'sandbox', 'conquest']:
                    analytics[ai] = await self._get_ai_explainability_analytics(ai)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting explainability analytics: {str(e)}")
            return {}

    async def _get_ai_explainability_analytics(self, ai_type: str) -> Dict[str, Any]:
        """Get explainability analytics for a specific AI from both memory and database"""
        try:
            # Get memory-based analytics
            memory_analytics = {}
            if ai_type in self._learning_states:
                explainability_metrics = self._learning_states[ai_type].get('explainability_metrics', {})
                memory_analytics = {
                    'average_confidence': explainability_metrics.get('average_confidence', 0),
                    'confidence_trend': explainability_metrics.get('confidence_scores', [])[-10:] if explainability_metrics.get('confidence_scores') else [],
                    'reasoning_quality_distribution': explainability_metrics.get('reasoning_quality_counts', {}),
                    'top_uncertainty_areas': sorted(
                        explainability_metrics.get('uncertainty_patterns', {}).items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5],
                    'total_answers_logged': len([r for r in self._learning_data if r.get('ai_type') == ai_type]),
                    'last_learning': self._learning_states[ai_type].get('last_learning')
                }
            
            # Get database-based analytics
            db_analytics = await self._get_db_explainability_analytics(ai_type)
            
            # Combine analytics (database takes precedence for persistence)
            combined_analytics = {**memory_analytics, **db_analytics}
            
            return combined_analytics
            
        except Exception as e:
            logger.error(f"Error getting AI explainability analytics for {ai_type}: {str(e)}")
            return {}

    async def _get_db_explainability_analytics(self, ai_type: str) -> Dict[str, Any]:
        """Get explainability analytics from the database"""
        try:
            session = get_session()
            async with session as s:
                from ..models.sql_models import ExplainabilityMetrics, AIAnswer
                from sqlalchemy import select, func
                
                # Get explainability metrics from database
                result = await s.execute(
                    select(ExplainabilityMetrics).where(ExplainabilityMetrics.ai_type == ai_type)
                )
                metrics_record = result.scalar_one_or_none()
                
                if metrics_record:
                    return {
                        'average_confidence': metrics_record.average_confidence,
                        'confidence_trend': metrics_record.confidence_trend or [],
                        'reasoning_quality_distribution': metrics_record.reasoning_quality_counts or {},
                        'top_uncertainty_areas': metrics_record.top_uncertainty_areas or [],
                        'total_answers_logged': metrics_record.total_answers_logged,
                        'answers_with_uncertainty': metrics_record.answers_with_uncertainty,
                        'answers_with_high_confidence': metrics_record.answers_with_high_confidence,
                        'last_learning': metrics_record.updated_at.isoformat() if metrics_record.updated_at else None
                    }
                
                # If no metrics record, get basic stats from AI answers
                result = await s.execute(
                    select(func.count(AIAnswer.id)).where(AIAnswer.ai_type == ai_type)
                )
                total_answers = result.scalar() or 0
                
                return {
                    'total_answers_logged': total_answers,
                    'average_confidence': 0,
                    'confidence_trend': [],
                    'reasoning_quality_distribution': {},
                    'top_uncertainty_areas': [],
                    'last_learning': None
                }
                
        except Exception as e:
            logger.error(f"Error getting database explainability analytics for {ai_type}: {str(e)}")
            return {}