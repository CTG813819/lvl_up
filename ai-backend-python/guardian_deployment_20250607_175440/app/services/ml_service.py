"""
Machine Learning Service using scikit-learn
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob

from ..core.config import settings
from ..core.database import get_session

logger = structlog.get_logger()


class MLService:
    """Machine Learning service using scikit-learn"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.models = {}
            self.scalers = {}
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the ML service"""
        instance = cls()
        
        # Download NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            logger.warning("Failed to download NLTK data", error=str(e))
        
        # Create model directory
        os.makedirs(settings.ml_model_path, exist_ok=True)
        
        # Load existing models
        await instance._load_models()
        
        logger.info("ML Service initialized successfully")
    
    async def _load_models(self):
        """Load existing trained models"""
        model_files = [
            'proposal_classifier.pkl',
            'confidence_predictor.pkl'
        ]
        
        for model_file in model_files:
            model_path = os.path.join(settings.ml_model_path, model_file)
            if os.path.exists(model_path):
                try:
                    with open(model_path, 'rb') as f:
                        model_name = model_file.replace('.pkl', '')
                        self.models[model_name] = pickle.load(f)
                    logger.info(f"Loaded model: {model_name}")
                except Exception as e:
                    logger.error(f"Failed to load model {model_file}", error=str(e))
    
    async def _save_model(self, model, model_name: str):
        """Save a trained model"""
        model_path = os.path.join(settings.ml_model_path, f"{model_name}.pkl")
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            logger.info(f"Saved model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to save model {model_name}", error=str(e))
    
    async def extract_features(self, proposal_data) -> Dict[str, Any]:
        """Extract features from a proposal for ML analysis"""
        features = {}
        
        # Text features
        code_before = proposal_data.code_before or ''
        code_after = proposal_data.code_after or ''
        
        features['code_length_before'] = len(code_before)
        features['code_length_after'] = len(code_after)
        features['code_length_ratio'] = len(code_after) / max(len(code_before), 1)
        
        # File type features
        file_path = proposal_data.file_path or ''
        file_ext = file_path.split('.')[-1] if '.' in file_path else 'unknown'
        features['file_extension'] = file_ext
        
        # AI type encoding
        ai_type = proposal_data.ai_type or 'Imperium'
        ai_type_encoding = {'Imperium': 0, 'Guardian': 1, 'Sandbox': 2}
        features['ai_type_encoded'] = ai_type_encoding.get(ai_type, 0)
        
        # Text analysis features
        ai_reasoning = proposal_data.ai_reasoning or ''
        if ai_reasoning:
            blob = TextBlob(ai_reasoning)
            features['reasoning_sentiment'] = blob.sentiment.polarity
            features['reasoning_subjectivity'] = blob.sentiment.subjectivity
            features['reasoning_length'] = len(ai_reasoning)
        
        # Code complexity features
        features['lines_added'] = code_after.count('\n') - code_before.count('\n')
        features['characters_added'] = len(code_after) - len(code_before)
        
        # Improvement type encoding
        improvement_type = proposal_data.improvement_type or ''
        improvement_types = ['performance', 'readability', 'security', 'bug-fix', 'refactor', 'feature', 'system']
        features['improvement_type_encoded'] = improvement_types.index(improvement_type) if improvement_type in improvement_types else -1
        
        return features
    
    async def analyze_proposal_quality(self, proposal_data) -> Dict[str, Any]:
        """Analyze the quality of a proposal using ML"""
        features = await self.extract_features(proposal_data)
        
        # Text analysis
        text_features = await self._extract_text_features(proposal_data)
        features.update(text_features)
        
        # Code analysis
        code_features = await self._extract_code_features(proposal_data)
        features.update(code_features)
        
        # Predict quality score
        quality_score = await self._predict_quality_score(features)
        
        # Predict approval probability
        approval_prob = await self._predict_approval_probability(features)
        
        return {
            'quality_score': quality_score,
            'approval_probability': approval_prob,
            'features': features,
            'recommendations': await self._generate_recommendations(features, quality_score)
        }
    
    async def _extract_text_features(self, proposal_data) -> Dict[str, Any]:
        """Extract text-based features"""
        features = {}
        
        ai_reasoning = proposal_data.ai_reasoning or ''
        if ai_reasoning:
            # Tokenize and analyze reasoning
            tokens = word_tokenize(ai_reasoning.lower())
            
            # Remove stopwords
            stop_words = set(stopwords.words('english'))
            tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
            
            features['reasoning_token_count'] = len(tokens)
            features['reasoning_unique_tokens'] = len(set(tokens))
            features['reasoning_lexical_diversity'] = len(set(tokens)) / max(len(tokens), 1)
        
        return features
    
    async def _extract_code_features(self, proposal_data) -> Dict[str, Any]:
        """Extract code-based features"""
        features = {}
        
        code_after = proposal_data.code_after or ''
        code_before = proposal_data.code_before or ''
        
        # Code complexity metrics
        features['code_complexity'] = await self._calculate_code_complexity(code_after)
        features['code_similarity'] = await self._calculate_code_similarity(code_before, code_after)
        
        # Language-specific features
        file_path = proposal_data.file_path or ''
        if file_path.endswith('.dart'):
            features['dart_specific'] = await self._extract_dart_features(code_after)
        
        return features
    
    async def _calculate_code_complexity(self, code: str) -> float:
        """Calculate code complexity score"""
        lines = code.split('\n')
        complexity = 0
        
        for line in lines:
            line = line.strip()
            if line:
                # Count control structures
                if any(keyword in line for keyword in ['if', 'for', 'while', 'switch', 'case']):
                    complexity += 1
                # Count function definitions
                if any(keyword in line for keyword in ['def ', 'function ', 'void ', 'int ', 'String ']):
                    complexity += 1
                # Count nested structures
                complexity += line.count('{') + line.count('(')
        
        return complexity / max(len(lines), 1)
    
    async def _calculate_code_similarity(self, code_before: str, code_after: str) -> float:
        """Calculate similarity between code before and after"""
        # Simple Jaccard similarity on lines
        lines_before = set(code_before.split('\n'))
        lines_after = set(code_after.split('\n'))
        
        intersection = len(lines_before.intersection(lines_after))
        union = len(lines_before.union(lines_after))
        
        return intersection / max(union, 1)
    
    async def _extract_dart_features(self, code: str) -> Dict[str, Any]:
        """Extract Dart-specific features"""
        features = {}
        
        # Dart-specific patterns
        features['has_async'] = 'async' in code
        features['has_await'] = 'await' in code
        features['has_future'] = 'Future' in code
        features['has_stream'] = 'Stream' in code
        features['has_widget'] = 'Widget' in code
        features['has_build'] = 'build(' in code
        features['has_setstate'] = 'setState' in code
        
        return features
    
    async def _predict_quality_score(self, features: Dict[str, Any]) -> float:
        """Predict quality score using trained model"""
        if 'quality_predictor' not in self.models:
            return 0.5  # Default score
        
        try:
            # Convert features to array
            feature_names = [
                'code_length_ratio', 'reasoning_sentiment', 'reasoning_length',
                'lines_added', 'code_complexity', 'code_similarity'
            ]
            
            feature_vector = [features.get(name, 0) for name in feature_names]
            feature_vector = np.array(feature_vector).reshape(1, -1)
            
            # Scale features if scaler exists
            if 'quality_scaler' in self.scalers:
                feature_vector = self.scalers['quality_scaler'].transform(feature_vector)
            
            # Predict
            score = self.models['quality_predictor'].predict(feature_vector)[0]
            return float(np.clip(score, 0, 1))
            
        except Exception as e:
            logger.error("Error predicting quality score", error=str(e))
            return 0.5
    
    async def _predict_approval_probability(self, features: Dict[str, Any]) -> float:
        """Predict approval probability"""
        if 'approval_predictor' not in self.models:
            return 0.5  # Default probability
        
        try:
            # Convert features to array
            feature_names = [
                'code_length_ratio', 'reasoning_sentiment', 'reasoning_length',
                'lines_added', 'code_complexity', 'code_similarity',
                'ai_type_encoded', 'improvement_type_encoded'
            ]
            
            feature_vector = [features.get(name, 0) for name in feature_names]
            feature_vector = np.array(feature_vector).reshape(1, -1)
            
            # Scale features if scaler exists
            if 'approval_scaler' in self.scalers:
                feature_vector = self.scalers['approval_scaler'].transform(feature_vector)
            
            # Predict probability
            prob = self.models['approval_predictor'].predict_proba(feature_vector)[0]
            return float(prob[1])  # Probability of approval
            
        except Exception as e:
            logger.error("Error predicting approval probability", error=str(e))
            return 0.5
    
    async def _generate_recommendations(self, features: Dict[str, Any], quality_score: float) -> List[str]:
        """Generate recommendations based on features and quality score"""
        recommendations = []
        
        if quality_score < 0.3:
            recommendations.append("Consider providing more detailed reasoning for the changes")
        
        if features.get('code_complexity', 0) > 10:
            recommendations.append("Code changes are complex - consider breaking into smaller improvements")
        
        if features.get('reasoning_length', 0) < 50:
            recommendations.append("Provide more detailed explanation for the proposed changes")
        
        if features.get('code_similarity', 0) < 0.1:
            recommendations.append("Changes are very different from original - ensure they maintain functionality")
        
        return recommendations
    
    async def train_models(self, force_retrain: bool = False):
        """Train ML models using historical proposal data"""
        try:
            from sqlalchemy import select
            from ..models.sql_models import Proposal
            
            session = get_session()
            try:
                # Get training data
                stmt = select(Proposal).where(
                    Proposal.user_feedback.in_(["approved", "rejected"])
                ).limit(1000)
                
                result = await session.execute(stmt)
                proposals = result.scalars().all()
                
                if len(proposals) < 50:
                    logger.warning("Insufficient data for training", count=len(proposals))
                    return
                
                # Prepare training data
                X = []
                y_quality = []
                y_approval = []
                
                for proposal_data in proposals:
                    features = await self.extract_features(proposal_data)
                    
                    # Quality score (simplified heuristic)
                    quality_score = 0.5
                    if proposal_data.user_feedback == "approved":
                        quality_score += 0.3
                    if proposal_data.confidence and proposal_data.confidence > 0.7:
                        quality_score += 0.2
                    if proposal_data.ai_reasoning and len(proposal_data.ai_reasoning) > 100:
                        quality_score += 0.1
                    
                    X.append(list(features.values()))
                    y_quality.append(quality_score)
                    y_approval.append(1 if proposal_data.user_feedback == "approved" else 0)
                
                X = np.array(X)
                y_quality = np.array(y_quality)
                y_approval = np.array(y_approval)
                
                # Split data
                X_train, X_test, y_quality_train, y_quality_test, y_approval_train, y_approval_test = train_test_split(
                    X, y_quality, y_approval, test_size=0.2, random_state=42
                )
                
                # Train quality predictor
                quality_model = GradientBoostingClassifier(random_state=42)
                quality_model.fit(X_train, y_quality_train)
                
                # Train approval predictor
                approval_model = RandomForestClassifier(random_state=42, n_estimators=100)
                approval_model.fit(X_train, y_approval_train)
                
                # Evaluate models
                quality_score = quality_model.score(X_test, y_quality_test)
                approval_score = approval_model.score(X_test, y_approval_test)
                
                logger.info("Model training completed", 
                           quality_accuracy=quality_score, 
                           approval_accuracy=approval_score)
                
                # Save models
                self.models['quality_predictor'] = quality_model
                self.models['approval_predictor'] = approval_model
                
                await self._save_model(quality_model, 'quality_predictor')
                await self._save_model(approval_model, 'approval_predictor')
                
            except Exception as e:
                logger.error("Error training models", error=str(e))
            finally:
                await session.close()
            
        except Exception as e:
            logger.error("Error in train_models", error=str(e))
    
    async def get_ml_insights(self) -> Dict[str, Any]:
        """Get insights from ML analysis"""
        try:
            from sqlalchemy import select, desc
            from ..models.sql_models import Proposal
            
            session = get_session()
            try:
                # Get recent proposals
                stmt = select(Proposal).order_by(desc(Proposal.created_at)).limit(100)
                result = await session.execute(stmt)
                recent_proposals = result.scalars().all()
                
                insights = {
                    'total_proposals': len(recent_proposals),
                    'approval_rate': 0,
                    'average_confidence': 0,
                    'common_improvement_types': {},
                    'quality_trends': [],
                    'recommendations': []
                }
                
                if recent_proposals:
                    # Calculate approval rate
                    approved = sum(1 for p in recent_proposals if p.user_feedback == 'approved')
                    insights['approval_rate'] = approved / len(recent_proposals)
                    
                    # Average confidence
                    confidences = [p.confidence or 0.5 for p in recent_proposals]
                    insights['average_confidence'] = sum(confidences) / len(confidences)
                    
                    # Common improvement types
                    improvement_types = [p.improvement_type for p in recent_proposals if p.improvement_type]
                    for imp_type in improvement_types:
                        insights['common_improvement_types'][imp_type] = insights['common_improvement_types'].get(imp_type, 0) + 1
                    
                    # Generate recommendations
                    if insights['approval_rate'] < 0.5:
                        insights['recommendations'].append("Consider improving proposal quality - approval rate is low")
                    
                    if insights['average_confidence'] < 0.6:
                        insights['recommendations'].append("AI confidence is low - consider retraining models")
                
                return insights
                
            except Exception as e:
                logger.error("Error getting ML insights", error=str(e))
                return {}
            finally:
                await session.close()
            
        except Exception as e:
            logger.error("Error in get_ml_insights", error=str(e))
            return {} 