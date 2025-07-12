#!/usr/bin/env python3
"""
Enhanced Training Scheduler
==========================

This service provides intelligent scheduling for ML model training,
ensuring continuous learning and improvement based on:

1. Data availability and quality
2. Model performance degradation
3. User feedback patterns
4. Cross-AI learning opportunities
5. Adaptive training frequency
6. Performance monitoring and alerts
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np
from dataclasses import dataclass
from enum import Enum

from ..core.config import settings
from ..core.database import get_session
from ..models.sql_models import Proposal, Learning
from .enhanced_ml_learning_service import EnhancedMLLearningService

logger = logging.getLogger(__name__)

class TrainingTrigger(Enum):
    """Training trigger types"""
    SCHEDULED = "scheduled"
    DATA_AVAILABLE = "data_available"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    USER_FEEDBACK = "user_feedback"
    CROSS_AI_LEARNING = "cross_ai_learning"
    MANUAL = "manual"

@dataclass
class TrainingMetrics:
    """Training metrics tracking"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_samples: int
    validation_samples: int
    training_time: float
    timestamp: datetime

class EnhancedTrainingScheduler:
    """Enhanced Training Scheduler for continuous ML improvement"""
    
    _instance = None
    _initialized = False
    _running = False
    _training_history = []
    _performance_thresholds = {
        'accuracy': 0.75,
        'precision': 0.70,
        'recall': 0.70,
        'f1_score': 0.70
    }
    _training_intervals = {
        'scheduled': timedelta(hours=6),  # Every 6 hours
        'data_available': timedelta(hours=2),  # Every 2 hours if new data
        'performance_degradation': timedelta(minutes=30),  # Immediate if performance drops
        'user_feedback': timedelta(hours=1),  # Every hour if user feedback
        'cross_ai_learning': timedelta(hours=4)  # Every 4 hours for cross-AI learning
    }
    _last_training = {}
    _ml_service = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_scheduler()
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the enhanced training scheduler"""
        if not cls._initialized:
            instance = cls()
            instance._ml_service = await EnhancedMLLearningService.initialize()
            await instance._load_training_history()
            cls._initialized = True
            logger.info("Enhanced Training Scheduler initialized")
        return cls()
    
    def _initialize_scheduler(self):
        """Initialize scheduler components"""
        try:
            # Initialize training triggers
            for trigger in TrainingTrigger:
                self._last_training[trigger.value] = None
            
            logger.info("Training scheduler initialized")
            
        except Exception as e:
            logger.error(f"Error initializing training scheduler: {str(e)}")
    
    async def _load_training_history(self):
        """Load training history from database"""
        try:
            async with get_session() as session:
                from sqlalchemy import select, desc
                
                # Get recent learning entries for training history
                stmt = select(Learning).order_by(desc(Learning.created_at)).limit(100)
                result = await session.execute(stmt)
                learning_entries = result.scalars().all()
                
                for entry in learning_entries:
                    self._training_history.append({
                        'ai_type': entry.ai_type,
                        'learning_type': entry.learning_type,
                        'confidence': entry.confidence,
                        'created_at': entry.created_at.isoformat(),
                        'pattern': entry.pattern
                    })
                
                logger.info(f"Loaded {len(self._training_history)} training history records")
                
        except Exception as e:
            logger.error(f"Error loading training history: {str(e)}")
    
    async def start_continuous_training(self):
        """Start continuous training monitoring"""
        if self._running:
            logger.warning("Training scheduler already running")
            return
        
        self._running = True
        logger.info("🚀 Starting continuous training scheduler")
        
        try:
            while self._running:
                await self._check_training_triggers()
                await asyncio.sleep(300)  # Check every 5 minutes
                
        except asyncio.CancelledError:
            logger.info("Training scheduler cancelled")
        except Exception as e:
            logger.error(f"Error in continuous training: {str(e)}")
        finally:
            self._running = False
    
    async def stop_continuous_training(self):
        """Stop continuous training monitoring"""
        self._running = False
        logger.info("🛑 Stopped continuous training scheduler")
    
    async def _check_training_triggers(self):
        """Check all training triggers"""
        try:
            triggers = []
            
            # Check scheduled training
            if await self._should_schedule_training():
                triggers.append(TrainingTrigger.SCHEDULED)
            
            # Check data availability
            if await self._has_new_training_data():
                triggers.append(TrainingTrigger.DATA_AVAILABLE)
            
            # Check performance degradation
            if await self._detect_performance_degradation():
                triggers.append(TrainingTrigger.PERFORMANCE_DEGRADATION)
            
            # Check user feedback patterns
            if await self._has_significant_user_feedback():
                triggers.append(TrainingTrigger.USER_FEEDBACK)
            
            # Check cross-AI learning opportunities
            if await self._has_cross_ai_learning_opportunities():
                triggers.append(TrainingTrigger.CROSS_AI_LEARNING)
            
            # Execute training if triggers are active
            if triggers:
                await self._execute_training(triggers)
            
        except Exception as e:
            logger.error(f"Error checking training triggers: {str(e)}")
    
    async def _should_schedule_training(self) -> bool:
        """Check if scheduled training should occur"""
        try:
            last_scheduled = self._last_training.get(TrainingTrigger.SCHEDULED.value)
            if not last_scheduled:
                return True
            
            time_since_last = datetime.now() - last_scheduled
            return time_since_last >= self._training_intervals['scheduled']
            
        except Exception as e:
            logger.error(f"Error checking scheduled training: {str(e)}")
            return False
    
    async def _has_new_training_data(self) -> bool:
        """Check if new training data is available"""
        try:
            async with get_session() as session:
                from sqlalchemy import select, func
                
                # Check for new proposals in the last 2 hours
                two_hours_ago = datetime.now() - timedelta(hours=2)
                stmt = select(func.count(Proposal.id)).where(
                    Proposal.created_at >= two_hours_ago,
                    Proposal.user_feedback.in_(["approved", "rejected"])
                )
                result = await session.execute(stmt)
                new_proposals = result.scalar()
                
                # Check for new learning entries
                stmt = select(func.count(Learning.id)).where(
                    Learning.created_at >= two_hours_ago
                )
                result = await session.execute(stmt)
                new_learning = result.scalar()
                
                return new_proposals > 10 or new_learning > 20
                
        except Exception as e:
            logger.error(f"Error checking new training data: {str(e)}")
            return False
    
    async def _detect_performance_degradation(self) -> bool:
        """Detect if model performance has degraded"""
        try:
            if not self._training_history:
                return False
            
            # Get recent performance metrics
            recent_metrics = await self._get_recent_performance_metrics()
            
            if not recent_metrics:
                return False
            
            # Check against thresholds
            for metric, threshold in self._performance_thresholds.items():
                if metric in recent_metrics and recent_metrics[metric] < threshold:
                    logger.warning(f"Performance degradation detected: {metric} = {recent_metrics[metric]} < {threshold}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting performance degradation: {str(e)}")
            return False
    
    async def _has_significant_user_feedback(self) -> bool:
        """Check if there's significant user feedback to learn from"""
        try:
            async with get_session() as session:
                from sqlalchemy import select, func
                
                # Check for user feedback in the last hour
                one_hour_ago = datetime.now() - timedelta(hours=1)
                stmt = select(func.count(Proposal.id)).where(
                    Proposal.created_at >= one_hour_ago,
                    Proposal.user_feedback.in_(["approved", "rejected"])
                )
                result = await session.execute(stmt)
                recent_feedback = result.scalar()
                
                return recent_feedback > 5
                
        except Exception as e:
            logger.error(f"Error checking user feedback: {str(e)}")
            return False
    
    async def _has_cross_ai_learning_opportunities(self) -> bool:
        """Check if there are cross-AI learning opportunities"""
        try:
            if not self._ml_service:
                return False
            
            analytics = await self._ml_service.get_enhanced_ml_analytics()
            opportunities = analytics.get('cross_ai_knowledge', {}).get('knowledge_transfer_opportunities', [])
            
            # Check if there are high-value transfer opportunities
            high_value_opportunities = [
                opp for opp in opportunities 
                if opp.get('transfer_value', 0) > 0.7
            ]
            
            return len(high_value_opportunities) > 3
            
        except Exception as e:
            logger.error(f"Error checking cross-AI learning opportunities: {str(e)}")
            return False
    
    async def _execute_training(self, triggers: List[TrainingTrigger]):
        """Execute training based on triggers"""
        try:
            logger.info(f"🔄 Executing training with triggers: {[t.value for t in triggers]}")
            
            # Determine training priority
            priority = self._get_training_priority(triggers)
            
            # Execute training
            training_result = await self._ml_service.train_enhanced_models(force_retrain=True)
            
            if training_result.get('status') == 'success':
                # Record training metrics
                metrics = await self._calculate_training_metrics(training_result)
                self._training_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'triggers': [t.value for t in triggers],
                    'priority': priority,
                    'metrics': metrics,
                    'training_samples': training_result.get('training_samples', 0)
                })
                
                # Update last training times
                for trigger in triggers:
                    self._last_training[trigger.value] = datetime.now()
                
                logger.info(f"✅ Training completed successfully", 
                           triggers=[t.value for t in triggers],
                           samples=training_result.get('training_samples', 0))
                
                # Check if performance improved
                await self._check_performance_improvement(metrics)
                
            else:
                logger.error(f"❌ Training failed: {training_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error executing training: {str(e)}")
    
    def _get_training_priority(self, triggers: List[TrainingTrigger]) -> str:
        """Get training priority based on triggers"""
        if TrainingTrigger.PERFORMANCE_DEGRADATION in triggers:
            return "high"
        elif TrainingTrigger.USER_FEEDBACK in triggers:
            return "medium"
        elif TrainingTrigger.CROSS_AI_LEARNING in triggers:
            return "medium"
        else:
            return "normal"
    
    async def _calculate_training_metrics(self, training_result: Dict[str, Any]) -> TrainingMetrics:
        """Calculate training metrics"""
        try:
            results = training_result.get('training_results', {})
            
            # Calculate average metrics
            accuracies = [results.get(f'{model}_accuracy', 0.5) for model in results.keys()]
            precisions = [results.get(f'{model}_precision', 0.5) for model in results.keys()]
            recalls = [results.get(f'{model}_recall', 0.5) for model in results.keys()]
            f1_scores = [results.get(f'{model}_f1', 0.5) for model in results.keys()]
            
            return TrainingMetrics(
                accuracy=np.mean(accuracies) if accuracies else 0.5,
                precision=np.mean(precisions) if precisions else 0.5,
                recall=np.mean(recalls) if recalls else 0.5,
                f1_score=np.mean(f1_scores) if f1_scores else 0.5,
                training_samples=training_result.get('training_samples', 0),
                validation_samples=int(training_result.get('training_samples', 0) * 0.2),
                training_time=training_result.get('training_time', 0.0),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error calculating training metrics: {str(e)}")
            return TrainingMetrics(
                accuracy=0.5, precision=0.5, recall=0.5, f1_score=0.5,
                training_samples=0, validation_samples=0, training_time=0.0,
                timestamp=datetime.now()
            )
    
    async def _check_performance_improvement(self, metrics: TrainingMetrics):
        """Check if training improved performance"""
        try:
            if not self._training_history:
                return
            
            # Get previous metrics
            previous_metrics = None
            for record in reversed(self._training_history[:-1]):  # Exclude current record
                if 'metrics' in record:
                    previous_metrics = record['metrics']
                    break
            
            if not previous_metrics:
                return
            
            # Compare metrics
            improvements = []
            if metrics.accuracy > previous_metrics.accuracy:
                improvements.append(f"Accuracy improved: {previous_metrics.accuracy:.3f} → {metrics.accuracy:.3f}")
            
            if metrics.precision > previous_metrics.precision:
                improvements.append(f"Precision improved: {previous_metrics.precision:.3f} → {metrics.precision:.3f}")
            
            if metrics.recall > previous_metrics.recall:
                improvements.append(f"Recall improved: {previous_metrics.recall:.3f} → {metrics.recall:.3f}")
            
            if metrics.f1_score > previous_metrics.f1_score:
                improvements.append(f"F1-score improved: {previous_metrics.f1_score:.3f} → {metrics.f1_score:.3f}")
            
            if improvements:
                logger.info(f"🎉 Performance improvements detected: {', '.join(improvements)}")
            else:
                logger.warning("⚠️ No performance improvements detected")
                
        except Exception as e:
            logger.error(f"Error checking performance improvement: {str(e)}")
    
    async def _get_recent_performance_metrics(self) -> Dict[str, float]:
        """Get recent performance metrics"""
        try:
            if not self._training_history:
                return {}
            
            # Get metrics from recent training records
            recent_records = [r for r in self._training_history if 'metrics' in r][-5:]
            
            if not recent_records:
                return {}
            
            # Calculate average metrics
            metrics = {
                'accuracy': np.mean([r['metrics'].accuracy for r in recent_records]),
                'precision': np.mean([r['metrics'].precision for r in recent_records]),
                'recall': np.mean([r['metrics'].recall for r in recent_records]),
                'f1_score': np.mean([r['metrics'].f1_score for r in recent_records])
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting recent performance metrics: {str(e)}")
            return {}
    
    async def get_training_scheduler_status(self) -> Dict[str, Any]:
        """Get training scheduler status"""
        try:
            status = {
                'status': 'running' if self._running else 'stopped',
                'last_training': {},
                'training_history': {
                    'total_records': len(self._training_history),
                    'recent_training': len([r for r in self._training_history if datetime.fromisoformat(r['timestamp']) > datetime.now() - timedelta(days=7)])
                },
                'performance_thresholds': self._performance_thresholds,
                'training_intervals': {k: str(v) for k, v in self._training_intervals.items()},
                'recent_metrics': await self._get_recent_performance_metrics()
            }
            
            # Add last training times
            for trigger, last_time in self._last_training.items():
                if last_time:
                    status['last_training'][trigger] = last_time.isoformat()
                else:
                    status['last_training'][trigger] = None
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting training scheduler status: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def manual_training_trigger(self, trigger_type: str = "manual") -> Dict[str, Any]:
        """Manually trigger training"""
        try:
            logger.info(f"🔧 Manual training trigger: {trigger_type}")
            
            training_result = await self._ml_service.train_enhanced_models(force_retrain=True)
            
            if training_result.get('status') == 'success':
                # Record manual training
                self._training_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'triggers': [trigger_type],
                    'priority': 'manual',
                    'training_samples': training_result.get('training_samples', 0)
                })
                
                self._last_training[TrainingTrigger.MANUAL.value] = datetime.now()
                
                return {
                    'status': 'success',
                    'message': 'Manual training completed successfully',
                    'training_samples': training_result.get('training_samples', 0)
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Manual training failed: {training_result.get("error", "Unknown error")}'
                }
                
        except Exception as e:
            logger.error(f"Error in manual training trigger: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def update_performance_thresholds(self, new_thresholds: Dict[str, float]):
        """Update performance thresholds"""
        try:
            self._performance_thresholds.update(new_thresholds)
            logger.info(f"Updated performance thresholds: {new_thresholds}")
            
        except Exception as e:
            logger.error(f"Error updating performance thresholds: {str(e)}")
    
    async def update_training_intervals(self, new_intervals: Dict[str, timedelta]):
        """Update training intervals"""
        try:
            self._training_intervals.update(new_intervals)
            logger.info(f"Updated training intervals: {new_intervals}")
            
        except Exception as e:
            logger.error(f"Error updating training intervals: {str(e)}")
    
    async def get_training_analytics(self) -> Dict[str, Any]:
        """Get comprehensive training analytics"""
        try:
            analytics = {
                'training_frequency': {
                    'total_training_sessions': len(self._training_history),
                    'recent_sessions': len([r for r in self._training_history if datetime.fromisoformat(r['timestamp']) > datetime.now() - timedelta(days=7)]),
                    'average_sessions_per_day': len([r for r in self._training_history if datetime.fromisoformat(r['timestamp']) > datetime.now() - timedelta(days=1)])
                },
                'trigger_analysis': {
                    'scheduled': len([r for r in self._training_history if 'scheduled' in r.get('triggers', [])]),
                    'data_available': len([r for r in self._training_history if 'data_available' in r.get('triggers', [])]),
                    'performance_degradation': len([r for r in self._training_history if 'performance_degradation' in r.get('triggers', [])]),
                    'user_feedback': len([r for r in self._training_history if 'user_feedback' in r.get('triggers', [])]),
                    'cross_ai_learning': len([r for r in self._training_history if 'cross_ai_learning' in r.get('triggers', [])]),
                    'manual': len([r for r in self._training_history if 'manual' in r.get('triggers', [])])
                },
                'performance_trends': await self._get_performance_trends(),
                'training_efficiency': await self._calculate_training_efficiency()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting training analytics: {str(e)}")
            return {'error': str(e)}
    
    async def _get_performance_trends(self) -> Dict[str, List[float]]:
        """Get performance trends over time"""
        try:
            records_with_metrics = [r for r in self._training_history if 'metrics' in r]
            
            if len(records_with_metrics) < 2:
                return {}
            
            # Sort by timestamp
            records_with_metrics.sort(key=lambda x: x['timestamp'])
            
            trends = {
                'accuracy': [r['metrics'].accuracy for r in records_with_metrics],
                'precision': [r['metrics'].precision for r in records_with_metrics],
                'recall': [r['metrics'].recall for r in records_with_metrics],
                'f1_score': [r['metrics'].f1_score for r in records_with_metrics],
                'timestamps': [r['timestamp'] for r in records_with_metrics]
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting performance trends: {str(e)}")
            return {}
    
    async def _calculate_training_efficiency(self) -> Dict[str, float]:
        """Calculate training efficiency metrics"""
        try:
            records_with_metrics = [r for r in self._training_history if 'metrics' in r]
            
            if not records_with_metrics:
                return {}
            
            # Calculate efficiency metrics
            total_training_time = sum(r['metrics'].training_time for r in records_with_metrics)
            total_samples = sum(r['metrics'].training_samples for r in records_with_metrics)
            average_accuracy = np.mean([r['metrics'].accuracy for r in records_with_metrics])
            
            efficiency = {
                'samples_per_minute': total_samples / max(1, total_training_time / 60),
                'accuracy_per_sample': average_accuracy / max(1, total_samples),
                'average_training_time': total_training_time / len(records_with_metrics),
                'efficiency_score': (average_accuracy * total_samples) / max(1, total_training_time)
            }
            
            return efficiency
            
        except Exception as e:
            logger.error(f"Error calculating training efficiency: {str(e)}")
            return {} 