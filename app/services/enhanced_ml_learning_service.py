#!/usr/bin/env python3
"""
Enhanced ML Learning Service
============================

This service provides advanced ML capabilities for continuous learning and improvement
of AI systems. It includes:

1. Continuous Model Training with Real Data
2. Adaptive Learning from User Feedback
3. Cross-AI Knowledge Transfer
4. Performance Optimization
5. Automated Model Selection
6. Learning Analytics and Insights
"""

import asyncio
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, VotingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, mean_squared_error, r2_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import logging
from pathlib import Path
import json
import pickle

from ..core.config import settings
from ..core.database import get_session
from ..models.sql_models import Proposal, Learning, AILearningHistory

logger = logging.getLogger(__name__)

class EnhancedMLLearningService:
    """Enhanced ML Learning Service with continuous learning and adaptive improvement"""
    
    _instance = None
    _initialized = False
    _models = {}
    _scalers = {}
    _encoders = {}
    _vectorizers = {}
    _performance_history = []
    _learning_metrics = {}
    _cross_ai_knowledge = {}
    _model_performance_tracker = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_enhanced_ml_models()
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the enhanced ML learning service"""
        if not cls._initialized:
            instance = cls()
            await instance._load_existing_models()
            await instance._load_performance_history()
            await instance._initialize_cross_ai_knowledge()
            cls._initialized = True
            logger.info("Enhanced ML Learning Service initialized")
        return cls()
    
    def _initialize_enhanced_ml_models(self):
        """Initialize enhanced ML models with multiple algorithms"""
        try:
            # Quality prediction models
            self._models['quality_ensemble'] = VotingClassifier([
                ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),
                ('gb', GradientBoostingRegressor(n_estimators=100, random_state=42)),
                ('svm', SVC(probability=True, random_state=42))
            ])
            
            # Approval prediction models
            self._models['approval_ensemble'] = VotingClassifier([
                ('lr', LogisticRegression(random_state=42)),
                ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),
                ('mlp', MLPClassifier(hidden_layer_sizes=(100, 50), random_state=42))
            ])
            
            # Learning pattern recognition
            self._models['pattern_classifier'] = RandomForestClassifier(n_estimators=150, random_state=42)
            
            # Performance prediction
            self._models['performance_predictor'] = GradientBoostingRegressor(n_estimators=200, random_state=42)
            
            # Cross-AI knowledge transfer
            self._models['knowledge_transfer'] = MLPClassifier(hidden_layer_sizes=(200, 100, 50), random_state=42)
            
            # Text analysis for reasoning quality
            self._vectorizers['reasoning_analyzer'] = TfidfVectorizer(max_features=1000, stop_words='english')
            
            # Clustering for pattern discovery
            self._models['pattern_clusterer'] = KMeans(n_clusters=10, random_state=42)
            
            # Initialize scalers and encoders
            self._scalers['feature_scaler'] = StandardScaler()
            self._scalers['quality_scaler'] = StandardScaler()
            self._encoders['ai_type_encoder'] = LabelEncoder()
            self._encoders['improvement_type_encoder'] = LabelEncoder()
            
            logger.info("Enhanced ML models initialized")
            
        except Exception as e:
            logger.error(f"Error initializing enhanced ML models: {str(e)}")
    
    async def _load_existing_models(self):
        """Load existing trained models"""
        try:
            model_dir = Path(settings.ml_model_path) / "enhanced"
            model_dir.mkdir(parents=True, exist_ok=True)
            
            for model_name in self._models.keys():
                model_path = model_dir / f"{model_name}.pkl"
                if model_path.exists():
                    self._models[model_name] = joblib.load(model_path)
                    logger.info(f"Loaded existing model: {model_name}")
            
            # Load scalers and encoders
            for scaler_name in self._scalers.keys():
                scaler_path = model_dir / f"{scaler_name}.pkl"
                if scaler_path.exists():
                    self._scalers[scaler_name] = joblib.load(scaler_path)
            
            for encoder_name in self._encoders.keys():
                encoder_path = model_dir / f"{encoder_name}.pkl"
                if encoder_path.exists():
                    self._encoders[encoder_name] = joblib.load(encoder_path)
                    
        except Exception as e:
            logger.error(f"Error loading existing models: {str(e)}")
    
    async def _save_enhanced_model(self, model_name: str):
        """Save an enhanced ML model"""
        try:
            model_dir = Path(settings.ml_model_path) / "enhanced"
            model_dir.mkdir(parents=True, exist_ok=True)
            
            model_path = model_dir / f"{model_name}.pkl"
            joblib.dump(self._models[model_name], model_path)
            
            # Save scalers and encoders
            if model_name in self._scalers:
                scaler_path = model_dir / f"{model_name}.pkl"
                joblib.dump(self._scalers[model_name], scaler_path)
            
            if model_name in self._encoders:
                encoder_path = model_dir / f"{model_name}.pkl"
                joblib.dump(self._encoders[model_name], encoder_path)
                
        except Exception as e:
            logger.error(f"Error saving enhanced model {model_name}: {str(e)}")
    
    async def _load_performance_history(self):
        """Load performance history for continuous learning"""
        try:
            async with get_session() as session:
                from sqlalchemy import select, desc
                
                # Get recent proposals for performance tracking
                stmt = select(Proposal).order_by(desc(Proposal.created_at)).limit(1000)
                result = await session.execute(stmt)
                proposals = result.scalars().all()
                
                for proposal in proposals:
                    self._performance_history.append({
                        'proposal_id': proposal.id,
                        'ai_type': proposal.ai_type,
                        'user_feedback': proposal.user_feedback,
                        'confidence': proposal.confidence or 0.5,
                        'created_at': proposal.created_at.isoformat(),
                        'improvement_type': proposal.improvement_type,
                        'ai_reasoning': proposal.ai_reasoning
                    })
                
                logger.info(f"Loaded {len(self._performance_history)} performance records")
                
        except Exception as e:
            logger.error(f"Error loading performance history: {str(e)}")
    
    async def _initialize_cross_ai_knowledge(self):
        """Initialize cross-AI knowledge transfer system"""
        try:
            ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
            
            for ai_type in ai_types:
                self._cross_ai_knowledge[ai_type] = {
                    'successful_patterns': [],
                    'failure_patterns': [],
                    'learning_insights': [],
                    'performance_metrics': {},
                    'knowledge_contributions': []
                }
            
            logger.info("Cross-AI knowledge system initialized")
            
        except Exception as e:
            logger.error(f"Error initializing cross-AI knowledge: {str(e)}")
    
    async def train_enhanced_models(self, force_retrain: bool = False) -> Dict[str, Any]:
        """Train enhanced ML models with continuous learning"""
        try:
            logger.info("🔄 Training enhanced ML models...")
            
            # Get comprehensive training data
            training_data = await self._prepare_enhanced_training_data()
            
            if len(training_data) < 100:
                logger.warning("Insufficient data for enhanced training", count=len(training_data))
                return {'status': 'insufficient_data', 'count': len(training_data)}
            
            # Prepare features and targets
            X, y_quality, y_approval, y_performance = await self._extract_enhanced_features(training_data)
            
            # Split data
            X_train, X_test, y_quality_train, y_quality_test, y_approval_train, y_approval_test, y_performance_train, y_performance_test = train_test_split(
                X, y_quality, y_approval, y_performance, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self._scalers['feature_scaler'].fit_transform(X_train)
            X_test_scaled = self._scalers['feature_scaler'].transform(X_test)
            
            # Train ensemble models
            training_results = {}
            
            # Train quality ensemble
            self._models['quality_ensemble'].fit(X_train_scaled, y_quality_train)
            quality_score = self._models['quality_ensemble'].score(X_test_scaled, y_quality_test)
            training_results['quality_ensemble'] = quality_score
            
            # Train approval ensemble
            self._models['approval_ensemble'].fit(X_train_scaled, y_approval_train)
            approval_score = self._models['approval_ensemble'].score(X_test_scaled, y_approval_test)
            training_results['approval_ensemble'] = approval_score
            
            # Train performance predictor
            self._models['performance_predictor'].fit(X_train_scaled, y_performance_train)
            performance_score = self._models['performance_predictor'].score(X_test_scaled, y_performance_test)
            training_results['performance_predictor'] = performance_score
            
            # Train pattern classifier with text features
            text_features = await self._extract_text_features_for_patterns(training_data)
            if len(text_features) > 10:
                self._models['pattern_classifier'].fit(text_features, y_quality_train[:len(text_features)])
                pattern_score = self._models['pattern_classifier'].score(text_features, y_quality_test[:len(text_features)])
                training_results['pattern_classifier'] = pattern_score
            
            # Save models
            for model_name in self._models.keys():
                await self._save_enhanced_model(model_name)
            
            # Update performance tracking
            self._model_performance_tracker[datetime.now().isoformat()] = training_results
            
            logger.info("✅ Enhanced ML models trained successfully", results=training_results)
            
            return {
                'status': 'success',
                'training_results': training_results,
                'models_trained': len(training_results),
                'training_samples': len(X_train)
            }
            
        except Exception as e:
            logger.error(f"Error training enhanced models: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _prepare_enhanced_training_data(self) -> List[Dict[str, Any]]:
        """Prepare comprehensive training data"""
        try:
            async with get_session() as session:
                from sqlalchemy import select, desc
                
                # Get proposals with feedback
                stmt = select(Proposal).where(
                    Proposal.user_feedback.in_(["approved", "rejected"])
                ).order_by(desc(Proposal.created_at)).limit(2000)
                
                result = await session.execute(stmt)
                proposals = result.scalars().all()
                
                training_data = []
                for proposal in proposals:
                    # Extract comprehensive features
                    features = await self._extract_comprehensive_features(proposal)
                    
                    # Calculate quality score
                    quality_score = await self._calculate_enhanced_quality_score(proposal)
                    
                    # Calculate performance score
                    performance_score = await self._calculate_performance_score(proposal)
                    
                    training_data.append({
                        'proposal_id': proposal.id,
                        'features': features,
                        'quality_score': quality_score,
                        'approval': 1 if proposal.user_feedback == "approved" else 0,
                        'performance_score': performance_score,
                        'ai_type': proposal.ai_type,
                        'improvement_type': proposal.improvement_type,
                        'ai_reasoning': proposal.ai_reasoning,
                        'confidence': proposal.confidence or 0.5
                    })
                
                return training_data
                
        except Exception as e:
            logger.error(f"Error preparing enhanced training data: {str(e)}")
            return []
    
    async def _extract_comprehensive_features(self, proposal) -> Dict[str, float]:
        """Extract comprehensive features from proposal"""
        try:
            features = {}
            
            # Basic features
            features['code_length'] = len(proposal.code_before or "") + len(proposal.code_after or "")
            features['reasoning_length'] = len(proposal.ai_reasoning or "")
            features['confidence'] = proposal.confidence or 0.5
            
            # AI type encoding
            ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
            features['ai_type_encoded'] = ai_types.index(proposal.ai_type) if proposal.ai_type in ai_types else 0
            
            # Improvement type encoding
            improvement_types = ["bug_fix", "feature", "optimization", "refactor", "security"]
            features['improvement_type_encoded'] = improvement_types.index(proposal.improvement_type) if proposal.improvement_type in improvement_types else 0
            
            # Code complexity features
            if proposal.code_before and proposal.code_after:
                features['code_complexity'] = await self._calculate_code_complexity(proposal.code_after)
                features['code_similarity'] = await self._calculate_code_similarity(proposal.code_before, proposal.code_after)
                features['lines_changed'] = abs(len(proposal.code_after.split('\n')) - len(proposal.code_before.split('\n')))
            
            # Reasoning quality features
            if proposal.ai_reasoning:
                features['reasoning_sentiment'] = await self._analyze_reasoning_sentiment(proposal.ai_reasoning)
                features['reasoning_keywords'] = await self._extract_reasoning_keywords(proposal.ai_reasoning)
            
            # Time-based features
            if proposal.created_at:
                features['hour_of_day'] = proposal.created_at.hour
                features['day_of_week'] = proposal.created_at.weekday()
            
            # Performance features
            features['previous_success_rate'] = await self._get_previous_success_rate(proposal.ai_type)
            features['ai_experience'] = await self._get_ai_experience_level(proposal.ai_type)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting comprehensive features: {str(e)}")
            return {}
    
    async def _calculate_enhanced_quality_score(self, proposal) -> float:
        """Calculate enhanced quality score"""
        try:
            score = 0.5  # Base score
            
            # User feedback impact
            if proposal.user_feedback == "approved":
                score += 0.3
            elif proposal.user_feedback == "rejected":
                score -= 0.2
            
            # Confidence impact
            if proposal.confidence and proposal.confidence > 0.7:
                score += 0.1
            
            # Reasoning quality impact
            if proposal.ai_reasoning and len(proposal.ai_reasoning) > 100:
                score += 0.1
            
            # Code quality impact
            if proposal.code_after:
                complexity = await self._calculate_code_complexity(proposal.code_after)
                if complexity < 5.0:  # Low complexity is good
                    score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating enhanced quality score: {str(e)}")
            return 0.5
    
    async def _calculate_performance_score(self, proposal) -> float:
        """Calculate performance score"""
        try:
            score = 0.5  # Base score
            
            # Success rate impact
            if proposal.user_feedback == "approved":
                score += 0.3
            
            # Confidence impact
            if proposal.confidence and proposal.confidence > 0.8:
                score += 0.2
            
            # Code improvement impact
            if proposal.code_before and proposal.code_after:
                before_complexity = await self._calculate_code_complexity(proposal.code_before)
                after_complexity = await self._calculate_code_complexity(proposal.code_after)
                if after_complexity < before_complexity:  # Reduced complexity
                    score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {str(e)}")
            return 0.5
    
    async def _extract_enhanced_features(self, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Extract enhanced features for training"""
        try:
            feature_names = [
                'code_length', 'reasoning_length', 'confidence', 'ai_type_encoded',
                'improvement_type_encoded', 'code_complexity', 'code_similarity',
                'lines_changed', 'reasoning_sentiment', 'reasoning_keywords',
                'hour_of_day', 'day_of_week', 'previous_success_rate', 'ai_experience'
            ]
            
            X = []
            y_quality = []
            y_approval = []
            y_performance = []
            
            for data in training_data:
                features = data['features']
                feature_vector = [features.get(name, 0) for name in feature_names]
                X.append(feature_vector)
                y_quality.append(data['quality_score'])
                y_approval.append(data['approval'])
                y_performance.append(data['performance_score'])
            
            return np.array(X), np.array(y_quality), np.array(y_approval), np.array(y_performance)
            
        except Exception as e:
            logger.error(f"Error extracting enhanced features: {str(e)}")
            return np.array([]), np.array([]), np.array([]), np.array([])
    
    async def _extract_text_features_for_patterns(self, training_data: List[Dict[str, Any]]) -> np.ndarray:
        """Extract text features for pattern recognition"""
        try:
            texts = []
            for data in training_data:
                text = f"{data.get('ai_reasoning', '')} {data.get('improvement_type', '')}"
                texts.append(text)
            
            if texts:
                return self._vectorizers['reasoning_analyzer'].fit_transform(texts).toarray()
            return np.array([])
            
        except Exception as e:
            logger.error(f"Error extracting text features: {str(e)}")
            return np.array([])
    
    async def _calculate_code_complexity(self, code: str) -> float:
        """Calculate code complexity score"""
        try:
            if not code:
                return 0.0
            
            lines = code.split('\n')
            complexity = 0.0
            
            for line in lines:
                stripped = line.strip()
                if stripped:
                    # Count control structures
                    if any(keyword in stripped for keyword in ['if', 'for', 'while', 'try', 'except']):
                        complexity += 1
                    # Count function definitions
                    if 'def ' in stripped or 'function' in stripped:
                        complexity += 1
                    # Count nested structures
                    complexity += stripped.count('{') + stripped.count('(')
            
            return min(10.0, complexity / max(1, len(lines)))
            
        except Exception as e:
            logger.error(f"Error calculating code complexity: {str(e)}")
            return 0.0
    
    async def _calculate_code_similarity(self, code_before: str, code_after: str) -> float:
        """Calculate code similarity"""
        try:
            if not code_before or not code_after:
                return 0.0
            
            # Simple similarity based on common lines
            before_lines = set(code_before.split('\n'))
            after_lines = set(code_after.split('\n'))
            
            intersection = before_lines.intersection(after_lines)
            union = before_lines.union(after_lines)
            
            return len(intersection) / max(1, len(union))
            
        except Exception as e:
            logger.error(f"Error calculating code similarity: {str(e)}")
            return 0.0
    
    async def _analyze_reasoning_sentiment(self, reasoning: str) -> float:
        """Analyze reasoning sentiment"""
        try:
            positive_words = ['improve', 'enhance', 'optimize', 'fix', 'better', 'good', 'success']
            negative_words = ['error', 'fail', 'bug', 'problem', 'issue', 'bad', 'wrong']
            
            words = reasoning.lower().split()
            positive_count = sum(1 for word in words if word in positive_words)
            negative_count = sum(1 for word in words if word in negative_words)
            
            total = len(words)
            if total == 0:
                return 0.0
            
            return (positive_count - negative_count) / total
            
        except Exception as e:
            logger.error(f"Error analyzing reasoning sentiment: {str(e)}")
            return 0.0
    
    async def _extract_reasoning_keywords(self, reasoning: str) -> int:
        """Extract reasoning keywords count"""
        try:
            keywords = ['because', 'therefore', 'however', 'additionally', 'furthermore', 'consequently']
            words = reasoning.lower().split()
            return sum(1 for word in words if word in keywords)
            
        except Exception as e:
            logger.error(f"Error extracting reasoning keywords: {str(e)}")
            return 0
    
    async def _get_previous_success_rate(self, ai_type: str) -> float:
        """Get previous success rate for AI type"""
        try:
            recent_proposals = [p for p in self._performance_history if p['ai_type'] == ai_type][-50:]
            if not recent_proposals:
                return 0.5
            
            approved = sum(1 for p in recent_proposals if p['user_feedback'] == 'approved')
            return approved / len(recent_proposals)
            
        except Exception as e:
            logger.error(f"Error getting previous success rate: {str(e)}")
            return 0.5
    
    async def _get_ai_experience_level(self, ai_type: str) -> float:
        """Get AI experience level"""
        try:
            total_proposals = len([p for p in self._performance_history if p['ai_type'] == ai_type])
            return min(1.0, total_proposals / 100.0)  # Normalize to 0-1
            
        except Exception as e:
            logger.error(f"Error getting AI experience level: {str(e)}")
            return 0.5
    
    async def predict_enhanced_quality(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict enhanced quality using ensemble models"""
        try:
            features = await self._extract_comprehensive_features_from_dict(proposal_data)
            
            if not features:
                return {'quality_score': 0.5, 'confidence': 0.5, 'recommendations': []}
            
            # Prepare feature vector
            feature_names = [
                'code_length', 'reasoning_length', 'confidence', 'ai_type_encoded',
                'improvement_type_encoded', 'code_complexity', 'code_similarity',
                'lines_changed', 'reasoning_sentiment', 'reasoning_keywords',
                'hour_of_day', 'day_of_week', 'previous_success_rate', 'ai_experience'
            ]
            
            feature_vector = [features.get(name, 0) for name in feature_names]
            feature_vector = np.array(feature_vector).reshape(1, -1)
            
            # Scale features
            if 'feature_scaler' in self._scalers:
                feature_vector = self._scalers['feature_scaler'].transform(feature_vector)
            
            # Predict quality
            quality_score = self._models['quality_ensemble'].predict_proba(feature_vector)[0][1]
            
            # Predict approval probability
            approval_prob = self._models['approval_ensemble'].predict_proba(feature_vector)[0][1]
            
            # Predict performance
            performance_score = self._models['performance_predictor'].predict(feature_vector)[0]
            
            # Generate recommendations
            recommendations = await self._generate_enhanced_recommendations(features, quality_score)
            
            return {
                'quality_score': float(quality_score),
                'approval_probability': float(approval_prob),
                'performance_score': float(performance_score),
                'confidence': float((quality_score + approval_prob + performance_score) / 3),
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error predicting enhanced quality: {str(e)}")
            return {'quality_score': 0.5, 'confidence': 0.5, 'recommendations': []}
    
    async def _extract_comprehensive_features_from_dict(self, proposal_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract comprehensive features from proposal dictionary"""
        try:
            features = {}
            
            # Basic features
            features['code_length'] = len(proposal_data.get('code_before', '')) + len(proposal_data.get('code_after', ''))
            features['reasoning_length'] = len(proposal_data.get('ai_reasoning', ''))
            features['confidence'] = proposal_data.get('confidence', 0.5)
            
            # AI type encoding
            ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
            features['ai_type_encoded'] = ai_types.index(proposal_data.get('ai_type', 'Imperium')) if proposal_data.get('ai_type') in ai_types else 0
            
            # Improvement type encoding
            improvement_types = ["bug_fix", "feature", "optimization", "refactor", "security"]
            features['improvement_type_encoded'] = improvement_types.index(proposal_data.get('improvement_type', 'feature')) if proposal_data.get('improvement_type') in improvement_types else 0
            
            # Code complexity features
            if proposal_data.get('code_before') and proposal_data.get('code_after'):
                features['code_complexity'] = await self._calculate_code_complexity(proposal_data['code_after'])
                features['code_similarity'] = await self._calculate_code_similarity(proposal_data['code_before'], proposal_data['code_after'])
                features['lines_changed'] = abs(len(proposal_data['code_after'].split('\n')) - len(proposal_data['code_before'].split('\n')))
            
            # Reasoning quality features
            if proposal_data.get('ai_reasoning'):
                features['reasoning_sentiment'] = await self._analyze_reasoning_sentiment(proposal_data['ai_reasoning'])
                features['reasoning_keywords'] = await self._extract_reasoning_keywords(proposal_data['ai_reasoning'])
            
            # Time-based features
            features['hour_of_day'] = datetime.now().hour
            features['day_of_week'] = datetime.now().weekday()
            
            # Performance features
            features['previous_success_rate'] = await self._get_previous_success_rate(proposal_data.get('ai_type', 'Imperium'))
            features['ai_experience'] = await self._get_ai_experience_level(proposal_data.get('ai_type', 'Imperium'))
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features from dict: {str(e)}")
            return {}
    
    async def _generate_enhanced_recommendations(self, features: Dict[str, float], quality_score: float) -> List[str]:
        """Generate enhanced recommendations based on features and quality score"""
        recommendations = []
        
        try:
            # Quality-based recommendations
            if quality_score < 0.3:
                recommendations.append("Consider providing more detailed reasoning for the changes")
                recommendations.append("Review code complexity and consider simplification")
            
            if quality_score < 0.5:
                recommendations.append("Improve code quality by following best practices")
                recommendations.append("Add comprehensive error handling")
            
            # Feature-based recommendations
            if features.get('code_complexity', 0) > 7.0:
                recommendations.append("Code complexity is high - consider breaking into smaller functions")
            
            if features.get('reasoning_length', 0) < 50:
                recommendations.append("Provide more detailed explanation for the proposed changes")
            
            if features.get('code_similarity', 0) < 0.1:
                recommendations.append("Changes are very different from original - ensure functionality is maintained")
            
            if features.get('previous_success_rate', 0.5) < 0.4:
                recommendations.append("Consider learning from previous successful patterns")
            
            # AI-specific recommendations
            ai_type = features.get('ai_type_encoded', 0)
            if ai_type == 0:  # Imperium
                recommendations.append("Imperium: Focus on system-level improvements and monitoring")
            elif ai_type == 1:  # Guardian
                recommendations.append("Guardian: Emphasize security and validation improvements")
            elif ai_type == 2:  # Sandbox
                recommendations.append("Sandbox: Consider experimental approaches with proper testing")
            elif ai_type == 3:  # Conquest
                recommendations.append("Conquest: Focus on user experience and app functionality")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating enhanced recommendations: {str(e)}")
            return ["Apply standard debugging and testing practices"]
    
    async def learn_from_user_feedback(self, proposal_id: str, user_feedback: str, ai_type: str) -> Dict[str, Any]:
        """Learn from user feedback to improve models"""
        try:
            # Get proposal data
            async with get_session() as session:
                from sqlalchemy import select
                
                stmt = select(Proposal).where(Proposal.id == proposal_id)
                result = await session.execute(stmt)
                proposal = result.scalar_one_or_none()
                
                if not proposal:
                    return {'status': 'error', 'message': 'Proposal not found'}
                
                # Extract features
                features = await self._extract_comprehensive_features(proposal)
                
                # Update performance history
                self._performance_history.append({
                    'proposal_id': proposal_id,
                    'ai_type': ai_type,
                    'user_feedback': user_feedback,
                    'confidence': proposal.confidence or 0.5,
                    'created_at': datetime.now().isoformat(),
                    'improvement_type': proposal.improvement_type,
                    'ai_reasoning': proposal.ai_reasoning
                })
                
                # Update cross-AI knowledge
                await self._update_cross_ai_knowledge(ai_type, features, user_feedback)
                
                # Check if retraining is needed
                if len(self._performance_history) % 50 == 0:  # Retrain every 50 new samples
                    await self.train_enhanced_models(force_retrain=True)
                
                return {
                    'status': 'success',
                    'learning_value': await self._calculate_learning_value(features, user_feedback),
                    'models_updated': True
                }
                
        except Exception as e:
            logger.error(f"Error learning from user feedback: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _update_cross_ai_knowledge(self, ai_type: str, features: Dict[str, float], user_feedback: str):
        """Update cross-AI knowledge base"""
        try:
            if ai_type not in self._cross_ai_knowledge:
                self._cross_ai_knowledge[ai_type] = {
                    'successful_patterns': [],
                    'failure_patterns': [],
                    'learning_insights': [],
                    'performance_metrics': {},
                    'knowledge_contributions': []
                }
            
            # Record pattern
            pattern = {
                'features': features,
                'feedback': user_feedback,
                'timestamp': datetime.now().isoformat(),
                'success': user_feedback == 'approved'
            }
            
            if user_feedback == 'approved':
                self._cross_ai_knowledge[ai_type]['successful_patterns'].append(pattern)
            else:
                self._cross_ai_knowledge[ai_type]['failure_patterns'].append(pattern)
            
            # Keep only recent patterns
            max_patterns = 100
            self._cross_ai_knowledge[ai_type]['successful_patterns'] = self._cross_ai_knowledge[ai_type]['successful_patterns'][-max_patterns:]
            self._cross_ai_knowledge[ai_type]['failure_patterns'] = self._cross_ai_knowledge[ai_type]['failure_patterns'][-max_patterns:]
            
        except Exception as e:
            logger.error(f"Error updating cross-AI knowledge: {str(e)}")
    
    async def _calculate_learning_value(self, features: Dict[str, float], user_feedback: str) -> float:
        """Calculate learning value from feedback"""
        try:
            learning_value = 0.5  # Base value
            
            # Feedback impact
            if user_feedback == 'approved':
                learning_value += 0.3
            else:
                learning_value += 0.2  # Learning from failures is valuable
            
            # Feature complexity impact
            if features.get('code_complexity', 0) > 5.0:
                learning_value += 0.1
            
            # Reasoning quality impact
            if features.get('reasoning_length', 0) > 100:
                learning_value += 0.1
            
            return min(1.0, learning_value)
            
        except Exception as e:
            logger.error(f"Error calculating learning value: {str(e)}")
            return 0.5
    
    async def get_enhanced_ml_analytics(self) -> Dict[str, Any]:
        """Get comprehensive ML analytics"""
        try:
            analytics = {
                'model_performance': self._model_performance_tracker,
                'performance_history': {
                    'total_records': len(self._performance_history),
                    'recent_activity': len([p for p in self._performance_history if datetime.fromisoformat(p['created_at']) > datetime.now() - timedelta(days=7)]),
                    'ai_type_distribution': {},
                    'success_rate': 0.0
                },
                'cross_ai_knowledge': {
                    'ai_types': list(self._cross_ai_knowledge.keys()),
                    'total_patterns': sum(len(data['successful_patterns']) + len(data['failure_patterns']) for data in self._cross_ai_knowledge.values()),
                    'knowledge_transfer_opportunities': await self._identify_knowledge_transfer_opportunities()
                },
                'learning_metrics': {
                    'models_trained': len(self._models),
                    'last_training': max(self._model_performance_tracker.keys()) if self._model_performance_tracker else None,
                    'training_frequency': 'continuous'
                }
            }
            
            # Calculate success rate
            if self._performance_history:
                approved = sum(1 for p in self._performance_history if p['user_feedback'] == 'approved')
                analytics['performance_history']['success_rate'] = approved / len(self._performance_history)
            
            # Calculate AI type distribution
            for record in self._performance_history:
                ai_type = record['ai_type']
                analytics['performance_history']['ai_type_distribution'][ai_type] = analytics['performance_history']['ai_type_distribution'].get(ai_type, 0) + 1
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting enhanced ML analytics: {str(e)}")
            return {'error': str(e)}
    
    async def _identify_knowledge_transfer_opportunities(self) -> List[Dict[str, Any]]:
        """Identify opportunities for cross-AI knowledge transfer"""
        try:
            opportunities = []
            
            for ai_type, knowledge in self._cross_ai_knowledge.items():
                successful_patterns = knowledge['successful_patterns']
                failure_patterns = knowledge['failure_patterns']
                
                if len(successful_patterns) > 10:
                    # Find patterns that could benefit other AIs
                    for pattern in successful_patterns[-5:]:  # Recent successful patterns
                        opportunities.append({
                            'source_ai': ai_type,
                            'pattern_type': 'successful',
                            'confidence': pattern.get('features', {}).get('confidence', 0.5),
                            'transfer_value': await self._calculate_transfer_value(pattern)
                        })
                
                if len(failure_patterns) > 5:
                    # Find failure patterns to avoid
                    for pattern in failure_patterns[-3:]:  # Recent failure patterns
                        opportunities.append({
                            'source_ai': ai_type,
                            'pattern_type': 'failure_avoidance',
                            'confidence': pattern.get('features', {}).get('confidence', 0.5),
                            'transfer_value': await self._calculate_transfer_value(pattern)
                        })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error identifying knowledge transfer opportunities: {str(e)}")
            return []
    
    async def _calculate_transfer_value(self, pattern: Dict[str, Any]) -> float:
        """Calculate the value of transferring a pattern"""
        try:
            features = pattern.get('features', {})
            
            # Higher confidence patterns are more valuable
            confidence = features.get('confidence', 0.5)
            
            # More complex patterns are more valuable
            complexity = features.get('code_complexity', 0)
            complexity_value = min(1.0, complexity / 10.0)
            
            # Recent patterns are more valuable
            timestamp = pattern.get('timestamp')
            if timestamp:
                age_hours = (datetime.now() - datetime.fromisoformat(timestamp)).total_seconds() / 3600
                recency_value = max(0.1, 1.0 - (age_hours / 168))  # Decay over a week
            
            transfer_value = (confidence + complexity_value + recency_value) / 3
            return min(1.0, transfer_value)
            
        except Exception as e:
            logger.error(f"Error calculating transfer value: {str(e)}")
            return 0.5
    
    async def apply_knowledge_transfer(self, source_ai: str, target_ai: str, pattern_type: str) -> Dict[str, Any]:
        """Apply knowledge transfer between AIs"""
        try:
            if source_ai not in self._cross_ai_knowledge or target_ai not in self._cross_ai_knowledge:
                return {'status': 'error', 'message': 'AI types not found in knowledge base'}
            
            source_knowledge = self._cross_ai_knowledge[source_ai]
            
            if pattern_type == 'successful':
                patterns = source_knowledge['successful_patterns']
            else:
                patterns = source_knowledge['failure_patterns']
            
            if not patterns:
                return {'status': 'error', 'message': 'No patterns available for transfer'}
            
            # Select best pattern for transfer
            best_pattern = max(patterns, key=lambda p: p.get('features', {}).get('confidence', 0))
            
            # Apply pattern to target AI
            self._cross_ai_knowledge[target_ai]['knowledge_contributions'].append({
                'source_ai': source_ai,
                'pattern': best_pattern,
                'applied_at': datetime.now().isoformat(),
                'pattern_type': pattern_type
            })
            
            return {
                'status': 'success',
                'transferred_pattern': best_pattern,
                'target_ai': target_ai,
                'transfer_value': await self._calculate_transfer_value(best_pattern)
            }
            
        except Exception as e:
            logger.error(f"Error applying knowledge transfer: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_enhanced_learning_status(self) -> Dict[str, Any]:
        """Get enhanced learning service status"""
        return {
            'status': 'active',
            'models_loaded': len(self._models),
            'performance_history_size': len(self._performance_history),
            'cross_ai_knowledge_size': sum(len(data['successful_patterns']) + len(data['failure_patterns']) for data in self._cross_ai_knowledge.values()),
            'last_training': max(self._model_performance_tracker.keys()) if self._model_performance_tracker else None,
            'knowledge_transfer_opportunities': len(await self._identify_knowledge_transfer_opportunities()),
            'continuous_learning_active': True
        } 