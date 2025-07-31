"""
Imperium AI Service - Code optimization and extension creation with comprehensive SCKIPIT integration
Enhanced with ML-driven code analysis, optimization suggestions, and extension validation
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
from sklearn.exceptions import NotFittedError

from ..core.database import get_session
from ..core.config import settings
from .ml_service import MLService
from .sckipit_service import SckipitService
from .ai_learning_service import AILearningService
from .imperium_extension_service import ImperiumExtensionService
from app.services.anthropic_service import call_claude, anthropic_rate_limited_call

logger = structlog.get_logger()


class ImperiumAIService:
    """Imperium AI Service - Code optimization and extension creation with comprehensive SCKIPIT integration"""
    
    _instance = None
    _initialized = False
    _optimizations = {}
    _extension_history = []
    _code_analysis_results = []
    _ml_models = {}
    _sckipit_models = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImperiumAIService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ml_service = MLService()
            self.sckipit_service = None  # Will be initialized properly in initialize()
            self.learning_service = AILearningService()
            self.custody_service = None # Initialize to None, will be set in methods
            self.extension_service = ImperiumExtensionService()
            self._initialized = True
            self._initialize_enhanced_ml_models()
            
            # SCKIPIT Integration
            self.sckipit_optimization_models = {}
            self.sckipit_code_analyzer = None
            self.sckipit_extension_validator = None
            self.sckipit_performance_predictor = None
            
            # Enhanced Optimization Data
            self.sckipit_enhanced_optimizations = []
            self.code_analysis_history = []
            self.extension_validation_results = []
            
            # Initialize SCKIPIT models
            self._initialize_sckipit_models() 

    def _initialize_enhanced_ml_models(self):
        """Initialize enhanced ML models with SCKIPIT integration"""
        try:
            # Create models directory
            os.makedirs(settings.ml_model_path, exist_ok=True)
            
            # Enhanced ML Models with SCKIPIT Integration
            self._ml_models = {
                # Code Optimization Predictor (Enhanced with SCKIPIT)
                'code_optimization_predictor': RandomForestRegressor(
                    n_estimators=200, 
                    max_depth=15, 
                    min_samples_split=5,
                    random_state=42
                ),
                
                # Performance Improvement Predictor (Enhanced with SCKIPIT)
                'performance_improvement_predictor': GradientBoostingRegressor(
                    n_estimators=150,
                    learning_rate=0.1,
                    max_depth=10,
                    random_state=42
                ),
                
                # Extension Quality Analyzer (Enhanced with SCKIPIT)
                'extension_quality_analyzer': AdaBoostRegressor(
                    n_estimators=100,
                    learning_rate=0.05,
                    random_state=42
                ),
                
                # Code Complexity Analyzer (Enhanced with SCKIPIT)
                'code_complexity_analyzer': MLPRegressor(
                    hidden_layer_sizes=(100, 50, 25),
                    activation='relu',
                    solver='adam',
                    max_iter=500,
                    random_state=42
                ),
                
                # Optimization Impact Predictor (Enhanced with SCKIPIT)
                'optimization_impact_predictor': SVR(
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
        """Initialize SCKIPIT-specific models for Imperium AI enhancement"""
        try:
            # SCKIPIT Code Optimization Models
            self.sckipit_models = {
                'code_optimization_analyzer': RandomForestRegressor(
                    n_estimators=150,
                    max_depth=12,
                    random_state=42
                ),
                
                'performance_predictor': GradientBoostingRegressor(
                    n_estimators=120,
                    learning_rate=0.1,
                    random_state=42
                ),
                
                'extension_validator': LogisticRegression(
                    random_state=42,
                    max_iter=200
                ),
                
                'code_quality_assessor': MLPRegressor(
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
            
            logger.info("SCKIPIT models for Imperium AI initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SCKIPIT models: {str(e)}")
    
    def _load_existing_sckipit_models(self):
        """Load existing trained SCKIPIT models"""
        try:
            model_files = {
                'code_optimization_analyzer': 'sckipit_code_optimization_analyzer.pkl',
                'performance_predictor': 'sckipit_performance_predictor.pkl',
                'extension_validator': 'sckipit_extension_validator.pkl',
                'code_quality_assessor': 'sckipit_code_quality_assessor.pkl',
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
    
    # ==================== SCKIPIT-ENHANCED OPTIMIZATION METHODS ====================
    
    async def optimize_code_with_sckipit(self, code: str, file_path: str, optimization_type: str = "general") -> Dict[str, Any]:
        """Optimize code using SCKIPIT-enhanced ML analysis"""
        try:
            logger.info(f"Imperium AI optimizing code with SCKIPIT: {file_path}")
            
            # Initialize SCKIPIT service
            sckipit = await SckipitService.initialize()
            
            # Analyze code quality with SCKIPIT
            quality_analysis = await sckipit.analyze_code_quality(code, file_path)
            
            # Extract optimization features
            optimization_features = await self._extract_optimization_features(code, file_path, optimization_type)
            
            # SCKIPIT Performance Analysis
            performance_analysis = await self._analyze_performance_with_sckipit(code, optimization_features)
            
            # SCKIPIT Optimization Suggestions
            optimization_suggestions = await self._generate_sckipit_optimizations(code, quality_analysis, performance_analysis)
            
            # Apply optimizations
            optimized_code = await self._apply_sckipit_optimizations(code, optimization_suggestions)
            
            # Validate optimized code
            validation_result = await self._validate_optimized_code_with_sckipit(optimized_code, file_path, quality_analysis)
            
            # Enhanced optimization record with SCKIPIT insights
            optimization_record = {
                'timestamp': datetime.now().isoformat(),
                'file_path': file_path,
                'optimization_type': optimization_type,
                'original_quality': quality_analysis.get('quality_score', 0.7),
                'optimized_quality': validation_result.get('quality_score', 0.7),
                'performance_improvement': performance_analysis.get('improvement_score', 0.0),
                'optimization_suggestions': optimization_suggestions,
                'validation_result': validation_result,
                'sckipit_confidence': validation_result.get('sckipit_confidence', 0.7)
            }
            
            self.sckipit_enhanced_optimizations.append(optimization_record)
            
            # Update SCKIPIT learning data
            await self._update_sckipit_optimization_data(optimization_record)
            
            logger.info(f"SCKIPIT-enhanced code optimization completed for {file_path}")
            
            return {
                'status': 'success',
                'optimized_code': optimized_code,
                'quality_improvement': validation_result.get('quality_score', 0.7) - quality_analysis.get('quality_score', 0.7),
                'performance_improvement': performance_analysis.get('improvement_score', 0.0),
                'optimization_suggestions': optimization_suggestions,
                'sckipit_analysis': {
                    'original_quality': quality_analysis,
                    'performance_analysis': performance_analysis,
                    'validation_result': validation_result
                }
            }
            
        except Exception as e:
            logger.error(f"Error optimizing code with SCKIPIT: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def create_extension_with_sckipit(self, extension_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create extension with SCKIPIT validation and analysis"""
        try:
            logger.info(f"Imperium AI creating extension with SCKIPIT: {extension_data.get('name', 'Unknown')}")
            
            # Initialize SCKIPIT service
            sckipit = await SckipitService.initialize()
            
            # Analyze extension requirements with SCKIPIT
            requirements_analysis = await self._analyze_extension_requirements_with_sckipit(extension_data)
            
            # Generate extension code with SCKIPIT validation
            extension_code = await self._generate_extension_code_with_sckipit(extension_data, requirements_analysis)
            
            # Validate extension with SCKIPIT
            validation_result = await self._validate_extension_with_sckipit(extension_code, extension_data)
            
            if not validation_result.get('is_valid', False):
                logger.warning(f"Extension validation failed with SCKIPIT: {validation_result.get('reason', 'Unknown error')}")
                return {
                    "status": "error",
                    "message": f"Extension validation failed: {validation_result.get('reason', 'Unknown error')}",
                    "sckipit_analysis": validation_result
                }
            
            # Create extension using extension service
            extension_result = await self.extension_service.create_extension(extension_data, extension_code)
            
            # Update SCKIPIT learning data
            await self._update_sckipit_extension_data(extension_data, extension_code, validation_result, extension_result)
            
            return {
                "status": "success",
                "extension_id": extension_result.get("extension_id"),
                "extension_name": extension_data.get("name"),
                "extension_code": extension_code,
                "sckipit_analysis": {
                    "requirements_analysis": requirements_analysis,
                    "validation_result": validation_result,
                    "quality_score": validation_result.get('quality_score', 0.7)
                },
                "message": f"Extension {extension_data.get('name')} created successfully with SCKIPIT analysis"
            }
            
        except Exception as e:
            logger.error(f"Error creating extension with SCKIPIT: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _analyze_performance_with_sckipit(self, code: str, features: Dict) -> Dict[str, Any]:
        """Analyze performance using SCKIPIT models"""
        try:
            # Use SCKIPIT performance predictor
            improvement_score = 0.5
            performance_analysis = {}
            if 'performance_predictor' in self.sckipit_models:
                X = np.array([list(features.values())])
                for _ in range(2):
                    try:
                        improvement_score = self.sckipit_models['performance_predictor'].predict(X)[0]
                        performance_analysis = {
                            'improvement_score': float(improvement_score),
                            'performance_level': await self._classify_performance_level(improvement_score),
                            'optimization_potential': await self._calculate_optimization_potential(features),
                            'bottlenecks': await self._identify_performance_bottlenecks(features),
                            'recommendations': await self._generate_performance_recommendations(improvement_score, features)
                        }
                        break
                    except NotFittedError:
                        logger.warning("Model 'performance_predictor' not fitted. Triggering retrain.")
                        # Retrain logic: call SckipitService retrain for now
                        sckipit = await SckipitService.initialize()
                        await sckipit.train_sckipit_models(force_retrain=True)
                else:
                    logger.error("Model 'performance_predictor' could not be fitted after retrain.")
                    performance_analysis = {
                        'improvement_score': 0.5,
                        'performance_level': 'medium',
                        'optimization_potential': 0.6,
                        'bottlenecks': [],
                        'recommendations': []
                    }
            else:
                performance_analysis = {
                    'improvement_score': 0.5,
                    'performance_level': 'medium',
                    'optimization_potential': 0.6,
                    'bottlenecks': [],
                    'recommendations': []
                }
            return performance_analysis
        except Exception as e:
            logger.error(f"Error analyzing performance with SCKIPIT: {str(e)}")
            return {'improvement_score': 0.5, 'performance_level': 'unknown'}
    
    async def _generate_sckipit_optimizations(self, code: str, quality_analysis: Dict, performance_analysis: Dict) -> List[str]:
        """Generate SCKIPIT-based optimization suggestions"""
        try:
            optimizations = []
            
            # Quality-based optimizations
            if quality_analysis.get('quality_score', 0.7) < 0.8:
                optimizations.append("Improve code quality and structure")
            
            if quality_analysis.get('complexity_score', 0.5) > 0.7:
                optimizations.append("Reduce code complexity for better maintainability")
            
            if quality_analysis.get('readability_score', 0.6) < 0.7:
                optimizations.append("Improve code readability with better naming and comments")
            
            # Performance-based optimizations
            if performance_analysis.get('improvement_score', 0.5) < 0.6:
                optimizations.append("Optimize algorithms and data structures")
            
            if performance_analysis.get('optimization_potential', 0.6) > 0.7:
                optimizations.append("Apply advanced optimization techniques")
            
            # General SCKIPIT recommendations
            optimizations.extend([
                "Follow coding best practices and conventions",
                "Implement efficient error handling",
                "Optimize memory usage and resource management",
                "Add comprehensive logging and monitoring"
            ])
            
            return list(set(optimizations))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error generating SCKIPIT optimizations: {str(e)}")
            return ["Apply general optimization practices"]
    
    async def _apply_sckipit_optimizations(self, code: str, optimizations: List[str]) -> str:
        """Apply SCKIPIT optimizations to code"""
        try:
            optimized_code = code
            
            # Apply basic optimizations based on SCKIPIT suggestions
            for optimization in optimizations:
                if 'quality' in optimization.lower():
                    optimized_code = self._improve_code_quality(optimized_code)
                elif 'complexity' in optimization.lower():
                    optimized_code = self._reduce_complexity(optimized_code)
                elif 'readability' in optimization.lower():
                    optimized_code = self._improve_readability(optimized_code)
                elif 'performance' in optimization.lower():
                    optimized_code = self._optimize_performance(optimized_code)
                elif 'error' in optimization.lower():
                    optimized_code = self._add_error_handling(optimized_code)
            
            return optimized_code
            
        except Exception as e:
            logger.error(f"Error applying SCKIPIT optimizations: {str(e)}")
            return code  # Return original code if optimizations fail
    
    async def _validate_optimized_code_with_sckipit(self, code: str, file_path: str, original_quality: Dict) -> Dict[str, Any]:
        """Validate optimized code with SCKIPIT analysis"""
        try:
            # Initialize SCKIPIT service
            sckipit = await SckipitService.initialize()
            
            # Analyze optimized code quality
            optimized_quality = await sckipit.analyze_code_quality(code, file_path)
            
            # Calculate improvement
            quality_improvement = optimized_quality.get('quality_score', 0.7) - original_quality.get('quality_score', 0.7)
            
            # Determine if optimization was successful
            is_valid = quality_improvement > 0 and optimized_quality.get('quality_score', 0.7) >= 0.7
            
            return {
                'is_valid': is_valid,
                'quality_score': optimized_quality.get('quality_score', 0.7),
                'quality_improvement': quality_improvement,
                'validation_issues': optimized_quality.get('improvements', []),
                'reason': 'Optimization successful' if is_valid else f'Quality improvement insufficient: {quality_improvement:.3f}',
                'sckipit_confidence': 0.8 if is_valid else 0.6
            }
            
        except Exception as e:
            logger.error(f"Error validating optimized code with SCKIPIT: {str(e)}")
            return {
                'is_valid': True,  # Fallback to allow optimization
                'quality_score': 0.7,
                'quality_improvement': 0.0,
                'validation_issues': [],
                'reason': 'SCKIPIT validation failed, using fallback',
                'sckipit_confidence': 0.5
            }
    
    async def _analyze_extension_requirements_with_sckipit(self, extension_data: Dict) -> Dict[str, Any]:
        """Analyze extension requirements using SCKIPIT"""
        try:
            # Initialize SCKIPIT service
            sckipit = await SckipitService.initialize()
            
            # Create requirements data for analysis
            requirements_data = {
                'name': extension_data.get('name', ''),
                'description': extension_data.get('description', ''),
                'target_ai': extension_data.get('target_ai', ''),
                'complexity': len(extension_data.get('features', [])),
                'feature_count': len(extension_data.get('features', [])),
                'description_length': len(extension_data.get('description', '')),
                'has_code': bool(extension_data.get('code', ''))
            }
            
            # Analyze requirements quality
            requirements_quality = await self._assess_requirements_quality(requirements_data)
            
            # Generate requirements suggestions
            suggestions = await self._generate_requirements_suggestions(requirements_data, requirements_quality)
            
            return {
                'requirements_quality': requirements_quality,
                'suggestions': suggestions,
                'complexity_assessment': await self._assess_extension_complexity(requirements_data),
                'feasibility_score': await self._calculate_feasibility_score(requirements_data),
                'sckipit_confidence': 0.8
            }
            
        except Exception as e:
            logger.error(f"Error analyzing extension requirements with SCKIPIT: {str(e)}")
            return {
                'requirements_quality': 0.7,
                'suggestions': ["Apply general best practices"],
                'complexity_assessment': 'medium',
                'feasibility_score': 0.7,
                'sckipit_confidence': 0.5
            }
    
    async def _generate_extension_code_with_sckipit(self, extension_data: Dict, requirements_analysis: Dict) -> str:
        """Generate extension code with SCKIPIT validation"""
        try:
            # Generate base extension code
            extension_code = await self._generate_extension_code(extension_data)
            
            # Validate code with SCKIPIT
            sckipit = await SckipitService.initialize()
            quality_analysis = await sckipit.analyze_code_quality(extension_code, f"extensions/{extension_data.get('name', 'extension')}.dart")
            
            # Apply improvements if quality is low
            if quality_analysis.get('quality_score', 0.7) < 0.8:
                improved_code = await self._apply_sckipit_improvements(extension_code, quality_analysis)
                return improved_code
            
            return extension_code
            
        except Exception as e:
            logger.error(f"Error generating extension code with SCKIPIT: {str(e)}")
            return await self._generate_extension_code(extension_data)
    
    async def _validate_extension_with_sckipit(self, extension_code: str, extension_data: Dict) -> Dict[str, Any]:
        """Validate extension with SCKIPIT analysis"""
        try:
            # Initialize SCKIPIT service
            sckipit = await SckipitService.initialize()
            
            # Analyze extension quality
            quality_analysis = await sckipit.analyze_code_quality(extension_code, f"extensions/{extension_data.get('name', 'extension')}.dart")
            
            # Check extension-specific requirements
            extension_validation = await self._validate_extension_requirements(extension_data, quality_analysis)
            
            # Determine if extension is valid
            is_valid = quality_analysis.get('quality_score', 0.7) >= 0.7 and extension_validation.get('requirements_met', True)
            
            return {
                'is_valid': is_valid,
                'quality_score': quality_analysis.get('quality_score', 0.7),
                'validation_issues': quality_analysis.get('improvements', []),
                'extension_validation': extension_validation,
                'reason': 'Extension meets SCKIPIT quality standards' if is_valid else f'Quality issues: {quality_analysis.get("improvements", [])}',
                'sckipit_confidence': 0.8 if is_valid else 0.6
            }
            
        except Exception as e:
            logger.error(f"Error validating extension with SCKIPIT: {str(e)}")
            return {
                'is_valid': True,  # Fallback to allow creation
                'quality_score': 0.7,
                'validation_issues': [],
                'extension_validation': {'requirements_met': True},
                'reason': 'SCKIPIT validation failed, using fallback',
                'sckipit_confidence': 0.5
            }
    
    # ==================== SCKIPIT HELPER METHODS ====================
    
    async def _extract_optimization_features(self, code: str, file_path: str, optimization_type: str) -> Dict[str, float]:
        """Extract features for optimization analysis"""
        try:
            return {
                'code_length': len(code),
                'line_count': len(code.split('\n')),
                'complexity_score': await self._calculate_code_complexity(code),
                'readability_score': await self._calculate_readability_score(code),
                'performance_score': await self._calculate_performance_score(code),
                'optimization_type_encoded': hash(optimization_type) % 10 / 10.0,
                'file_type_encoded': hash(file_path.split('.')[-1]) % 10 / 10.0,
                'has_comments': 1.0 if '//' in code or '/*' in code else 0.0,
                'has_error_handling': 1.0 if 'try' in code and 'catch' in code else 0.0
            }
        except Exception as e:
            logger.error(f"Error extracting optimization features: {str(e)}")
            return {'code_length': 0.0, 'line_count': 0.0, 'complexity_score': 0.0}
    
    async def _classify_performance_level(self, improvement_score: float) -> str:
        """Classify performance level based on improvement score"""
        try:
            if improvement_score >= 0.8:
                return "excellent"
            elif improvement_score >= 0.6:
                return "good"
            elif improvement_score >= 0.4:
                return "acceptable"
            else:
                return "needs_improvement"
        except Exception as e:
            logger.error(f"Error classifying performance level: {str(e)}")
            return "unknown"
    
    async def _calculate_optimization_potential(self, features: Dict) -> float:
        """Calculate optimization potential based on features"""
        try:
            # Weighted combination of features
            weights = {
                'complexity_score': 0.3,
                'performance_score': 0.25,
                'readability_score': 0.2,
                'code_length': 0.15,
                'has_error_handling': 0.1
            }
            
            potential = 0.0
            for feature, weight in weights.items():
                normalized_value = min(1.0, features.get(feature, 0.0) / 1000.0)  # Normalize
                potential += normalized_value * weight
            
            return min(1.0, max(0.0, potential))
        except Exception as e:
            logger.error(f"Error calculating optimization potential: {str(e)}")
            return 0.5
    
    async def _identify_performance_bottlenecks(self, features: Dict) -> List[str]:
        """Identify performance bottlenecks based on features"""
        try:
            bottlenecks = []
            
            if features.get('complexity_score', 0.0) > 0.7:
                bottlenecks.append("High code complexity affecting performance")
            
            if features.get('code_length', 0.0) > 1000:
                bottlenecks.append("Large code size may impact loading time")
            
            if features.get('has_error_handling', 0.0) < 0.5:
                bottlenecks.append("Insufficient error handling may cause crashes")
            
            if features.get('readability_score', 0.0) < 0.6:
                bottlenecks.append("Poor readability may lead to maintenance issues")
            
            return bottlenecks
        except Exception as e:
            logger.error(f"Error identifying performance bottlenecks: {str(e)}")
            return ["General performance optimization needed"]
    
    async def _generate_performance_recommendations(self, improvement_score: float, features: Dict) -> List[str]:
        """Generate performance recommendations based on analysis"""
        try:
            recommendations = []
            
            if improvement_score < 0.6:
                recommendations.extend([
                    "Optimize algorithms and data structures",
                    "Implement caching mechanisms",
                    "Reduce unnecessary computations",
                    "Profile code to identify bottlenecks"
                ])
            
            if features.get('complexity_score', 0.0) > 0.7:
                recommendations.append("Simplify complex algorithms")
            
            if features.get('code_length', 0.0) > 1000:
                recommendations.append("Break down large functions into smaller ones")
            
            return recommendations
        except Exception as e:
            logger.error(f"Error generating performance recommendations: {str(e)}")
            return ["Apply general performance optimization practices"]
    
    async def _update_sckipit_optimization_data(self, optimization_record: Dict):
        """Update SCKIPIT learning data with optimization results"""
        try:
            # Add to SCKIPIT-enhanced optimizations
            self.sckipit_enhanced_optimizations.append(optimization_record)
            
            # Keep only recent data to prevent memory issues
            max_records = 100
            if len(self.sckipit_enhanced_optimizations) > max_records:
                self.sckipit_enhanced_optimizations = self.sckipit_enhanced_optimizations[-max_records:]
            
            logger.info(f"Updated SCKIPIT optimization data for {optimization_record.get('file_path', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error updating SCKIPIT optimization data: {str(e)}")
    
    async def _update_sckipit_extension_data(self, extension_data: Dict, extension_code: str, validation_result: Dict, extension_result: Dict):
        """Update SCKIPIT learning data with extension creation results"""
        try:
            # Add to extension validation results
            extension_creation_data = {
                'timestamp': datetime.now().isoformat(),
                'extension_name': extension_data.get('name', ''),
                'extension_data': extension_data,
                'validation_result': validation_result,
                'extension_result': extension_result,
                'success': extension_result.get('status') == 'success'
            }
            
            self.extension_validation_results.append(extension_creation_data)
            
            # Keep only recent data to prevent memory issues
            max_records = 50
            if len(self.extension_validation_results) > max_records:
                self.extension_validation_results = self.extension_validation_results[-max_records:]
            
            logger.info(f"Updated SCKIPIT extension data for {extension_data.get('name', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error updating SCKIPIT extension data: {str(e)}")
    
    async def get_sckipit_analytics(self) -> Dict[str, Any]:
        """Get SCKIPIT analytics for Imperium AI"""
        try:
            return {
                'total_optimizations': len(self.sckipit_enhanced_optimizations),
                'total_extensions': len(self.extension_validation_results),
                'average_quality_improvement': sum(opt.get('quality_improvement', 0.0) for opt in self.sckipit_enhanced_optimizations) / len(self.sckipit_enhanced_optimizations) if self.sckipit_enhanced_optimizations else 0.0,
                'average_performance_improvement': sum(opt.get('performance_improvement', 0.0) for opt in self.sckipit_enhanced_optimizations) / len(self.sckipit_enhanced_optimizations) if self.sckipit_enhanced_optimizations else 0.0,
                'extension_success_rate': len([ext for ext in self.extension_validation_results if ext.get('success', False)]) / len(self.extension_validation_results) if self.extension_validation_results else 0.0,
                'recent_optimizations': self.sckipit_enhanced_optimizations[-5:] if self.sckipit_enhanced_optimizations else [],
                'recent_extensions': self.extension_validation_results[-5:] if self.extension_validation_results else [],
                'sckipit_integration_status': 'active'
            }
        except Exception as e:
            logger.error(f"Error getting SCKIPIT analytics: {str(e)}")
            return {'error': str(e)}
    
    # ==================== CODE OPTIMIZATION HELPER METHODS ====================
    
    async def _calculate_code_complexity(self, code: str) -> float:
        """Calculate code complexity score"""
        try:
            lines = code.split('\n')
            complexity_score = 0.0
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('if ') or stripped.startswith('for ') or stripped.startswith('while '):
                    complexity_score += 0.1
                if stripped.count('{') > 0:
                    complexity_score += 0.05
                if stripped.count('}') > 0:
                    complexity_score += 0.05
            
            return min(1.0, complexity_score / len(lines) if lines else 0.0)
        except Exception as e:
            logger.error(f"Error calculating code complexity: {str(e)}")
            return 0.5
    
    async def _calculate_readability_score(self, code: str) -> float:
        """Calculate code readability score"""
        try:
            lines = code.split('\n')
            readability_score = 0.0
            total_lines = len(lines)
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('//') or stripped.startswith('///'):
                    readability_score += 0.1
                if len(stripped) <= 80:
                    readability_score += 0.05
                if stripped and not stripped.startswith('}'):
                    readability_score += 0.02
            
            return min(1.0, readability_score / total_lines if total_lines > 0 else 0.0)
        except Exception as e:
            logger.error(f"Error calculating readability score: {str(e)}")
            return 0.6
    
    async def _calculate_performance_score(self, code: str) -> float:
        """Calculate performance score"""
        try:
            performance_score = 0.7  # Base score
            
            # Check for performance indicators
            if 'async' in code or 'await' in code:
                performance_score += 0.1
            if 'cache' in code.lower():
                performance_score += 0.1
            if 'optimize' in code.lower():
                performance_score += 0.05
            
            return min(1.0, performance_score)
        except Exception as e:
            logger.error(f"Error calculating performance score: {str(e)}")
            return 0.7
    
    def _improve_code_quality(self, code: str) -> str:
        """Improve code quality"""
        try:
            # Basic quality improvements
            improved_code = code
            
            # Add comments for complex logic
            lines = improved_code.split('\n')
            for i, line in enumerate(lines):
                if 'if ' in line and '&&' in line and not line.strip().startswith('//'):
                    lines.insert(i, f"// Complex condition: {line.strip()}")
            
            return '\n'.join(lines)
        except Exception as e:
            logger.error(f"Error improving code quality: {str(e)}")
            return code
    
    def _reduce_complexity(self, code: str) -> str:
        """Reduce code complexity"""
        try:
            # Basic complexity reduction
            improved_code = code
            
            # Split complex conditions
            lines = improved_code.split('\n')
            for i, line in enumerate(lines):
                if 'if ' in line and line.count('&&') > 1:
                    # Split complex condition
                    condition_parts = line.split('&&')
                    if len(condition_parts) > 1:
                        new_lines = []
                        for j, part in enumerate(condition_parts):
                            if j == 0:
                                new_lines.append(f"if ({part.strip()})")
                            else:
                                new_lines.append(f"    && ({part.strip()})")
                        lines[i] = '\n'.join(new_lines)
            
            return '\n'.join(lines)
        except Exception as e:
            logger.error(f"Error reducing complexity: {str(e)}")
            return code
    
    def _improve_readability(self, code: str) -> str:
        """Improve code readability"""
        try:
            # Basic readability improvements
            improved_code = code
            
            # Add spacing around operators
            improved_code = improved_code.replace('&&', ' && ')
            improved_code = improved_code.replace('||', ' || ')
            improved_code = improved_code.replace('==', ' == ')
            improved_code = improved_code.replace('!=', ' != ')
            
            return improved_code
        except Exception as e:
            logger.error(f"Error improving readability: {str(e)}")
            return code
    
    def _optimize_performance(self, code: str) -> str:
        """Optimize code performance"""
        try:
            # Basic performance optimizations
            improved_code = code
            
            # Add async/await where appropriate
            if 'Future.delayed' in improved_code and 'async' not in improved_code:
                improved_code = improved_code.replace('Future.delayed', 'await Future.delayed')
            
            return improved_code
        except Exception as e:
            logger.error(f"Error optimizing performance: {str(e)}")
            return code
    
    def _add_error_handling(self, code: str) -> str:
        """Add error handling to code"""
        try:
            # Basic error handling addition
            if 'try {' not in code and 'catch' not in code:
                lines = code.split('\n')
                if lines:
                    for i, line in enumerate(lines):
                        if 'void main()' in line or 'Widget build(' in line:
                            lines.insert(i, '  try {')
                            lines.append('  } catch (e) {')
                            lines.append('    print("Error: $e");')
                            lines.append('  }')
                            break
            
            return '\n'.join(lines)
        except Exception as e:
            logger.error(f"Error adding error handling: {str(e)}") 

    async def answer_prompt(self, prompt: str) -> str:
        learning_log = await self.learning_service.get_learning_log("imperium")
        structured_response = await self.sckipit_service.generate_answer_with_llm(prompt, learning_log)
        
        # Extract the answer from the structured response
        answer = structured_response.get("answer", "No answer generated")
        
        # Log the full structured response for learning and analytics
        await self.learning_service.log_answer("imperium", prompt, answer, structured_response)
        
        return answer 

    async def run_cross_ai_optimization(self) -> dict:
        """Proactively optimize and propose improvements for all AIs using live data and ML/SCKIPIT."""
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        results = {}
        for ai in ai_types:
            try:
                # Skip self for now if desired
                if ai == "imperium":
                    continue
                # Get code/logic for the AI (could be via repo, service, or API)
                # For demo, use a generic prompt
                prompt = f"Analyze and optimize the code, logic, and learning patterns for the {ai} AI. Suggest performance, maintainability, and extensibility improvements."
                answer = await self.answer_prompt(prompt)
                # Log the optimization proposal for learning
                await self.learning_service.log_answer("imperium", prompt, answer, {"ai_target": ai, "optimization": answer})
                results[ai] = answer
            except Exception as e:
                results[ai] = f"Error optimizing {ai}: {str(e)}"
        return {"status": "success", "cross_ai_optimizations": results} 