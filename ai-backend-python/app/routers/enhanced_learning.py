#!/usr/bin/env python3
"""
Enhanced Learning Router
========================

This router provides comprehensive ML learning endpoints for:

1. Continuous Model Training
2. Cross-AI Knowledge Transfer
3. Performance Analytics
4. Learning Insights
5. Training Scheduler Management
6. Model Performance Monitoring
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

from ..services.enhanced_ml_learning_service import EnhancedMLLearningService
from ..services.enhanced_training_scheduler import EnhancedTrainingScheduler
from ..core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/enhanced-learning", tags=["Enhanced Learning"])

# Initialize services
ml_service = None
training_scheduler = None

async def get_services():
    """Get initialized services"""
    global ml_service, training_scheduler
    
    if ml_service is None:
        ml_service = await EnhancedMLLearningService.initialize()
    
    if training_scheduler is None:
        training_scheduler = await EnhancedTrainingScheduler.initialize()
    
    return ml_service, training_scheduler

@router.post("/train-models")
async def train_enhanced_models(force_retrain: bool = False):
    """Train enhanced ML models"""
    try:
        ml_service, _ = await get_services()
        
        logger.info("🔄 Training enhanced ML models...")
        result = await ml_service.train_enhanced_models(force_retrain=force_retrain)
        
        if result.get('status') == 'success':
            return {
                'success': True,
                'message': 'Enhanced ML models trained successfully',
                'training_results': result.get('training_results', {}),
                'models_trained': result.get('models_trained', 0),
                'training_samples': result.get('training_samples', 0),
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=f"Training failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error training enhanced models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-quality")
async def predict_enhanced_quality(proposal_data: Dict[str, Any]):
    """Predict enhanced quality using ensemble models"""
    try:
        ml_service, _ = await get_services()
        
        result = await ml_service.predict_enhanced_quality(proposal_data)
        
        return {
            'success': True,
            'prediction': result,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error predicting enhanced quality: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learn-from-feedback")
async def learn_from_user_feedback(proposal_id: str, user_feedback: str, ai_type: str):
    """Learn from user feedback to improve models"""
    try:
        ml_service, _ = await get_services()
        
        result = await ml_service.learn_from_user_feedback(proposal_id, user_feedback, ai_type)
        
        if result.get('status') == 'success':
            return {
                'success': True,
                'message': 'Learning from feedback completed',
                'learning_value': result.get('learning_value', 0.0),
                'models_updated': result.get('models_updated', False),
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=f"Learning failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error learning from feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_enhanced_ml_analytics():
    """Get comprehensive ML analytics"""
    try:
        ml_service, _ = await get_services()
        
        analytics = await ml_service.get_enhanced_ml_analytics()
        
        return {
            'success': True,
            'analytics': analytics,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting enhanced ML analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_enhanced_learning_status():
    """Get enhanced learning service status"""
    try:
        ml_service, _ = await get_services()
        
        status = await ml_service.get_enhanced_learning_status()
        
        return {
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting enhanced learning status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge-transfer")
async def apply_knowledge_transfer(source_ai: str, target_ai: str, pattern_type: str = "successful"):
    """Apply knowledge transfer between AIs"""
    try:
        ml_service, _ = await get_services()
        
        result = await ml_service.apply_knowledge_transfer(source_ai, target_ai, pattern_type)
        
        if result.get('status') == 'success':
            return {
                'success': True,
                'message': 'Knowledge transfer completed successfully',
                'transferred_pattern': result.get('transferred_pattern', {}),
                'target_ai': result.get('target_ai'),
                'transfer_value': result.get('transfer_value', 0.0),
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=f"Knowledge transfer failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error applying knowledge transfer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-continuous-training")
async def start_continuous_training(background_tasks: BackgroundTasks):
    """Start continuous training scheduler"""
    try:
        _, training_scheduler = await get_services()
        
        background_tasks.add_task(training_scheduler.start_continuous_training)
        
        return {
            'success': True,
            'message': 'Continuous training scheduler started',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting continuous training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-continuous-training")
async def stop_continuous_training():
    """Stop continuous training scheduler"""
    try:
        _, training_scheduler = await get_services()
        
        await training_scheduler.stop_continuous_training()
        
        return {
            'success': True,
            'message': 'Continuous training scheduler stopped',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error stopping continuous training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/training-scheduler-status")
async def get_training_scheduler_status():
    """Get training scheduler status"""
    try:
        _, training_scheduler = await get_services()
        
        status = await training_scheduler.get_training_scheduler_status()
        
        return {
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting training scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/manual-training-trigger")
async def manual_training_trigger(trigger_type: str = "manual"):
    """Manually trigger training"""
    try:
        _, training_scheduler = await get_services()
        
        result = await training_scheduler.manual_training_trigger(trigger_type)
        
        if result.get('status') == 'success':
            return {
                'success': True,
                'message': result.get('message', 'Manual training completed'),
                'training_samples': result.get('training_samples', 0),
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=f"Manual training failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error in manual training trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/training-analytics")
async def get_training_analytics():
    """Get comprehensive training analytics"""
    try:
        _, training_scheduler = await get_services()
        
        analytics = await training_scheduler.get_training_analytics()
        
        return {
            'success': True,
            'analytics': analytics,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting training analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-performance-thresholds")
async def update_performance_thresholds(thresholds: Dict[str, float]):
    """Update performance thresholds for training triggers"""
    try:
        _, training_scheduler = await get_services()
        
        await training_scheduler.update_performance_thresholds(thresholds)
        
        return {
            'success': True,
            'message': 'Performance thresholds updated successfully',
            'thresholds': thresholds,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating performance thresholds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-training-intervals")
async def update_training_intervals(intervals: Dict[str, int]):
    """Update training intervals (in minutes)"""
    try:
        _, training_scheduler = await get_services()
        
        # Convert minutes to timedelta
        new_intervals = {}
        for trigger, minutes in intervals.items():
            new_intervals[trigger] = timedelta(minutes=minutes)
        
        await training_scheduler.update_training_intervals(new_intervals)
        
        return {
            'success': True,
            'message': 'Training intervals updated successfully',
            'intervals': intervals,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating training intervals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-performance")
async def get_model_performance():
    """Get detailed model performance metrics"""
    try:
        ml_service, _ = await get_services()
        
        analytics = await ml_service.get_enhanced_ml_analytics()
        
        # Extract model performance data
        model_performance = {
            'models_loaded': analytics.get('learning_metrics', {}).get('models_trained', 0),
            'last_training': analytics.get('learning_metrics', {}).get('last_training'),
            'performance_history': analytics.get('performance_history', {}),
            'cross_ai_knowledge': analytics.get('cross_ai_knowledge', {})
        }
        
        return {
            'success': True,
            'model_performance': model_performance,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting model performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning-insights")
async def get_learning_insights(ai_type: Optional[str] = None):
    """Get learning insights for specific AI or all AIs"""
    try:
        ml_service, _ = await get_services()
        
        analytics = await ml_service.get_enhanced_ml_analytics()
        
        if ai_type:
            # Get insights for specific AI
            cross_ai_data = analytics.get('cross_ai_knowledge', {})
            ai_insights = cross_ai_data.get(ai_type, {})
            
            insights = {
                'ai_type': ai_type,
                'successful_patterns': len(ai_insights.get('successful_patterns', [])),
                'failure_patterns': len(ai_insights.get('failure_patterns', [])),
                'learning_insights': len(ai_insights.get('learning_insights', [])),
                'knowledge_contributions': len(ai_insights.get('knowledge_contributions', []))
            }
        else:
            # Get insights for all AIs
            cross_ai_data = analytics.get('cross_ai_knowledge', {})
            insights = {}
            
            for ai_type, ai_data in cross_ai_data.items():
                insights[ai_type] = {
                    'successful_patterns': len(ai_data.get('successful_patterns', [])),
                    'failure_patterns': len(ai_data.get('failure_patterns', [])),
                    'learning_insights': len(ai_data.get('learning_insights', [])),
                    'knowledge_contributions': len(ai_data.get('knowledge_contributions', []))
                }
        
        return {
            'success': True,
            'learning_insights': insights,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting learning insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/continuous-learning-status")
async def get_continuous_learning_status():
    """Get continuous learning system status"""
    try:
        ml_service, training_scheduler = await get_services()
        
        ml_status = await ml_service.get_enhanced_learning_status()
        scheduler_status = await training_scheduler.get_training_scheduler_status()
        
        continuous_learning_status = {
            'ml_service': ml_status,
            'training_scheduler': scheduler_status,
            'overall_status': 'active' if scheduler_status.get('status') == 'running' else 'inactive',
            'last_activity': max(
                ml_status.get('last_training', ''),
                scheduler_status.get('last_training', {}).get('scheduled', ''),
                default=''
            )
        }
        
        return {
            'success': True,
            'continuous_learning_status': continuous_learning_status,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting continuous learning status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/force-retrain")
async def force_retrain_all_models():
    """Force retrain all models with current data"""
    try:
        ml_service, training_scheduler = await get_services()
        
        # Force retrain ML models
        ml_result = await ml_service.train_enhanced_models(force_retrain=True)
        
        # Trigger manual training in scheduler
        scheduler_result = await training_scheduler.manual_training_trigger("force_retrain")
        
        return {
            'success': True,
            'message': 'Force retrain completed',
            'ml_training': ml_result,
            'scheduler_training': scheduler_result,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in force retrain: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def enhanced_learning_health():
    """Health check for enhanced learning system"""
    try:
        ml_service, training_scheduler = await get_services()
        
        ml_status = await ml_service.get_enhanced_learning_status()
        scheduler_status = await training_scheduler.get_training_scheduler_status()
        
        health_status = {
            'ml_service_healthy': ml_status.get('status') == 'active',
            'training_scheduler_healthy': scheduler_status.get('status') in ['running', 'stopped'],
            'models_loaded': ml_status.get('models_loaded', 0) > 0,
            'scheduler_running': scheduler_status.get('status') == 'running',
            'last_activity': max(
                ml_status.get('last_training', ''),
                scheduler_status.get('last_training', {}).get('scheduled', ''),
                default=''
            )
        }
        
        overall_health = all([
            health_status['ml_service_healthy'],
            health_status['training_scheduler_healthy'],
            health_status['models_loaded']
        ])
        
        return {
            'success': True,
            'healthy': overall_health,
            'health_status': health_status,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return {
            'success': False,
            'healthy': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        } 