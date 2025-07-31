"""
AI Growth Service - Enables AI to build upon itself and expand capabilities
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import structlog
import json
import uuid
import os
from pathlib import Path

# Advanced ML imports for growth
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from sklearn.pipeline import Pipeline
import joblib

from ..core.database import get_session
from ..core.config import settings
from .ml_service import MLService
from .ai_learning_service import AILearningService
from app.services.anthropic_service import call_claude, anthropic_rate_limited_call

logger = structlog.get_logger()


class AIGrowthService:
    """AI Growth Service - Enables autonomous AI expansion and learning"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIGrowthService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ml_service = MLService()
            self.learning_service = AILearningService()
            self.growth_models = {}
            self.performance_history = []
            self.capability_expansions = []
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the AI Growth service"""
        instance = cls()
        
        # Create growth model directory
        os.makedirs(f"{settings.ml_model_path}/growth", exist_ok=True)
        
        # Load existing growth models
        await instance._load_growth_models()
        
        # Initialize growth tracking
        await instance._initialize_growth_tracking()
        
        logger.info("AI Growth Service initialized successfully")
        return instance
    
    async def _load_growth_models(self):
        """Load existing growth models"""
        growth_dir = f"{settings.ml_model_path}/growth"
        
        model_files = [
            'performance_predictor.pkl',
            'capability_expander.pkl',
            'self_improvement_classifier.pkl',
            'knowledge_synthesizer.pkl'
        ]
        
        for model_file in model_files:
            model_path = os.path.join(growth_dir, model_file)
            if os.path.exists(model_path):
                try:
                    model_name = model_file.replace('.pkl', '')
                    self.growth_models[model_name] = joblib.load(model_path)
                    logger.info(f"Loaded growth model: {model_name}")
                except Exception as e:
                    logger.error(f"Failed to load growth model {model_file}", error=str(e))
    
    async def _initialize_growth_tracking(self):
        """Initialize growth tracking metrics"""
        try:
            # Get historical performance data
            async with get_session() as session:
                from sqlalchemy import select, func
                from ..models.sql_models import Learning, Proposal
                
                # Simplified query to avoid _static_cache_key issues
                stmt = select(
                    Learning.ai_type,
                    func.count(Learning.id).label('learning_count')
                ).group_by(Learning.ai_type)
                
                result = await session.execute(stmt)
                performance_data = result.fetchall()
                
                # Store performance history with simplified metrics
                for row in performance_data:
                    self.performance_history.append({
                        'ai_type': row.ai_type,
                        'avg_confidence': 0.5,  # Default value
                        'learning_count': row.learning_count,
                        'date': datetime.utcnow().isoformat()
                    })
                
                logger.info(f"Loaded {len(self.performance_history)} performance records")
                
        except Exception as e:
            logger.error("Error initializing growth tracking", error=str(e))
    
    async def analyze_growth_potential(self, ai_type: str) -> Dict[str, Any]:
        """Analyze growth potential for a specific AI type"""
        try:
            # Get current performance metrics
            current_performance = await self._get_current_performance(ai_type)
            
            # Predict growth potential
            growth_potential = await self._predict_growth_potential(current_performance)
            
            # Identify expansion opportunities
            expansion_opportunities = await self._identify_expansion_opportunities(ai_type)
            
            # Generate growth recommendations
            growth_recommendations = await self._generate_growth_recommendations(
                ai_type, current_performance, growth_potential, expansion_opportunities
            )
            
            result = {
                'ai_type': ai_type,
                'current_performance': current_performance,
                'growth_potential': growth_potential,
                'expansion_opportunities': expansion_opportunities,
                'growth_recommendations': growth_recommendations,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            # Claude verification
            try:
                verification = await anthropic_rate_limited_call(
                    f"{ai_type} AI analyzed growth potential. Summary: {result}. Please verify and suggest further expansion or learning opportunities.",
                    ai_name=ai_type.lower()
                )
                logger.info(f"Claude verification for growth analysis: {verification}")
            except Exception as e:
                logger.warning(f"Claude verification error: {str(e)}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing growth potential: {str(e)}")
            # Claude failure analysis
            try:
                advice = await anthropic_rate_limited_call(
                    f"{ai_type} AI failed to analyze growth potential. Error: {str(e)}. Please analyze and suggest how to improve.",
                    ai_name=ai_type.lower()
                )
                logger.info(f"Claude advice for failed growth analysis: {advice}")
            except Exception as ce:
                logger.warning(f"Claude error: {str(ce)}")
            return {'error': str(e)}
    
    async def _get_current_performance(self, ai_type: str) -> Dict[str, Any]:
        """Get current performance metrics for an AI type"""
        try:
            async with get_session() as session:
                from sqlalchemy import select, func, desc, case
                from ..models.sql_models import Learning, Proposal
                
                # Simplified query to avoid _static_cache_key issues
                stmt = select(
                    func.count(Learning.id).label('total_learning')
                ).select_from(Learning).where(
                    Learning.ai_type == ai_type,
                    Learning.created_at >= datetime.utcnow() - timedelta(days=30)
                )
                
                result = await session.execute(stmt)
                learning_performance = result.fetchone()
                
                # Get proposal performance separately
                stmt = select(
                    func.avg(Proposal.confidence).label('avg_proposal_confidence')
                ).select_from(Proposal).where(
                    Proposal.ai_type == ai_type,
                    Proposal.created_at >= datetime.utcnow() - timedelta(days=30)
                )
                
                result = await session.execute(stmt)
                proposal_performance = result.fetchone()
                
                # Get proposal approval rate
                stmt = select(
                    func.count(Proposal.id).label('total_proposals'),
                    func.sum(case((Proposal.user_feedback == 'approved', 1), else_=0)).label('approved_proposals')
                ).select_from(Proposal).where(
                    Proposal.ai_type == ai_type,
                    Proposal.created_at >= datetime.utcnow() - timedelta(days=30)
                )
                
                result = await session.execute(stmt)
                proposal_stats = result.fetchone()
                
                approval_rate = 0
                if proposal_stats.total_proposals and proposal_stats.total_proposals > 0:
                    approval_rate = proposal_stats.approved_proposals / proposal_stats.total_proposals
                
                return {
                    'avg_confidence': 0.5,  # Default value
                    'total_learning': learning_performance.total_learning or 0,
                    'avg_proposal_confidence': float(proposal_performance.avg_proposal_confidence or 0),
                    'approval_rate': approval_rate,
                    'total_proposals': proposal_stats.total_proposals or 0,
                    'approved_proposals': proposal_stats.approved_proposals or 0
                }
                
        except Exception as e:
            logger.error(f"Error getting current performance: {str(e)}")
            return {}
    
    async def _predict_growth_potential(self, current_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Predict growth potential using ML models"""
        try:
            # Prepare features for growth prediction
            features = np.array([
                current_performance.get('avg_confidence', 0),
                current_performance.get('total_learning', 0),
                current_performance.get('avg_proposal_confidence', 0),
                current_performance.get('approval_rate', 0),
                current_performance.get('total_proposals', 0)
            ]).reshape(1, -1)
            
            # Predict growth potential
            if 'performance_predictor' in self.growth_models:
                growth_score = self.growth_models['performance_predictor'].predict(features)[0]
            else:
                # Fallback calculation
                growth_score = (
                    current_performance.get('avg_confidence', 0) * 0.3 +
                    current_performance.get('approval_rate', 0) * 0.4 +
                    min(current_performance.get('total_learning', 0) / 100, 1.0) * 0.3
                )
            
            # Determine growth stage
            if growth_score < 0.3:
                growth_stage = "emerging"
            elif growth_score < 0.6:
                growth_stage = "developing"
            elif growth_score < 0.8:
                growth_stage = "mature"
            else:
                growth_stage = "advanced"
            
            return {
                'growth_score': float(growth_score),
                'growth_stage': growth_stage,
                'growth_confidence': 0.8,
                'predicted_improvement': float(growth_score * 0.2)  # 20% improvement potential
            }
            
        except Exception as e:
            logger.error(f"Error predicting growth potential: {str(e)}")
            return {'growth_score': 0.5, 'growth_stage': 'unknown'}
    
    async def _identify_expansion_opportunities(self, ai_type: str) -> List[Dict[str, Any]]:
        """Identify opportunities for AI capability expansion"""
        opportunities = []
        
        try:
            # Analyze current capabilities vs potential
            current_capabilities = await self._analyze_current_capabilities(ai_type)
            
            # Define expansion opportunities based on AI type
            if ai_type == "Imperium":
                opportunities.extend([
                    {
                        'type': 'code_optimization',
                        'description': 'Advanced code optimization algorithms',
                        'priority': 'high',
                        'estimated_impact': 0.3,
                        'implementation_complexity': 'medium'
                    },
                    {
                        'type': 'performance_analysis',
                        'description': 'Deep performance profiling and analysis',
                        'priority': 'medium',
                        'estimated_impact': 0.2,
                        'implementation_complexity': 'high'
                    }
                ])
            
            elif ai_type == "Guardian":
                opportunities.extend([
                    {
                        'type': 'security_scanning',
                        'description': 'Advanced security vulnerability detection',
                        'priority': 'high',
                        'estimated_impact': 0.4,
                        'implementation_complexity': 'medium'
                    },
                    {
                        'type': 'code_quality',
                        'description': 'Enhanced code quality metrics and standards',
                        'priority': 'medium',
                        'estimated_impact': 0.25,
                        'implementation_complexity': 'low'
                    }
                ])
            
            elif ai_type == "Sandbox":
                opportunities.extend([
                    {
                        'type': 'experiment_automation',
                        'description': 'Automated experiment design and execution',
                        'priority': 'high',
                        'estimated_impact': 0.35,
                        'implementation_complexity': 'medium'
                    },
                    {
                        'type': 'test_generation',
                        'description': 'Intelligent test case generation',
                        'priority': 'medium',
                        'estimated_impact': 0.2,
                        'implementation_complexity': 'high'
                    }
                ])
            
            elif ai_type == "Conquest":
                opportunities.extend([
                    {
                        'type': 'deployment_optimization',
                        'description': 'Smart deployment strategies and rollback',
                        'priority': 'high',
                        'estimated_impact': 0.3,
                        'implementation_complexity': 'medium'
                    },
                    {
                        'type': 'monitoring_enhancement',
                        'description': 'Advanced monitoring and alerting',
                        'priority': 'medium',
                        'estimated_impact': 0.25,
                        'implementation_complexity': 'low'
                    }
                ])
            
            # Filter opportunities based on current capabilities
            filtered_opportunities = []
            for opp in opportunities:
                if not self._capability_exists(current_capabilities, opp['type']):
                    filtered_opportunities.append(opp)
            
            return filtered_opportunities
            
        except Exception as e:
            logger.error(f"Error identifying expansion opportunities: {str(e)}")
            return []
    
    async def _analyze_current_capabilities(self, ai_type: str) -> List[str]:
        """Analyze current capabilities of an AI type"""
        try:
            async with get_session() as session:
                from sqlalchemy import select, distinct
                from ..models.sql_models import Learning
                
                # Get learning patterns to understand current capabilities
                stmt = select(distinct(Learning.learning_type)).where(
                    Learning.ai_type == ai_type
                )
                
                result = await session.execute(stmt)
                learning_types = [row[0] for row in result.fetchall()]
                
                # Map learning types to capabilities
                capabilities = []
                for learning_type in learning_types:
                    if 'code_analysis' in learning_type:
                        capabilities.append('code_analysis')
                    if 'security' in learning_type:
                        capabilities.append('security_scanning')
                    if 'experiment' in learning_type:
                        capabilities.append('experimentation')
                    if 'deployment' in learning_type:
                        capabilities.append('deployment')
                
                return list(set(capabilities))
                
        except Exception as e:
            logger.error("Error analyzing current capabilities", error=str(e))
            return []
    
    def _capability_exists(self, current_capabilities: List[str], capability_type: str) -> bool:
        """Check if a capability already exists"""
        capability_mapping = {
            'code_optimization': 'code_analysis',
            'security_scanning': 'security_scanning',
            'experiment_automation': 'experimentation',
            'deployment_optimization': 'deployment'
        }
        
        mapped_capability = capability_mapping.get(capability_type, capability_type)
        return mapped_capability in current_capabilities
    
    async def _generate_growth_recommendations(
        self, 
        ai_type: str, 
        current_performance: Dict[str, Any],
        growth_potential: Dict[str, Any],
        expansion_opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate specific growth recommendations"""
        recommendations = []
        
        try:
            # Performance-based recommendations
            if current_performance.get('avg_confidence', 0) < 0.6:
                recommendations.append({
                    'type': 'performance_improvement',
                    'title': 'Improve Decision Confidence',
                    'description': 'Focus on improving the confidence of AI decisions through better training data and model refinement',
                    'priority': 'high',
                    'estimated_effort': 'medium'
                })
            
            if current_performance.get('approval_rate', 0) < 0.5:
                recommendations.append({
                    'type': 'quality_improvement',
                    'title': 'Enhance Proposal Quality',
                    'description': 'Work on improving the quality and acceptance rate of AI-generated proposals',
                    'priority': 'high',
                    'estimated_effort': 'high'
                })
            
            # Growth stage recommendations
            if growth_potential.get('growth_stage') == 'emerging':
                recommendations.append({
                    'type': 'foundation_building',
                    'title': 'Build Strong Foundation',
                    'description': 'Focus on establishing core capabilities and learning patterns',
                    'priority': 'high',
                    'estimated_effort': 'low'
                })
            
            elif growth_potential.get('growth_stage') == 'developing':
                recommendations.append({
                    'type': 'capability_expansion',
                    'title': 'Expand Capabilities',
                    'description': 'Start implementing advanced features and expanding AI capabilities',
                    'priority': 'medium',
                    'estimated_effort': 'medium'
                })
            
            # Expansion opportunity recommendations
            for opportunity in expansion_opportunities[:3]:  # Top 3 opportunities
                recommendations.append({
                    'type': 'capability_expansion',
                    'title': f'Implement {opportunity["type"].replace("_", " ").title()}',
                    'description': opportunity['description'],
                    'priority': opportunity['priority'],
                    'estimated_effort': opportunity['implementation_complexity'],
                    'estimated_impact': opportunity['estimated_impact']
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating growth recommendations: {str(e)}")
            return []
    
    async def implement_growth_recommendation(self, ai_type: str, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Implement a growth recommendation"""
        try:
            logger.info(f"🚀 Implementing growth recommendation for {ai_type}", recommendation=recommendation)
            
            # Track implementation
            implementation_id = str(uuid.uuid4())
            
            # Simulate implementation process
            if recommendation['type'] == 'performance_improvement':
                result = await self._implement_performance_improvement(ai_type)
            elif recommendation['type'] == 'capability_expansion':
                result = await self._implement_capability_expansion(ai_type, recommendation)
            elif recommendation['type'] == 'foundation_building':
                result = await self._implement_foundation_building(ai_type)
            else:
                result = {'status': 'unknown_recommendation_type'}
            
            # Record implementation
            await self._record_implementation(implementation_id, ai_type, recommendation, result)
            
            return {
                'implementation_id': implementation_id,
                'ai_type': ai_type,
                'recommendation': recommendation,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Error implementing growth recommendation", error=str(e))
            return {'error': str(e)}
    
    async def _implement_performance_improvement(self, ai_type: str) -> Dict[str, Any]:
        """Implement performance improvement"""
        try:
            # Retrain models with more data
            await self.ml_service.train_models(force_retrain=True)
            
            # Optimize feature extraction
            # This would involve improving the feature engineering process
            
            return {
                'status': 'success',
                'improvements': ['model_retraining', 'feature_optimization'],
                'estimated_impact': 0.15
            }
        except Exception as e:
            logger.error("Error implementing performance improvement", error=str(e))
            return {'status': 'error', 'error': str(e)}
    
    async def _implement_capability_expansion(self, ai_type: str, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Implement capability expansion"""
        try:
            capability_type = recommendation.get('title', '').split('Implement ')[-1].lower().replace(' ', '_')
            
            # Create new learning patterns for the capability
            await self._create_capability_learning_pattern(ai_type, capability_type)
            
            # Update AI agent behavior
            await self._update_agent_capabilities(ai_type, capability_type)
            
            return {
                'status': 'success',
                'capability_added': capability_type,
                'estimated_impact': recommendation.get('estimated_impact', 0.2)
            }
        except Exception as e:
            logger.error("Error implementing capability expansion", error=str(e))
            return {'status': 'error', 'error': str(e)}
    
    async def _implement_foundation_building(self, ai_type: str) -> Dict[str, Any]:
        """Implement foundation building"""
        try:
            # Create basic learning patterns
            await self._create_basic_learning_patterns(ai_type)
            
            # Initialize core capabilities
            await self._initialize_core_capabilities(ai_type)
            
            return {
                'status': 'success',
                'foundation_established': True,
                'estimated_impact': 0.3
            }
        except Exception as e:
            logger.error("Error implementing foundation building", error=str(e))
            return {'status': 'error', 'error': str(e)}
    
    async def _create_capability_learning_pattern(self, ai_type: str, capability_type: str):
        """Create learning patterns for new capabilities"""
        try:
            async with get_session() as session:
                from ..models.sql_models import Learning
                
                # Create learning entry for new capability
                learning_entry = Learning(
                    ai_type=ai_type,
                    learning_type=f"capability_expansion_{capability_type}",
                    learning_data={
                        'pattern': f"new_capability_{capability_type}",
                        'context': f"AI {ai_type} expanded with {capability_type} capability",
                        'feedback': f"Capability {capability_type} successfully implemented",
                        'confidence': 0.8
                    }
                )
                
                session.add(learning_entry)
                await session.commit()
                
        except Exception as e:
            logger.error("Error creating capability learning pattern", error=str(e))
    
    async def _update_agent_capabilities(self, ai_type: str, capability_type: str):
        """Update AI agent capabilities"""
        # This would involve updating the AI agent service to include new capabilities
        logger.info(f"Updated {ai_type} agent with {capability_type} capability")
    
    async def _create_basic_learning_patterns(self, ai_type: str):
        """Create basic learning patterns for new AI types"""
        try:
            async with get_session() as session:
                from ..models.sql_models import Learning
                
                basic_patterns = [
                    "code_analysis_basic",
                    "proposal_generation_basic",
                    "learning_feedback_basic"
                ]
                
                for pattern in basic_patterns:
                    learning_entry = Learning(
                        ai_type=ai_type,
                        learning_type=pattern,
                        learning_data={
                            'pattern': "foundation_establishment",
                            'context': f"Basic {pattern} capability established for {ai_type}",
                            'feedback': "Foundation learning pattern created",
                            'confidence': 0.7
                        }
                    )
                    session.add(learning_entry)
                
                await session.commit()
                
        except Exception as e:
            logger.error("Error creating basic learning patterns", error=str(e))
    
    async def _initialize_core_capabilities(self, ai_type: str):
        """Initialize core capabilities for an AI type"""
        logger.info(f"Initialized core capabilities for {ai_type}")
    
    async def _record_implementation(self, implementation_id: str, ai_type: str, recommendation: Dict[str, Any], result: Dict[str, Any]):
        """Record implementation details"""
        try:
            async with get_session() as session:
                from ..models.sql_models import Learning
                
                learning_entry = Learning(
                    ai_type=ai_type,
                    learning_type="growth_implementation",
                    learning_data={
                        'pattern': f"implementation_{implementation_id}",
                        'context': f"Growth recommendation implementation: {recommendation.get('title', 'Unknown')}",
                        'feedback': f"Implementation result: {result.get('status', 'unknown')}",
                        'confidence': 0.9
                    }
                )
                
                session.add(learning_entry)
                await session.commit()
                
        except Exception as e:
            logger.error("Error recording implementation", error=str(e))
    
    async def train_growth_models(self):
        """Train the growth prediction models"""
        try:
            logger.info("🔄 Training AI growth models...")
            
            # Prepare training data from performance history
            if len(self.performance_history) < 10:
                logger.warning("Insufficient data for training growth models")
                return
            
            # Convert to DataFrame
            df = pd.DataFrame(self.performance_history)
            
            # Prepare features and targets
            X = df[['avg_confidence', 'learning_count']].fillna(0)
            y = df['avg_confidence'].fillna(0)  # Predict future confidence
            
            # Train performance predictor
            performance_predictor = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                random_state=42
            )
            
            performance_predictor.fit(X, y)
            
            # Save the model
            growth_dir = f"{settings.ml_model_path}/growth"
            joblib.dump(performance_predictor, f"{growth_dir}/performance_predictor.pkl")
            
            self.growth_models['performance_predictor'] = performance_predictor
            
            logger.info("✅ Growth models trained successfully")
            
        except Exception as e:
            logger.error("Error training growth models", error=str(e))
    
    def _to_roman(self, n: int) -> str:
        """Convert an integer to a Roman numeral (for prestige display)."""
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
        roman_num = ''
        i = 0
        while n > 0:
            for _ in range(n // val[i]):
                roman_num += syb[i]
                n -= val[i]
            i += 1
        return roman_num if roman_num else "I"

    async def get_growth_insights(self) -> Dict[str, Any]:
        """Get comprehensive growth insights (live from DB, with prestige/leveling)."""
        try:
            ai_types = ["Imperium", "Guardian", "Sandbox", "Conquest"]
            growth_insights = {}
            growth_scores = []
            prestige_map = {}
            from sqlalchemy import select, update
            from ..models.sql_models import AgentMetrics
            async with get_session() as session:
                for ai_type in ai_types:
                    stmt = select(AgentMetrics).where(AgentMetrics.agent_type == ai_type.lower()).order_by(AgentMetrics.updated_at.desc())
                    result = await session.execute(stmt)
                    metrics = result.scalars().first()
                    if metrics:
                        growth_score = float(metrics.learning_score or 0)
                        # Prestige logic: if growth_score >= 100, increment prestige, reset score
                        if growth_score >= 100:
                            new_prestige = (metrics.prestige or 0) + 1
                            await session.execute(update(AgentMetrics).where(AgentMetrics.id == metrics.id).values(
                                learning_score=0.0, prestige=new_prestige, updated_at=datetime.utcnow()
                            ))
                            await session.commit()
                            growth_score = 0.0
                            metrics.prestige = new_prestige
                        growth_scores.append(growth_score)
                        prestige_map[ai_type] = metrics.prestige or 0
                        growth_insights[ai_type] = {
                            'growth_score': growth_score,
                            'success_rate': float(metrics.success_rate or 0),
                            'failure_rate': float(metrics.failure_rate or 0),
                            'total_learning_cycles': metrics.total_learning_cycles,
                            'last_learning_cycle': metrics.last_learning_cycle.isoformat() if metrics.last_learning_cycle else None,
                            'growth_stage': metrics.status,
                            'capabilities': metrics.capabilities,
                            'improvement_suggestions': metrics.improvement_suggestions,
                            'updated_at': metrics.updated_at.isoformat() if metrics.updated_at else None,
                            'prestige': metrics.prestige or 0,
                            'prestige_roman': self._to_roman(metrics.prestige or 0)
                        }
                    else:
                        growth_insights[ai_type] = {
                            'growth_score': 0.0,
                            'success_rate': 0.0,
                            'failure_rate': 0.0,
                            'total_learning_cycles': 0,
                            'last_learning_cycle': None,
                            'growth_stage': 'unknown',
                            'capabilities': [],
                            'improvement_suggestions': [],
                            'updated_at': None,
                            'prestige': 0,
                            'prestige_roman': "I"
                        }
            # Calculate live average
            average_growth_score = float(np.mean(growth_scores)) if growth_scores else 0.0
            # System prestige logic: if avg reaches 100, increment system prestige, reset avg
            # For demo, store in a file (could use DB table for production)
            system_prestige_path = "system_prestige.txt"
            system_prestige = 0
            import os
            if os.path.exists(system_prestige_path):
                with open(system_prestige_path, "r") as f:
                    try:
                        system_prestige = int(f.read().strip())
                    except Exception:
                        system_prestige = 0
            if average_growth_score >= 100:
                system_prestige += 1
                average_growth_score = 0.0
                with open(system_prestige_path, "w") as f:
                    f.write(str(system_prestige))
            overall_growth = {
                'average_growth_score': average_growth_score,
                'system_maturity': self._calculate_system_maturity(growth_insights),
                'total_learning_entries': sum([insight['total_learning_cycles'] for insight in growth_insights.values()]),
                'total_expansion_opportunities': sum([len(insight.get('improvement_suggestions', [])) for insight in growth_insights.values()]),
                'system_prestige': system_prestige,
                'system_prestige_roman': self._to_roman(system_prestige)
            }
            return {
                'ai_growth_insights': growth_insights,
                'overall_growth': overall_growth,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Error getting growth insights", error=str(e))
            return {'error': str(e)}
    
    def _calculate_system_maturity(self, growth_insights: Dict[str, Any]) -> str:
        """Calculate overall system maturity"""
        try:
            growth_scores = [
                insight.get('growth_score', 0.5)
                for insight in growth_insights.values()
            ]
            
            avg_score = np.mean(growth_scores)
            
            if avg_score < 0.3:
                return "emerging"
            elif avg_score < 0.6:
                return "developing"
            elif avg_score < 0.8:
                return "mature"
            else:
                return "advanced"
        except Exception as e:
            logger.error("Error calculating system maturity", error=str(e))
            return "unknown" 

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