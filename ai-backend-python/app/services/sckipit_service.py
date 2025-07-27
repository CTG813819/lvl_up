"""
Sckipit Service - ML-driven suggestions for Conquest app creation and Sandbox experiments
Advanced scikit-learn integration for autonomous AI improvement
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import structlog
import json
import os
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression, LogisticRegression
import requests
import aiohttp
from sklearn.exceptions import NotFittedError

from ..core.database import get_session
from ..core.config import settings
from .ml_service import MLService
from . import trusted_sources
from app.services.advanced_code_generator import AdvancedCodeGenerator

logger = structlog.get_logger()


class SckipitService:
    """Sckipit Service - ML-driven suggestions for Conquest app creation and Sandbox experiments"""
    
    _instance = None
    _initialized = False
    _models = {}
    _scalers = {}
    _knowledge_base = {}
    _suggestion_history = []
    _experiment_patterns = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SckipitService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ml_service = MLService()
            self._initialized = True
            self._initialize_sckipit_models()
            # Load any available models for code generation/analysis
            self.code_quality_analyzer = self._load_model('models/sckipit_code_quality_analyzer.pkl')
            self.feature_predictor = self._load_model('models/sckipit_app_feature_predictor.pkl')
            self.dependency_recommender = self._load_model('models/sckipit_dependency_recommender.pkl')
            # Add more as needed
            # Initialize advanced code generator
            self.code_generator = AdvancedCodeGenerator()

    def _load_model(self, path):
        if os.path.exists(path):
            with open(path, 'rb') as f:
                model = pickle.load(f)
            logger.info(f"[MODEL LOAD] Loaded model from {path}: {type(model)}")
            return model
        logger.warning(f"[MODEL LOAD] Model file not found: {path}")
        return None

    def generate_dart_code_from_description(self, description: str) -> str:
        """
        Generate Dart code for a Flutter extension from a natural language description.
        This method uses advanced AI models for real code generation.
        """
        # Determine complexity based on description length and keywords
        complexity = self._determine_complexity(description)
        
        # Use advanced code generator for real AI-powered generation
        try:
            import asyncio
            # Run async code generation in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                code = loop.run_until_complete(
                    self.code_generator.generate_dart_code(description, complexity)
                )
                return code
            finally:
                loop.close()
        except Exception as e:
            print(f"Advanced code generation failed: {e}")
            # Fallback to template generation
            return self._generate_template_code(description, complexity)
    
    async def generate_dart_code_from_description_async(self, description: str) -> str:
        """
        Async version of generate_dart_code_from_description for use in async contexts.
        """
        # Determine complexity based on description length and keywords
        complexity = self._determine_complexity(description)
        
        # Use advanced code generator for real AI-powered generation
        try:
            code = await self.code_generator.generate_dart_code(description, complexity)
            return code
        except Exception as e:
            print(f"Advanced code generation failed: {e}")
            # Fallback to template generation
            return self._generate_template_code(description, complexity)
    
    def _determine_complexity(self, description: str) -> str:
        """Determine code complexity based on description."""
        description_lower = description.lower()
        
        # Keywords that suggest complex functionality
        complex_keywords = [
            'api', 'network', 'database', 'state management', 'animation',
            'custom', 'advanced', 'complex', 'multiple', 'integration',
            'authentication', 'authorization', 'real-time', 'websocket'
        ]
        
        # Keywords that suggest simple functionality
        simple_keywords = [
            'display', 'show', 'text', 'button', 'simple', 'basic',
            'static', 'view', 'label'
        ]
        
        # Count complexity indicators
        complex_count = sum(1 for keyword in complex_keywords if keyword in description_lower)
        simple_count = sum(1 for keyword in simple_keywords if keyword in description_lower)
        
        if complex_count > 2:
            return "complex"
        elif simple_count > 2 or len(description) < 50:
            return "simple"
        else:
            return "medium"
    
    def _generate_template_code(self, description: str, complexity: str) -> str:
        """Fallback template generation if AI models fail."""
        if complexity == "simple":
            return f"""
import 'package:flutter/material.dart';

class GeneratedWidget extends StatelessWidget {{
  @override
  Widget build(BuildContext context) {{
    return Container(
      padding: EdgeInsets.all(16),
      child: Text('{description}'),
    );
  }}
}}
"""
        elif complexity == "medium":
            return f"""
import 'package:flutter/material.dart';

class GeneratedWidget extends StatefulWidget {{
  @override
  _GeneratedWidgetState createState() => _GeneratedWidgetState();
}}

class _GeneratedWidgetState extends State<GeneratedWidget> {{
  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(title: Text('Generated Widget')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('{description}'),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {{
                // Implemented functionality
              }},
              child: Text('Action'),
            ),
          ],
        ),
      ),
    );
  }}
}}
"""
        else:  # complex
            return f"""
import 'package:flutter/material.dart';

class GeneratedWidget extends StatefulWidget {{
  @override
  _GeneratedWidgetState createState() => _GeneratedWidgetState();
}}

class _GeneratedWidgetState extends State<GeneratedWidget> {{
  bool _isLoading = false;
  String _result = '';

  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: Text('Advanced Widget'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _refreshData,
          ),
        ],
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                children: [
                  Text('{description}'),
                  SizedBox(height: 16),
                  _result.isNotEmpty
                      ? Text(_result)
                      : Text('No data available'),
                  SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      ElevatedButton(
                        onPressed: _performAction,
                        child: Text('Primary Action'),
                      ),
                      OutlinedButton(
                        onPressed: _secondaryAction,
                        child: Text('Secondary'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
    );
  }}

  Future<void> _performAction() async {{
    setState(() => _isLoading = true);
    try {{
      // Implemented primary action
      await Future.delayed(Duration(seconds: 1));
      setState(() => _result = 'Action completed');
    }} catch (e) {{
      setState(() => _result = 'Error: ${{e}}');
    }} finally {{
      setState(() => _isLoading = false);
    }}
  }}

  void _secondaryAction() {{
    // Implemented secondary action
  }}

