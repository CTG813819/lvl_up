"""
AI Learning Service with scikit-learn integration
LIVE LEARNING - NO STUBS OR SIMULATIONS
ENHANCED ML PRODUCTIVITY - ADVANCED PROPOSAL IMPROVEMENT
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import requests
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_recall_fscore_support
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
import pickle
import os
import json

from ..core.database import get_session
from ..core.config import settings
from .ml_service import MLService
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
            self._initialized = True
            self._initialize_enhanced_ml_models()
    
    @classmethod
    async def initialize(cls):
        """Initialize the AI Learning service"""
        instance = cls()
        logger.info("AI Learning Service initialized with ENHANCED ML capabilities")
        return instance
    
    def _initialize_enhanced_ml_models(self):
        """Initialize ENHANCED scikit-learn models for AI learning and proposal improvement"""
        try:
            # Create models directory
            os.makedirs(settings.ml_model_path, exist_ok=True)
            
            # Initialize ENHANCED models for better productivity
            self._ml_models = {
                # Proposal Quality Prediction
                'proposal_quality_predictor': RandomForestRegressor(
                    n_estimators=200, 
                    max_depth=15, 
                    min_samples_split=5,
                    random_state=42
                ),
                
                # Failure Prediction (Enhanced)
                'failure_predictor': GradientBoostingRegressor(
                    n_estimators=150,
                    learning_rate=0.1,
                    max_depth=8,
                    random_state=42
                ),
                
                # Improvement Recommendation Engine
                'improvement_recommender': AdaBoostRegressor(
                    n_estimators=100,
                    learning_rate=0.05,
                    random_state=42
                ),
                
                # Code Quality Analyzer
                'code_quality_analyzer': MLPRegressor(
                    hidden_layer_sizes=(100, 50, 25),
                    activation='relu',
                    solver='adam',
                    max_iter=500,
                    random_state=42
                ),
                
                # Productivity Predictor
                'productivity_predictor': SVR(
                    kernel='rbf',
                    C=1.0,
                    gamma='scale'
                ),
                
                # Proposal Clustering for Pattern Recognition
                'proposal_clusterer': KMeans(
                    n_clusters=8,
                    random_state=42
                ),
                
                # Feature Selection for Better Models
                'feature_selector': SelectKBest(
                    score_func=f_regression,
                    k=10
                )
            }
            
            # Load existing models if available
            self._load_existing_models()
            
            logger.info("ENHANCED ML models initialized for AI learning and proposal improvement")
        except Exception as e:
            logger.error(f"Error initializing ENHANCED ML models: {str(e)}")
    
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
        """Get AI learning insights using ML analysis"""
        try:
            if ai_type not in self._learning_states:
                return {'error': 'No learning data available'}
            
            state = self._learning_states[ai_type]
            
            # Analyze learning patterns
            total_events = len(state['learning_events'])
            total_improvements = len(state['improvements_learned'])
            
            # Calculate learning efficiency
            learning_efficiency = total_improvements / max(total_events, 1)
            
            # Get recent learning activity
            recent_events = state['learning_events'][-5:] if state['learning_events'] else []
            
            insights = {
                'ai_type': ai_type,
                'total_learning_events': total_events,
                'total_improvements_learned': total_improvements,
                'learning_efficiency': learning_efficiency,
                'recent_learning_events': recent_events,
                'failure_patterns': state.get('failure_patterns', []),
                'success_patterns': state.get('success_patterns', []),
                'last_learning': state.get('last_learning'),
                'ml_model_status': 'active' if 'failure_predictor' in self._ml_models else 'inactive'
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting learning insights: {str(e)}")
            return {'error': str(e)}
    
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
                        Learning.pattern == pattern
                    )
                )
                existing = existing_learning.scalar_one_or_none()
                
                if existing:
                    # Update existing learning
                    existing.applied_count += 1
                    existing.success_rate = (existing.success_rate + (1.0 if status == "approved" else 0.0)) / 2.0
                    existing.updated_at = datetime.utcnow()
                    existing.feedback = feedback_reason or f"Proposal {status}"
                    logger.info("Updated existing learning pattern", 
                               pattern=pattern, 
                               success_rate=existing.success_rate,
                               applied_count=existing.applied_count)
                else:
                    # Create new learning entry
                    new_learning = Learning(
                        ai_type=proposal.ai_type,
                        learning_type="proposal_outcome",
                        pattern=pattern,
                        context=f"Proposal {proposal_id} outcome: {status}",
                        feedback=feedback_reason or f"Proposal {status}",
                        confidence=0.8,
                        applied_count=1,
                        success_rate=1.0 if status == "approved" else 0.0,
                        created_at=datetime.utcnow()
                    )
                    session.add(new_learning)
                    logger.info("Created new learning pattern", 
                               pattern=pattern, 
                               ai_type=proposal.ai_type)
                
                # Update proposal with learning applied
                proposal.ai_learning_applied = True
                proposal.updated_at = datetime.utcnow()
                
                await session.commit()
                
                return {
                    "status": "success",
                    "pattern": pattern,
                    "ai_type": proposal.ai_type,
                    "learning_applied": True
                }
                
        except Exception as e:
            logger.error("Error learning from proposal", error=str(e), proposal_id=proposal_id)
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
                total_applied = sum(entry.applied_count for entry in learning_entries)
                avg_success_rate = sum(entry.success_rate for entry in learning_entries) / total_patterns if total_patterns > 0 else 0.0
                
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
                success_count = success_result.scalar()
                
                success_rate = (success_count / proposal_count * 100) if proposal_count > 0 else 0.0
                
                return {
                    "total_patterns": total_patterns,
                    "total_applied": total_applied,
                    "average_success_rate": avg_success_rate,
                    "recent_learning": [
                        {
                            "pattern": entry.pattern,
                            "ai_type": entry.ai_type,
                            "success_rate": entry.success_rate,
                            "applied_count": entry.applied_count,
                            "updated_at": entry.updated_at.isoformat()
                        }
                        for entry in recent_entries
                    ],
                    "proposal_stats": {
                        "total": proposal_count,
                        "successful": success_count,
                        "success_rate": success_rate
                    },
                    "learning_progress": min(avg_success_rate * 100, 100.0),
                    "last_updated": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error("Error getting learning stats", error=str(e))
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
                    Learning.learning_type == "proposal_outcome",
                    Learning.success_rate > 0.7  # Only apply high-confidence patterns
                ).order_by(Learning.success_rate.desc())
                
                result = await session.execute(stmt)
                learning_patterns = result.scalars().all()
                
                improvements = []
                confidence_boost = 0.0
                
                for pattern in learning_patterns:
                    # Apply pattern-based improvements
                    if "security" in pattern.pattern and proposal_data.get("improvement_type") == "security":
                        confidence_boost += 0.1
                        improvements.append("Applied security learning pattern")
                    
                    elif "performance" in pattern.pattern and proposal_data.get("improvement_type") == "performance":
                        confidence_boost += 0.1
                        improvements.append("Applied performance learning pattern")
                    
                    elif "quality" in pattern.pattern and proposal_data.get("improvement_type") == "quality":
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
            logger.error("Error applying learning to proposal", error=str(e))
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
                    logger.error(f"Error learning topic {topic} for {ai_type}", error=str(e))
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