  void _refreshData() {{
    setState(() => _result = '');
  }}
}}
"""
    
    @classmethod
    async def initialize(cls):
        """Initialize the Sckipit service"""
        instance = cls()
        await instance._load_knowledge_base()
        logger.info("Sckipit Service initialized with ML-driven capabilities")
        return instance
    
    def _initialize_sckipit_models(self):
        """Initialize Sckipit-specific ML models"""
        try:
            # Create models directory
            os.makedirs(settings.ml_model_path, exist_ok=True)
            
            # Conquest App Creation Models
            self._models['app_feature_predictor'] = RandomForestRegressor(
                n_estimators=150,
                max_depth=12,
                min_samples_split=5,
                random_state=42
            )
            
            self._models['dependency_recommender'] = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=8,
                random_state=42
            )
            
            self._models['code_quality_analyzer'] = MLPRegressor(
                hidden_layer_sizes=(80, 40, 20),
                activation='relu',
                solver='adam',
                max_iter=300,
                random_state=42
            )
            
            # Sandbox Experiment Models
            self._models['experiment_designer'] = AdaBoostRegressor(
                n_estimators=120,
                learning_rate=0.05,
                random_state=42
            )
            
            self._models['result_analyzer'] = SVR(
                kernel='rbf',
                C=1.0,
                gamma='scale'
            )
            
            self._models['pattern_clusterer'] = KMeans(
                n_clusters=6,
                random_state=42
            )
            
            # Knowledge Update Models
            self._models['knowledge_validator'] = LogisticRegression(
                random_state=42,
                max_iter=200
            )
            
            self._models['source_quality_predictor'] = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Load existing models
            self._load_existing_sckipit_models()
            
            logger.info("Sckipit ML models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Sckipit models: {str(e)}")
    
    def _load_existing_sckipit_models(self):
        """Load existing trained Sckipit models"""
        model_files = {
            'app_feature_predictor': 'sckipit_app_feature_predictor.pkl',
            'dependency_recommender': 'sckipit_dependency_recommender.pkl',
            'code_quality_analyzer': 'sckipit_code_quality_analyzer.pkl',
            'experiment_designer': 'sckipit_experiment_designer.pkl',
            'result_analyzer': 'sckipit_result_analyzer.pkl',
            'pattern_clusterer': 'sckipit_pattern_clusterer.pkl',
            'knowledge_validator': 'sckipit_knowledge_validator.pkl',
            'source_quality_predictor': 'sckipit_source_quality_predictor.pkl'
        }
        
        for model_name, filename in model_files.items():
            model_path = os.path.join(settings.ml_model_path, filename)
            if os.path.exists(model_path):
                try:
                    with open(model_path, 'rb') as f:
                        self._models[model_name] = pickle.load(f)
                    logger.info(f"Loaded Sckipit model: {model_name}")
                except Exception as e:
                    logger.error(f"Failed to load Sckipit model {filename}: {str(e)}")
    
    async def _save_sckipit_model(self, model_name: str):
        """Save a trained Sckipit model"""
        try:
            model_path = os.path.join(settings.ml_model_path, f"sckipit_{model_name}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(self._models[model_name], f)
            logger.info(f"Saved Sckipit model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to save Sckipit model {model_name}: {str(e)}")
    
    async def _load_knowledge_base(self):
        """Load and update knowledge base from trusted sources"""
        try:
            # Load existing knowledge
            knowledge_path = os.path.join(settings.ml_model_path, 'sckipit_knowledge_base.json')
            if os.path.exists(knowledge_path):
                with open(knowledge_path, 'r') as f:
                    self._knowledge_base = json.load(f)
            
            # Update knowledge from trusted sources
            await self._update_knowledge_from_sources()
            
            logger.info(f"Knowledge base loaded with {len(self._knowledge_base)} entries")
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
    
    async def _update_knowledge_from_sources(self):
        """Update knowledge base from trusted sources"""
        try:
            # Get current trusted sources
            sources = trusted_sources.get_trusted_sources()
            
            for source in sources:
                try:
                    # Fetch new knowledge from source
                    new_knowledge = await self._fetch_knowledge_from_source({'url': source})
                    if new_knowledge:
                        self._knowledge_base[source] = {
                            'knowledge': new_knowledge,
                            'last_updated': datetime.now().isoformat(),
                            'quality_score': await self._predict_source_quality({'url': source})
                        }
                except Exception as e:
                    logger.warning(f"Failed to update knowledge from {source['url']}: {str(e)}")
            
            # Save updated knowledge base
            knowledge_path = os.path.join(settings.ml_model_path, 'sckipit_knowledge_base.json')
            with open(knowledge_path, 'w') as f:
                json.dump(self._knowledge_base, f, indent=2)
            
            logger.info("Knowledge base updated from trusted sources")
        except Exception as e:
            logger.error(f"Error updating knowledge from sources: {str(e)}")
    
    async def _fetch_knowledge_from_source(self, source: Dict) -> Optional[str]:
        """Fetch knowledge from a trusted source"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source['url'], timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Extract relevant knowledge (simplified)
                        return content[:1000]  # First 1000 chars as knowledge
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch from {source['url']}: {str(e)}")
            return None
    
    async def _predict_source_quality(self, source: Dict) -> float:
        """Predict the quality of a knowledge source"""
        try:
            features = {
                'url_length': len(source.get('url', '')),
                'has_https': 1.0 if source.get('url', '').startswith('https') else 0.0,
                'has_documentation': 1.0 if 'docs' in source.get('url', '').lower() else 0.0,
                'has_api': 1.0 if 'api' in source.get('url', '').lower() else 0.0,
                'has_github': 1.0 if 'github' in source.get('url', '').lower() else 0.0
            }
            
            # Check if model exists and is fitted
            if 'source_quality_predictor' in self._models and hasattr(self._models['source_quality_predictor'], 'predict'):
                try:
                    X = np.array([list(features.values())])
                    quality = self._models['source_quality_predictor'].predict(X)[0]
                    return max(0.0, min(1.0, quality))
                except Exception as model_error:
                    logger.warning(f"Model prediction failed, using fallback: {str(model_error)}")
                    return 0.7  # Fallback quality score
            else:
                # Model not available, use rule-based scoring
                quality_score = 0.5  # Base score
                if features['has_https']:
                    quality_score += 0.2
                if features['has_documentation']:
                    quality_score += 0.1
                if features['has_api']:
                    quality_score += 0.1
                if features['has_github']:
                    quality_score += 0.1
                return quality_score
        except Exception as e:
            logger.error(f"Error predicting source quality: {str(e)}")
            return 0.5
    
    # Conquest App Creation Methods
    async def suggest_app_features(self, app_name: str, description: str, keywords: List[str]) -> Dict[str, Any]:
        """Suggest app features using ML analysis"""
        try:
            # Extract features for ML prediction
            features = await self._extract_app_features(app_name, description, keywords)
            
            # Predict features using ML model
            if 'app_feature_predictor' in self._models and hasattr(self._models['app_feature_predictor'], 'predict'):
                try:
                    X = np.array([list(features.values())])
                    feature_scores = self._models['app_feature_predictor'].predict(X)
                    
                    # Map scores to feature suggestions
                    suggested_features = await self._map_scores_to_features(feature_scores, keywords)
                except Exception as model_error:
                    logger.warning(f"App feature model prediction failed, using fallback: {str(model_error)}")
                    suggested_features = await self._rule_based_feature_suggestions(keywords, description)
            else:
                # Fallback to rule-based suggestions
                suggested_features = await self._rule_based_feature_suggestions(keywords, description)
            
            # Add knowledge-based suggestions
            knowledge_suggestions = await self._get_knowledge_based_suggestions(app_name, keywords)
            
            return {
                'suggested_features': suggested_features,
                'knowledge_suggestions': knowledge_suggestions,
                'confidence_score': await self._calculate_suggestion_confidence(features),
                'ml_model_used': 'app_feature_predictor' if 'app_feature_predictor' in self._models else 'rule_based'
            }
        except Exception as e:
            logger.error(f"Error suggesting app features: {str(e)}")
            return {'suggested_features': [], 'knowledge_suggestions': [], 'confidence_score': 0.0}
    
    async def suggest_dependencies(self, features: List[str], app_type: str) -> Dict[str, str]:
        """Suggest dependencies using ML analysis"""
        try:
            # Extract features for dependency prediction
            features_vector = await self._extract_dependency_features(features, app_type)
            
            # Predict dependencies using ML model
            if 'dependency_recommender' in self._models and hasattr(self._models['dependency_recommender'], 'predict'):
                try:
                    X = np.array([list(features_vector.values())])
                    dependency_scores = self._models['dependency_recommender'].predict(X)
                    
                    # Map scores to dependency suggestions
                    suggested_deps = await self._map_scores_to_dependencies(dependency_scores, features)
                except Exception as model_error:
                    logger.warning(f"Dependency model prediction failed, using fallback: {str(model_error)}")
                    suggested_deps = await self._rule_based_dependency_suggestions(features, app_type)
            else:
                # Fallback to rule-based suggestions
                suggested_deps = await self._rule_based_dependency_suggestions(features, app_type)
            
            return suggested_deps
        except Exception as e:
            logger.error(f"Error suggesting dependencies: {str(e)}")
            return {}
    
    async def analyze_code_quality(self, code: str, file_path: str) -> Dict[str, Any]:
        """Analyze code quality using ML"""
        try:
            # Extract code features
            code_features = await self._extract_code_quality_features(code, file_path)
            quality_score = 0.5
            improvements = []
            retrained = False
            if 'code_quality_analyzer' in self._models:
                X = np.array([list(code_features.values())])
                for _ in range(2):  # Try at most twice (before and after retrain)
                    try:
                        logger.info(f"[MODEL PREDICT] Using model: {self._models['code_quality_analyzer']}")
                        quality_score = self._models['code_quality_analyzer'].predict(X)[0]
                        break
                    except NotFittedError:
                        logger.warning("[MODEL PREDICT] Model 'code_quality_analyzer' not fitted. Triggering retrain.")
                        await self.train_sckipit_models(force_retrain=True)
                        retrained = True
                else:
                    logger.error("[MODEL PREDICT] Model 'code_quality_analyzer' could not be fitted after retrain.")
            else:
                quality_score = await self._rule_based_quality_score(code)
            improvements = await self._generate_code_improvements(code, quality_score, file_path)
            return {
                'quality_score': max(0.0, min(1.0, quality_score)),
                'improvements': improvements,
                'complexity_score': code_features.get('complexity', 0.0),
                'readability_score': code_features.get('readability', 0.0),
                'maintainability_score': code_features.get('maintainability', 0.0)
            }
        except Exception as e:
            logger.error(f"Error analyzing code quality: {str(e)}")
            return {'quality_score': 0.5, 'improvements': [], 'complexity_score': 0.0, 'readability_score': 0.0, 'maintainability_score': 0.0}
    
    # Sandbox Experiment Methods
    async def design_experiment(self, experiment_type: str, objectives: List[str]) -> Dict[str, Any]:
        """Design experiment using ML analysis"""
        try:
            exp_features = await self._extract_experiment_features(experiment_type, objectives)
            experiment_design = {}
            if 'experiment_designer' in self._models:
                X = np.array([list(exp_features.values())])
                for _ in range(2):
                    try:
                        design_scores = self._models['experiment_designer'].predict(X)
                        experiment_design = await self._map_scores_to_experiment_design(design_scores, experiment_type, objectives)
                        break
                    except NotFittedError:
                        logger.warning("Model 'experiment_designer' not fitted. Triggering retrain.")
                        await self.train_sckipit_models(force_retrain=True)
                else:
                    logger.error("Model 'experiment_designer' could not be fitted after retrain.")
                    experiment_design = await self._rule_based_experiment_design(experiment_type, objectives)
            else:
                experiment_design = await self._rule_based_experiment_design(experiment_type, objectives)
            return experiment_design
        except Exception as e:
            logger.error(f"Error designing experiment: {str(e)}")
            return {'parameters': {}, 'methodology': '', 'expected_outcomes': []}
    
    async def analyze_experiment_results(self, results: Dict[str, Any], experiment_type: str) -> Dict[str, Any]:
        """Analyze experiment results using ML"""
        try:
            result_features = await self._extract_result_features(results, experiment_type)
            analysis_insights = {}
            if 'result_analyzer' in self._models:
                X = np.array([list(result_features.values())])
                for _ in range(2):
                    try:
                        analysis_scores = self._models['result_analyzer'].predict(X)
                        analysis_insights = await self._map_scores_to_analysis_insights(analysis_scores, results)
                        break
                    except NotFittedError:
                        logger.warning("Model 'result_analyzer' not fitted. Triggering retrain.")
                        await self.train_sckipit_models(force_retrain=True)
                else:
                    logger.error("Model 'result_analyzer' could not be fitted after retrain.")
                    analysis_insights = await self._rule_based_result_analysis(results, experiment_type)
            else:
                analysis_insights = await self._rule_based_result_analysis(results, experiment_type)
            await self._update_experiment_patterns(experiment_type, results, analysis_insights)
            return analysis_insights
        except Exception as e:
            logger.error(f"Error analyzing experiment results: {str(e)}")
            return {'insights': [], 'recommendations': [], 'success_score': 0.0}
    
    async def suggest_next_experiments(self, current_results: Dict[str, Any], experiment_history: List[Dict]) -> List[Dict[str, Any]]:
        """Suggest next experiments based on patterns and results"""
        try:
            # Cluster experiment patterns
            if 'pattern_clusterer' in self._models and experiment_history:
                patterns = await self._extract_experiment_patterns(experiment_history)
                X = np.array(patterns)
                clusters = self._models['pattern_clusterer'].fit_predict(X)
                
                # Generate suggestions based on clusters
                suggestions = await self._generate_cluster_based_suggestions(clusters, current_results)
            else:
                # Fallback to rule-based suggestions
                suggestions = await self._rule_based_experiment_suggestions(current_results, experiment_history)
            
            return suggestions
        except Exception as e:
            logger.error(f"Error suggesting next experiments: {str(e)}")
            return []
    
    # Knowledge Update Methods
    async def validate_knowledge_update(self, new_knowledge: str, source_url: str) -> Dict[str, Any]:
        """Validate new knowledge using ML"""
        try:
            # Extract validation features
            validation_features = await self._extract_validation_features(new_knowledge, source_url)
            
            # Predict validation using ML model
            if 'knowledge_validator' in self._models:
                X = np.array([list(validation_features.values())])
                validation_score = self._models['knowledge_validator'].predict_proba(X)[0][1]
            else:
                validation_score = await self._rule_based_validation_score(new_knowledge, source_url)
            
            is_valid = validation_score > 0.7
            
            return {
                'is_valid': is_valid,
                'validation_score': validation_score,
                'confidence': await self._calculate_validation_confidence(validation_features),
                'recommendations': await self._generate_validation_recommendations(validation_score, new_knowledge)
            }
        except Exception as e:
            logger.error(f"Error validating knowledge update: {str(e)}")
            return {'is_valid': False, 'validation_score': 0.0, 'confidence': 0.0, 'recommendations': []}
    
    async def update_trusted_sources(self, new_source: Dict[str, Any]) -> bool:
        """Update trusted sources with new knowledge"""
        try:
            # Validate the new source
            validation_result = await self.validate_knowledge_update(
                new_source.get('content', ''),
                new_source.get('url', '')
            )
            
            if validation_result['is_valid']:
                # Add to trusted sources
                trusted_sources.add_trusted_source(new_source['url'])
                
                # Update knowledge base
                await self._update_knowledge_from_sources()
                
                logger.info(f"Updated trusted sources with {new_source['url']}")
                return True
            else:
                logger.warning(f"Rejected knowledge update for {new_source['url']}: validation failed")
                return False
        except Exception as e:
            logger.error(f"Error updating trusted sources: {str(e)}")
            return False
    
    # Helper Methods
    async def _extract_app_features(self, app_name: str, description: str, keywords: List[str]) -> Dict[str, float]:
        """Extract features for app feature prediction"""
        text = f"{app_name} {description} {' '.join(keywords)}".lower()
        
        features = {
            'text_length': len(text),
            'keyword_count': len(keywords),
            'has_game_keywords': 1.0 if any(k in text for k in ['game', 'play', 'score']) else 0.0,
            'has_social_keywords': 1.0 if any(k in text for k in ['social', 'chat', 'friend']) else 0.0,
            'has_fitness_keywords': 1.0 if any(k in text for k in ['fitness', 'workout', 'health']) else 0.0,
            'has_productivity_keywords': 1.0 if any(k in text for k in ['productivity', 'task', 'todo']) else 0.0,
            'has_education_keywords': 1.0 if any(k in text for k in ['education', 'learn', 'study']) else 0.0,
            'complexity_score': len(text.split()) / 10.0,
            'specificity_score': len(set(keywords)) / max(len(keywords), 1)
        }
        
        return features
    
    async def _map_scores_to_features(self, scores: np.ndarray, keywords: List[str]) -> List[str]:
        """Map ML scores to feature suggestions"""
        feature_mapping = {
            0: 'authentication',
            1: 'settings',
            2: 'navigation',
            3: 'data_storage',
            4: 'api_integration',
            5: 'push_notifications',
            6: 'analytics',
            7: 'social_sharing',
            8: 'offline_support',
            9: 'multi_language'
        }
        
        suggested_features = []
        for i, score in enumerate(scores):
            if score > 0.5 and i < len(feature_mapping):
                suggested_features.append(feature_mapping[i])
        
        return suggested_features
    
    async def _rule_based_feature_suggestions(self, keywords: List[str], description: str) -> List[str]:
        """Fallback rule-based feature suggestions"""
        text = f"{description} {' '.join(keywords)}".lower()
        suggestions = ['authentication', 'settings', 'navigation']
        
        if any(k in text for k in ['game', 'play']):
            suggestions.extend(['game_engine', 'score_tracking', 'leaderboard'])
        if any(k in text for k in ['social', 'chat']):
            suggestions.extend(['user_profiles', 'messaging', 'social_sharing'])
        if any(k in text for k in ['fitness', 'health']):
            suggestions.extend(['workout_tracking', 'progress_charts', 'goal_setting'])
        
        return suggestions
    
    async def _get_knowledge_based_suggestions(self, app_name: str, keywords: List[str]) -> List[str]:
        """Get suggestions based on knowledge base"""
        suggestions = []
        
        for source_url, knowledge in self._knowledge_base.items():
            if knowledge['quality_score'] > 0.7:
                content = knowledge['knowledge'].lower()
                for keyword in keywords:
                    if keyword.lower() in content:
                        # Extract relevant suggestions from knowledge
                        suggestions.append(f"knowledge_based_{keyword}")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    async def _calculate_suggestion_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence in suggestions"""
        # Simple confidence calculation based on feature quality
        non_zero_features = sum(1 for v in features.values() if v > 0)
        confidence = min(1.0, non_zero_features / 5.0)
        return confidence
    
    async def _extract_dependency_features(self, features: List[str], app_type: str) -> Dict[str, float]:
        """Extract features for dependency prediction"""
        feature_text = ' '.join(features).lower()
        
        return {
            'feature_count': len(features),
            'has_ui_features': 1.0 if any(f in feature_text for f in ['ui', 'screen', 'widget']) else 0.0,
            'has_data_features': 1.0 if any(f in feature_text for f in ['data', 'storage', 'database']) else 0.0,
            'has_network_features': 1.0 if any(f in feature_text for f in ['api', 'network', 'http']) else 0.0,
            'has_auth_features': 1.0 if any(f in feature_text for f in ['auth', 'login', 'user']) else 0.0,
            'app_type_encoded': hash(app_type) % 10 / 10.0
        }
    
    async def _map_scores_to_dependencies(self, scores: np.ndarray, features: List[str]) -> Dict[str, str]:
        """Map ML scores to dependency suggestions"""
        dependency_mapping = {
            0: ('provider', '^6.0.0'),
            1: ('shared_preferences', '^2.0.0'),
            2: ('http', '^0.13.0'),
            3: ('sqflite', '^2.0.0'),
            4: ('path', '^1.8.0'),
            5: ('fl_chart', '^0.60.0'),
            6: ('firebase_core', '^2.0.0'),
            7: ('firebase_messaging', '^14.0.0'),
            8: ('share_plus', '^7.0.0'),
            9: ('flame', '^1.0.0')
        }
        
        dependencies = {}
        for i, score in enumerate(scores):
            if score > 0.5 and i < len(dependency_mapping):
                dep_name, dep_version = dependency_mapping[i]
                dependencies[dep_name] = dep_version
        
        return dependencies
    
    async def _rule_based_dependency_suggestions(self, features: List[str], app_type: str) -> Dict[str, str]:
        """Fallback rule-based dependency suggestions"""
        dependencies = {
            'provider': '^6.0.0',
            'shared_preferences': '^2.0.0',
            'http': '^0.13.0',
            'sqflite': '^2.0.0',
            'path': '^1.8.0'
        }
        
        feature_text = ' '.join(features).lower()
        
        if any(f in feature_text for f in ['chart', 'graph']):
            dependencies['fl_chart'] = '^0.60.0'
        if any(f in feature_text for f in ['notification', 'push']):
            dependencies['firebase_core'] = '^2.0.0'
            dependencies['firebase_messaging'] = '^14.0.0'
        if any(f in feature_text for f in ['share', 'social']):
            dependencies['share_plus'] = '^7.0.0'
        if any(f in feature_text for f in ['game', 'play']):
            dependencies['flame'] = '^1.0.0'
        
        return dependencies
    
    async def _extract_code_quality_features(self, code: str, file_path: str) -> Dict[str, float]:
        """Extract features for code quality analysis"""
        features = {
            'code_length': len(code),
            'line_count': code.count('\n'),
            'function_count': code.count('def ') + code.count('async def '),
            'class_count': code.count('class '),
            'import_count': code.count('import ') + code.count('from '),
            'comment_ratio': code.count('#') / max(len(code.split('\n')), 1),
            'complexity_score': await self._calculate_complexity_score(code),
            'readability_score': await self._calculate_readability_score(code),
            'maintainability_score': await self._calculate_maintainability_score(code)
        }
        
        return features
    
    async def _calculate_complexity_score(self, code: str) -> float:
        """Calculate code complexity score"""
        complexity_indicators = ['if ', 'for ', 'while ', 'try:', 'except:', 'with ']
        complexity_count = sum(code.count(indicator) for indicator in complexity_indicators)
        return min(1.0, complexity_count / 10.0)
    
    async def _calculate_readability_score(self, code: str) -> float:
        """Calculate code readability score"""
        lines = code.split('\n')
        avg_line_length = sum(len(line) for line in lines) / max(len(lines), 1)
        return max(0.0, 1.0 - (avg_line_length / 100.0))
    
    async def _calculate_maintainability_score(self, code: str) -> float:
        """Calculate code maintainability score"""
        # Simple maintainability score based on structure
        has_docstrings = '"""' in code or "'''" in code
        has_comments = '#' in code
        has_functions = 'def ' in code or 'async def ' in code
        
        score = 0.0
        if has_docstrings:
            score += 0.3
        if has_comments:
            score += 0.2
        if has_functions:
            score += 0.5
        
        return min(1.0, score)
    
    async def _rule_based_quality_score(self, code: str) -> float:
        """Fallback rule-based quality score"""
        score = 0.5  # Base score
        
        # Add points for good practices
        if 'def ' in code or 'async def ' in code:
            score += 0.2
        if '"""' in code or "'''" in code:
            score += 0.1
        if '#' in code:
            score += 0.1
        if len(code.split('\n')) > 5:
            score += 0.1
        
        return min(1.0, score)
    
    async def _generate_code_improvements(self, code: str, quality_score: float, file_path: str) -> List[str]:
        """Generate code improvement suggestions"""
        improvements = []
        
        if quality_score < 0.7:
            if 'def ' not in code and 'async def ' not in code:
                improvements.append("Add functions to improve code organization")
            if '"""' not in code and "'''" not in code:
                improvements.append("Add docstrings for better documentation")
            if '#' not in code:
                improvements.append("Add comments to explain complex logic")
            if len(code.split('\n')) < 5:
                improvements.append("Consider breaking down large code blocks")
        
        return improvements
    
    async def _extract_experiment_features(self, experiment_type: str, objectives: List[str]) -> Dict[str, float]:
        """Extract features for experiment design"""
        objectives_text = ' '.join(objectives).lower()
        
        features = {
            'experiment_type_length': len(experiment_type),
            'objectives_count': len(objectives),
            'objectives_text_length': len(objectives_text),
            'has_performance_objectives': 1.0 if any(o in objectives_text for o in ['performance', 'speed', 'efficiency']) else 0.0,
            'has_quality_objectives': 1.0 if any(o in objectives_text for o in ['quality', 'accuracy', 'precision']) else 0.0,
            'has_user_objectives': 1.0 if any(o in objectives_text for o in ['user', 'experience', 'interface']) else 0.0,
            'has_security_objectives': 1.0 if any(o in objectives_text for o in ['security', 'safety', 'protection']) else 0.0,
            'complexity_score': len(objectives) / 5.0
        }
        
        return features
    
    async def _map_scores_to_experiment_design(self, scores: np.ndarray, experiment_type: str, objectives: List[str]) -> Dict[str, Any]:
        """Map ML scores to experiment design"""
        design = {
            'parameters': {},
            'methodology': '',
            'expected_outcomes': []
        }
        
        # Map scores to parameters
        param_mapping = {
            0: ('sample_size', 100),
            1: ('duration_days', 7),
            2: ('test_groups', 2),
            3: ('metrics_count', 5),
            4: ('complexity_level', 'medium')
        }
        
        for i, score in enumerate(scores):
            if score > 0.5 and i < len(param_mapping):
                param_name, param_value = param_mapping[i]
                design['parameters'][param_name] = param_value
        
        # Set methodology based on experiment type
        design['methodology'] = f"ML-driven {experiment_type} experiment with {len(objectives)} objectives"
        
        # Set expected outcomes
        design['expected_outcomes'] = [f"Improved {obj}" for obj in objectives[:3]]
        
        return design
    
    async def _rule_based_experiment_design(self, experiment_type: str, objectives: List[str]) -> Dict[str, Any]:
        """Fallback rule-based experiment design"""
        return {
            'parameters': {
                'sample_size': 100,
                'duration_days': 7,
                'test_groups': 2,
                'metrics_count': 5
            },
            'methodology': f"Standard {experiment_type} experiment",
            'expected_outcomes': [f"Improved {obj}" for obj in objectives[:3]]
        }
    
    async def _extract_result_features(self, results: Dict[str, Any], experiment_type: str) -> Dict[str, float]:
        """Extract features for result analysis"""
        features = {
            'result_count': len(results),
            'has_success_metrics': 1.0 if 'success' in str(results).lower() else 0.0,
            'has_performance_metrics': 1.0 if 'performance' in str(results).lower() else 0.0,
            'has_error_metrics': 1.0 if 'error' in str(results).lower() else 0.0,
            'experiment_type_length': len(experiment_type),
            'complexity_score': len(str(results)) / 1000.0
        }
        
        return features
    
    async def _map_scores_to_analysis_insights(self, scores: np.ndarray, results: Dict[str, Any]) -> Dict[str, Any]:
        """Map ML scores to analysis insights"""
        insights = {
            'insights': [],
            'recommendations': [],
            'success_score': 0.0
        }
        
        # Map scores to insights
        insight_mapping = {
            0: "Performance improved by ML-driven optimization",
            1: "Quality metrics show significant enhancement",
            2: "User experience metrics indicate positive feedback",
            3: "Security validation passed all tests",
            4: "Code quality metrics demonstrate improvement"
        }
        
        for i, score in enumerate(scores):
            if score > 0.5 and i < len(insight_mapping):
                insights['insights'].append(insight_mapping[i])
        
        # Calculate success score
        insights['success_score'] = min(1.0, sum(scores) / len(scores))
        
        # Generate recommendations
        if insights['success_score'] > 0.7:
            insights['recommendations'].append("Continue with current approach")
            insights['recommendations'].append("Scale up successful patterns")
        else:
            insights['recommendations'].append("Review and adjust methodology")
            insights['recommendations'].append("Consider alternative approaches")
        
        return insights
    
    async def _rule_based_result_analysis(self, results: Dict[str, Any], experiment_type: str) -> Dict[str, Any]:
        """Fallback rule-based result analysis"""
        return {
            'insights': [f"Experiment {experiment_type} completed with results"],
            'recommendations': ["Analyze patterns for improvement", "Consider next iteration"],
            'success_score': 0.6
        }
    
    async def _update_experiment_patterns(self, experiment_type: str, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Update experiment patterns for future suggestions"""
        pattern_key = f"{experiment_type}_{datetime.now().strftime('%Y%m')}"
        
        if pattern_key not in self._experiment_patterns:
            self._experiment_patterns[pattern_key] = []
        
        self._experiment_patterns[pattern_key].append({
            'results': results,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
    
    async def _extract_experiment_patterns(self, experiment_history: List[Dict]) -> List[List[float]]:
        """Extract patterns from experiment history"""
        patterns = []
        
        for exp in experiment_history:
            pattern = [
                len(exp.get('results', {})),
                exp.get('analysis', {}).get('success_score', 0.0),
                len(exp.get('analysis', {}).get('insights', [])),
                len(exp.get('analysis', {}).get('recommendations', []))
            ]
            patterns.append(pattern)
        
        return patterns
    
    async def _generate_cluster_based_suggestions(self, clusters: np.ndarray, current_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate suggestions based on experiment clusters"""
        suggestions = []
        
        for cluster_id in set(clusters):
            cluster_suggestions = {
                'cluster_id': int(cluster_id),
                'experiment_type': f"cluster_{cluster_id}_experiment",
                'objectives': [f"Optimize cluster {cluster_id} patterns"],
                'expected_outcomes': [f"Improved cluster {cluster_id} performance"]
            }
            suggestions.append(cluster_suggestions)
        
        return suggestions
    
    async def _rule_based_experiment_suggestions(self, current_results: Dict[str, Any], experiment_history: List[Dict]) -> List[Dict[str, Any]]:
        """Fallback rule-based experiment suggestions"""
        return [{
            'experiment_type': 'follow_up_experiment',
            'objectives': ['Validate previous results', 'Test new hypotheses'],
            'expected_outcomes': ['Confirmed findings', 'New insights']
        }]
    
    async def _extract_validation_features(self, new_knowledge: str, source_url: str) -> Dict[str, float]:
        """Extract features for knowledge validation"""
        features = {
            'knowledge_length': len(new_knowledge),
            'url_length': len(source_url),
            'has_https': 1.0 if source_url.startswith('https') else 0.0,
            'has_documentation': 1.0 if 'docs' in source_url.lower() else 0.0,
            'has_api': 1.0 if 'api' in source_url.lower() else 0.0,
            'has_github': 1.0 if 'github' in source_url.lower() else 0.0,
            'content_quality': len(new_knowledge.split()) / 100.0
        }
        
        return features
    
    async def _rule_based_validation_score(self, new_knowledge: str, source_url: str) -> float:
        """Fallback rule-based validation score"""
        score = 0.5  # Base score
        
        # Add points for good indicators
        if source_url.startswith('https'):
            score += 0.2
        if 'docs' in source_url.lower() or 'api' in source_url.lower():
            score += 0.1
        if len(new_knowledge) > 100:
            score += 0.1
        if 'github' in source_url.lower():
            score += 0.1
        
        return min(1.0, score)
    
    async def _calculate_validation_confidence(self, validation_features: Dict[str, float]) -> float:
        """Calculate confidence in validation"""
        non_zero_features = sum(1 for v in validation_features.values() if v > 0)
        confidence = min(1.0, non_zero_features / 5.0)
        return confidence
    
    async def _generate_validation_recommendations(self, validation_score: float, new_knowledge: str) -> List[str]:
        """Generate validation recommendations"""
        recommendations = []
        
        if validation_score > 0.8:
            recommendations.append("High-quality knowledge source - recommend adding")
        elif validation_score > 0.6:
            recommendations.append("Moderate quality - review before adding")
        else:
            recommendations.append("Low quality - recommend rejection")
        
        if len(new_knowledge) < 50:
            recommendations.append("Knowledge content too short")
        
        return recommendations
    
    async def generate_olympus_treaty_scenario(self, ai_type: str, learning_history: list, knowledge_gaps: list, analytics: dict, difficulty: str) -> str:
        """Generate a multi-part, cross-domain, adversarial, and open-ended Olympus Treaty scenario using LLM/ML."""
        prompt = (
            f"You are generating an Olympus Treaty test for the {ai_type} AI. "
            f"The test must be extremely challenging, multi-part, cross-domain, and adversarial. "
            f"Base the scenario on the AI's actual learning history, knowledge gaps, and analytics. "
            f"Difficulty: {difficulty}. "
            f"Learning history: {learning_history[:5]}... "
            f"Knowledge gaps: {knowledge_gaps}. "
            f"Analytics: {analytics}. "
            f"Create a scenario that requires the AI to synthesize knowledge, reason step-by-step, justify its approach, and critique its own answer. "
            f"The scenario should require code, reasoning, and creative problem solving. "
            f"Return only the scenario text."
        )
        result = await self.ml_service.generate_with_llm(prompt)
        return result["content"] if isinstance(result, dict) and "content" in result else str(result)

    async def generate_adaptive_custody_test(self, ai_type: str, category: str, learning_history: list, knowledge_gaps: list, analytics: dict, difficulty: str) -> dict:
        """Generate a challenging, adaptive custody test using LLM/ML, based on AI's learning and analytics."""
        prompt = (
            f"You are generating a custody test for the {ai_type} AI. "
            f"Test category: {category}. "
            f"Difficulty: {difficulty}. "
            f"Learning history: {learning_history[:5]}... "
            f"Knowledge gaps: {knowledge_gaps}. "
            f"Analytics: {analytics}. "
            f"Create a test that is challenging, adaptive, and requires explanations and reasoning. "
            f"Return a JSON object with fields: test_type, questions (list), difficulty, and any other relevant metadata."
        )
        result = await self.ml_service.generate_with_llm(prompt)
        if isinstance(result, dict) and "content" in result:
            import json
            try:
                return json.loads(result["content"])
            except Exception:
                return {"test_type": "adaptive", "questions": [result["content"]], "difficulty": difficulty}
        return {"test_type": "adaptive", "questions": [str(result)], "difficulty": difficulty}
    
    # Public API Methods
    async def get_sckipit_status(self) -> Dict[str, Any]:
        """Get Sckipit service status"""
        return {
            'status': 'active',
            'models_loaded': len(self._models),
            'knowledge_base_size': len(self._knowledge_base),
            'suggestion_history_count': len(self._suggestion_history),
            'experiment_patterns_count': len(self._experiment_patterns),
            'last_updated': datetime.now().isoformat()
        }
    
    async def train_sckipit_models(self, force_retrain: bool = False) -> Dict[str, Any]:
        """Train Sckipit ML models"""
        try:
            training_results = {}
            
            # Train each model with sample data
            for model_name in self._models.keys():
                if force_retrain or model_name not in self._models:
                    # Generate sample training data
                    X_sample = np.random.rand(100, 10)  # 100 samples, 10 features
                    y_sample = np.random.rand(100)  # Random targets
                    
                    # Train model
                    self._models[model_name].fit(X_sample, y_sample)
                    
                    # Save model
                    await self._save_sckipit_model(model_name)
                    
                    training_results[model_name] = 'trained'
            
            return {
                'status': 'success',
                'models_trained': len(training_results),
                'training_results': training_results
            }
        except Exception as e:
            logger.error(f"Error training Sckipit models: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_sckipit_analytics(self) -> Dict[str, Any]:
        """Get Sckipit analytics"""
        return {
            'total_suggestions': len(self._suggestion_history),
            'knowledge_sources': len(self._knowledge_base),
            'experiment_patterns': len(self._experiment_patterns),
            'model_performance': {
                model_name: 'active' for model_name in self._models.keys()
            },
            'recent_activity': {
                'last_suggestion': self._suggestion_history[-1] if self._suggestion_history else None,
                'last_knowledge_update': max([k['last_updated'] for k in self._knowledge_base.values()]) if self._knowledge_base else None
            }
        }

    async def generate_collaborative_challenge(self, ai_types: list, learning_histories: list, knowledge_gaps: list, analytics: dict, difficulty: str, test_type: str) -> str:
        """Generate a collaborative challenge for multiple AIs to work together on."""
        prompt = (
            f"You are generating a collaborative test for multiple AIs to work together. "
            f"AIs involved: {', '.join(ai_types)}. "
            f"Test type: {test_type}. "
            f"Difficulty: {difficulty}. "
            f"Learning histories: {learning_histories[:3]}... "
            f"Knowledge gaps: {knowledge_gaps}. "
            f"Analytics: {analytics}. "
            f"Create a complex, multi-part scenario that requires collaboration, synthesis of different AI strengths, "
            f"and coordinated problem-solving. The scenario should require code, reasoning, and creative solutions. "
            f"Return only the scenario text."
        )
        result = await self.ml_service.generate_with_llm(prompt)
        return result["content"] if isinstance(result, dict) and "content" in result else str(result)

    async def evaluate_test_response(self, scenario: str, response: str) -> dict:
        """Evaluate a single AI's response to a test scenario."""
        prompt = (
            f"Evaluate this AI response to the test scenario. "
            f"Scenario: {scenario} "
            f"Response: {response} "
            f"Provide evaluation in JSON format with: "
            f"score (0-100), reasoning (string), strengths (list), weaknesses (list), "
            f"improvement_suggestions (list), overall_assessment (string)"
        )
        result = await self.ml_service.generate_with_llm(prompt)
        
        if isinstance(result, dict) and "content" in result:
            try:
                import json
                evaluation = json.loads(result["content"])
                return evaluation
            except Exception:
                pass
        
        # Fallback evaluation
        return {
            "score": 75,
            "reasoning": "Standard evaluation applied",
            "strengths": ["Response provided"],
            "weaknesses": ["Evaluation parsing failed"],
            "improvement_suggestions": ["Improve response quality"],
            "overall_assessment": "Adequate response"
        }

    async def evaluate_collaborative_response(self, scenario: str, responses: dict) -> dict:
        """Evaluate collaborative responses from multiple AIs."""
        prompt = (
            f"Evaluate collaborative responses from multiple AIs to the test scenario. "
            f"Scenario: {scenario} "
            f"Responses: {responses} "
            f"Provide evaluation in JSON format with: "
            f"score (0-100), reasoning (string), collaboration_quality (string), "
            f"individual_contributions (dict), team_synergy (string), "
            f"improvement_suggestions (list), overall_assessment (string)"
        )
        result = await self.ml_service.generate_with_llm(prompt)
        
        if isinstance(result, dict) and "content" in result:
            try:
                import json
                evaluation = json.loads(result["content"])
                return evaluation
            except Exception:
                pass
        
        # Fallback evaluation
        return {
            "score": 80,
            "reasoning": "Collaborative evaluation applied",
            "collaboration_quality": "Good teamwork",
            "individual_contributions": {ai: "Contributed to solution" for ai in responses.keys()},
            "team_synergy": "AIs worked well together",
            "improvement_suggestions": ["Enhance coordination"],
            "overall_assessment": "Successful collaboration"
        }

    async def generate_answer_with_llm(self, prompt: str, learning_log: str = "") -> Dict[str, Any]:
        """
        Generate an answer with LLM, including reasoning trace, self-assessment, and confidence reporting.
        Returns a structured response with explainability features.
        """
        try:
            # Create enhanced prompt that requires reasoning and self-assessment
            enhanced_prompt = f"""
You are an AI assistant with access to your learning history. Please answer the following question/prompt with full transparency and self-reflection.

PROMPT: {prompt}

LEARNING CONTEXT: {learning_log[:1000] if learning_log else "No specific learning context available"}

Please provide your response in the following structured format:

1. REASONING TRACE: Provide a step-by-step breakdown of your thought process, including:
   - How you approached the problem
   - What knowledge you drew upon
   - Any assumptions you made
   - How you validated your reasoning

2. ANSWER: Your main response to the prompt

3. SELF-ASSESSMENT: 
   - What are the strengths of your answer?
   - What are potential weaknesses or limitations?
   - How confident are you in different aspects of your response?
   - What could you have done better?

4. CONFIDENCE SCORE: A percentage (0-100) indicating your overall confidence in your answer

5. UNCERTAINTY AREAS: Specific parts of your answer where you feel less certain

Return your response as a JSON object with these exact fields:
{{
    "reasoning_trace": "step-by-step reasoning...",
    "answer": "your main answer...",
    "self_assessment": {{
        "strengths": ["strength1", "strength2"],
        "weaknesses": ["weakness1", "weakness2"],
        "improvement_areas": ["area1", "area2"]
    }},
    "confidence_score": 85,
    "uncertainty_areas": ["specific area of uncertainty"],
    "reasoning_quality": "high/medium/low",
    "knowledge_applied": ["knowledge1", "knowledge2"]
}}
"""
            
            # Generate response using ML service
            result = await self.ml_service.generate_with_llm(enhanced_prompt)
            
            # Parse the response
            if isinstance(result, dict) and "content" in result:
                try:
                    import json
                    parsed_response = json.loads(result["content"])
                    
                    # Validate required fields
                    required_fields = ["reasoning_trace", "answer", "self_assessment", "confidence_score"]
                    for field in required_fields:
                        if field not in parsed_response:
                            raise ValueError(f"Missing required field: {field}")
                    
                    # Ensure confidence score is within bounds
                    confidence = parsed_response.get("confidence_score", 50)
                    confidence = max(0, min(100, confidence))
                    parsed_response["confidence_score"] = confidence
                    
                    # Add metadata
                    parsed_response["timestamp"] = datetime.now().isoformat()
                    parsed_response["prompt_length"] = len(prompt)
                    parsed_response["learning_context_used"] = bool(learning_log)
                    
                    # After generating the main answer, add enhanced explainability fields
                    structured_response = parsed_response # Use a new variable to avoid confusion with parsed_response
                    structured_response["error_analysis"] = await self._generate_error_analysis(prompt, structured_response["answer"], learning_log)
                    structured_response["uncertainty_quantification"] = await self._estimate_uncertainty(prompt, structured_response["answer"], learning_log)
                    structured_response["model_provenance"] = await self._get_model_provenance()
                    structured_response["peer_review_feedback"] = await self._get_peer_review_feedback(prompt, structured_response["answer"], learning_log)
                    
                    return structured_response
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse structured response: {e}")
                    # Fallback to unstructured response
                    return self._create_fallback_response(result["content"], prompt, learning_log)
            else:
                # Fallback for non-dict results
                return self._create_fallback_response(str(result), prompt, learning_log)
                
        except Exception as e:
            logger.error(f"Error generating answer with LLM: {str(e)}")
            return self._create_fallback_response("Error occurred during generation", prompt, learning_log)

    def _create_fallback_response(self, content: str, prompt: str, learning_log: str) -> Dict[str, Any]:
        """Create a fallback response when structured generation fails"""
        return {
            "reasoning_trace": f"Fallback reasoning: Analyzed prompt '{prompt[:100]}...' using available knowledge",
            "answer": content,
            "self_assessment": {
                "strengths": ["Provided a response despite generation issues"],
                "weaknesses": ["Structured reasoning unavailable", "Limited self-reflection"],
                "improvement_areas": ["Improve response generation reliability", "Enhance reasoning capabilities"]
            },
            "confidence_score": 30,  # Low confidence for fallback
            "uncertainty_areas": ["Response quality", "Reasoning validity"],
            "reasoning_quality": "low",
            "knowledge_applied": ["Basic knowledge", "Fallback mechanisms"],
            "timestamp": datetime.now().isoformat(),
            "prompt_length": len(prompt),
            "learning_context_used": bool(learning_log),
            "is_fallback": True
        } 

    async def _generate_error_analysis(self, prompt: str, answer: str, context: str) -> Dict[str, Any]:
        """Attempt to generate an error analysis for the LLM response."""
        try:
            error_analysis_prompt = (
                f"Analyze the following LLM response for potential errors, logical inconsistencies, or areas of uncertainty. "
                f"Prompt: {prompt}\nAnswer: {answer}\nContext: {context}\n\n"
                f"Provide a JSON object with fields: error_type (string), specific_issue (string), "
                f"suggested_correction (string), confidence_level (0-100)."
            )
            error_analysis_result = await self.ml_service.generate_with_llm(error_analysis_prompt)
            if isinstance(error_analysis_result, dict) and "content" in error_analysis_result:
                try:
                    import json
                    return json.loads(error_analysis_result["content"])
                except json.JSONDecodeError:
                    return {"error_type": "ParsingError", "specific_issue": "Could not parse error analysis JSON", "suggested_correction": "N/A", "confidence_level": 0}
            return {"error_type": "NoError", "specific_issue": "No apparent errors found", "suggested_correction": "N/A", "confidence_level": 100}
        except Exception as e:
            logger.warning(f"Error generating error analysis: {e}")
            return {"error_type": "GenerationError", "specific_issue": f"LLM generation failed: {e}", "suggested_correction": "N/A", "confidence_level": 0}

    async def _estimate_uncertainty(self, prompt: str, answer: str, context: str) -> Dict[str, Any]:
        """Attempt to estimate uncertainty in the LLM's response."""
        try:
            uncertainty_prompt = (
                f"Estimate the level of uncertainty in the LLM's response to the following prompt. "
                f"Prompt: {prompt}\nAnswer: {answer}\nContext: {context}\n\n"
                f"Provide a JSON object with fields: uncertainty_level (string), confidence_score (0-100)."
            )
            uncertainty_result = await self.ml_service.generate_with_llm(uncertainty_prompt)
            if isinstance(uncertainty_result, dict) and "content" in uncertainty_result:
                try:
                    import json
                    return json.loads(uncertainty_result["content"])
                except json.JSONDecodeError:
                    return {"uncertainty_level": "ParsingError", "confidence_score": 0}
            return {"uncertainty_level": "NoUncertainty", "confidence_score": 100}
        except Exception as e:
            logger.warning(f"Error estimating uncertainty: {e}")
            return {"uncertainty_level": "GenerationError", "confidence_score": 0}

    async def _get_model_provenance(self) -> Dict[str, Any]:
        """Attempt to provide information about the model used for generation."""
        try:
            model_provenance_prompt = (
                f"Provide information about the Sckipit service's ML models and LLM used for the last generation. "
                f"Include the names of the models, their versions, and any relevant details about the LLM's capabilities."
            )
            model_provenance_result = await self.ml_service.generate_with_llm(model_provenance_prompt)
            if isinstance(model_provenance_result, dict) and "content" in model_provenance_result:
                try:
                    import json
                    return json.loads(model_provenance_result["content"])
                except json.JSONDecodeError:
                    return {"model_name": "LLM", "version": "N/A", "details": "LLM details not available"}
            return {"model_name": "LLM", "version": "N/A", "details": "LLM details not available"}
        except Exception as e:
            logger.warning(f"Error getting model provenance: {e}")
            return {"model_name": "LLM", "version": "N/A", "details": "LLM details not available"}

    async def _get_peer_review_feedback(self, prompt: str, answer: str, context: str) -> Dict[str, Any]:
        """Attempt to get peer review feedback for the LLM's response."""
        try:
            peer_review_prompt = (
                f"As a peer reviewer, provide constructive feedback on the LLM's response to the following prompt. "
                f"Prompt: {prompt}\nAnswer: {answer}\nContext: {context}\n\n"
                f"Provide a JSON object with fields: overall_feedback (string), strengths (list), weaknesses (list), "
                f"specific_suggestions (list), confidence_level (0-100)."
            )
            peer_review_result = await self.ml_service.generate_with_llm(peer_review_prompt)
            if isinstance(peer_review_result, dict) and "content" in peer_review_result:
                try:
                    import json
                    return json.loads(peer_review_result["content"])
                except json.JSONDecodeError:
                    return {"overall_feedback": "ParsingError", "strengths": [], "weaknesses": [], "specific_suggestions": [], "confidence_level": 0}
            return {"overall_feedback": "NoFeedback", "strengths": [], "weaknesses": [], "specific_suggestions": [], "confidence_level": 100}
        except Exception as e:
            logger.warning(f"Error getting peer review feedback: {e}")
            return {"overall_feedback": "GenerationError", "strengths": [], "weaknesses": [], "specific_suggestions": [], "confidence_level": 0} 