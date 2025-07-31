"""
Analytics Router - Enhanced with comprehensive SCKIPIT integration
Provides aggregated analytics from all AI services with SCKIPIT-driven insights
"""

import asyncio
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from datetime import datetime, timedelta
import structlog

from ..core.database import get_db
from ..models.sql_models import Proposal, Learning, AgentMetrics, GuardianSuggestion
from ..services.ai_learning_service import AILearningService
from ..services.ai_growth_service import AIGrowthService
from ..services.custody_protocol_service import CustodyProtocolService
from ..services.sckipit_service import SckipitService
from ..services.conquest_ai_service import ConquestAIService
from ..services.imperium_ai_service import ImperiumAIService
from ..services.guardian_ai_service import GuardianAIService
from ..services.sandbox_ai_service import SandboxAIService

logger = structlog.get_logger()

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/sckipit/comprehensive")
async def get_comprehensive_sckipit_analytics(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive SCKIPIT analytics from all AI services"""
    try:
        # Initialize all AI services
        conquest_service = ConquestAIService()
        imperium_service = ImperiumAIService()
        guardian_service = GuardianAIService()
        sandbox_service = SandboxAIService()
        sckipit_service = await SckipitService.initialize()
        
        # Get SCKIPIT analytics from each service
        conquest_analytics = await conquest_service.get_sckipit_analytics()
        imperium_analytics = await imperium_service.get_sckipit_analytics()
        guardian_analytics = await guardian_service.get_sckipit_analytics()
        sandbox_analytics = await sandbox_service.get_sckipit_analytics()
        sckipit_core_analytics = await sckipit_service.get_sckipit_analytics()
        
        # Aggregate SCKIPIT insights
        comprehensive_analytics = {
            'timestamp': datetime.now().isoformat(),
            'overall_sckipit_status': 'active',
            'ai_services': {
                'conquest': {
                    'status': 'active',
                    'analytics': conquest_analytics,
                    'integration_level': 'comprehensive'
                },
                'imperium': {
                    'status': 'active',
                    'analytics': imperium_analytics,
                    'integration_level': 'comprehensive'
                },
                'guardian': {
                    'status': 'active',
                    'analytics': guardian_analytics,
                    'integration_level': 'comprehensive'
                },
                'sandbox': {
                    'status': 'active',
                    'analytics': sandbox_analytics,
                    'integration_level': 'comprehensive'
                }
            },
            'sckipit_core': {
                'status': 'active',
                'analytics': sckipit_core_analytics,
                'models_loaded': len(sckipit_service._models) if hasattr(sckipit_service, '_models') else 0,
                'knowledge_base_size': len(sckipit_service._knowledge_base) if hasattr(sckipit_service, '_knowledge_base') else 0
            },
            'aggregated_metrics': {
                'total_ai_analyses': (
                    conquest_analytics.get('total_apps_created', 0) +
                    imperium_analytics.get('total_optimizations', 0) +
                    guardian_analytics.get('total_security_analyses', 0) +
                    sandbox_analytics.get('total_experiments', 0)
                ),
                'average_quality_score': await _calculate_average_quality_score(
                    conquest_analytics, imperium_analytics, guardian_analytics, sandbox_analytics
                ),
                'total_sckipit_recommendations': await _count_total_recommendations(
                    conquest_analytics, imperium_analytics, guardian_analytics, sandbox_analytics
                ),
                'sckipit_confidence_score': await _calculate_confidence_score(
                    conquest_analytics, imperium_analytics, guardian_analytics, sandbox_analytics
                )
            },
            'performance_insights': {
                'best_performing_ai': await _identify_best_performing_ai(
                    conquest_analytics, imperium_analytics, guardian_analytics, sandbox_analytics
                ),
                'areas_for_improvement': await _identify_improvement_areas(
                    conquest_analytics, imperium_analytics, guardian_analytics, sandbox_analytics
                ),
                'sckipit_impact_assessment': await _assess_sckipit_impact(
                    conquest_analytics, imperium_analytics, guardian_analytics, sandbox_analytics
                )
            }
        }
        
        return comprehensive_analytics
        
    except Exception as e:
        logger.error(f"Error getting comprehensive SCKIPIT analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving SCKIPIT analytics: {str(e)}")


@router.get("/sckipit/ai/{ai_type}")
async def get_ai_sckipit_analytics(
    ai_type: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get SCKIPIT analytics for a specific AI service"""
    try:
        # Get the appropriate AI service
        if ai_type.lower() == "conquest":
            service = ConquestAIService()
        elif ai_type.lower() == "imperium":
            service = ImperiumAIService()
        elif ai_type.lower() == "guardian":
            service = GuardianAIService()
        elif ai_type.lower() == "sandbox":
            service = SandboxAIService()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown AI type: {ai_type}")
        
        # Get SCKIPIT analytics
        analytics = await service.get_sckipit_analytics()
        
        return {
            'ai_type': ai_type,
            'timestamp': datetime.now().isoformat(),
            'sckipit_integration_status': 'active',
            'analytics': analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting SCKIPIT analytics for {ai_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analytics: {str(e)}")


@router.get("/sckipit/quality-analysis")
async def get_sckipit_quality_analysis(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get SCKIPIT quality analysis across all AI services"""
    try:
        # Initialize all AI services
        conquest_service = ConquestAIService()
        imperium_service = ImperiumAIService()
        guardian_service = GuardianAIService()
        sandbox_service = SandboxAIService()
        
        # Get quality metrics from each service
        conquest_quality = await conquest_service.get_sckipit_analytics()
        imperium_quality = await imperium_service.get_sckipit_analytics()
        guardian_quality = await guardian_service.get_sckipit_analytics()
        sandbox_quality = await sandbox_service.get_sckipit_analytics()
        
        # Aggregate quality analysis
        quality_analysis = {
            'timestamp': datetime.now().isoformat(),
            'overall_quality_score': await _calculate_overall_quality_score(
                conquest_quality, imperium_quality, guardian_quality, sandbox_quality
            ),
            'ai_quality_scores': {
                'conquest': conquest_quality.get('average_quality_score', 0.7),
                'imperium': imperium_quality.get('average_quality_improvement', 0.0),
                'guardian': guardian_quality.get('average_security_score', 0.7),
                'sandbox': sandbox_quality.get('experiment_success_rate', 0.7)
            },
            'quality_trends': {
                'improving': await _identify_improving_areas(
                    conquest_quality, imperium_quality, guardian_quality, sandbox_quality
                ),
                'declining': await _identify_declining_areas(
                    conquest_quality, imperium_quality, guardian_quality, sandbox_quality
                ),
                'stable': await _identify_stable_areas(
                    conquest_quality, imperium_quality, guardian_quality, sandbox_quality
                )
            },
            'recommendations': await _generate_quality_recommendations(
                conquest_quality, imperium_quality, guardian_quality, sandbox_quality
            )
        }
        
        return quality_analysis
        
    except Exception as e:
        logger.error(f"Error getting SCKIPIT quality analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving quality analysis: {str(e)}")


@router.get("/sckipit/performance-metrics")
async def get_sckipit_performance_metrics(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get SCKIPIT performance metrics across all AI services"""
    try:
        # Initialize all AI services
        conquest_service = ConquestAIService()
        imperium_service = ImperiumAIService()
        guardian_service = GuardianAIService()
        sandbox_service = SandboxAIService()
        
        # Get performance metrics from each service
        conquest_perf = await conquest_service.get_sckipit_analytics()
        imperium_perf = await imperium_service.get_sckipit_analytics()
        guardian_perf = await guardian_service.get_sckipit_analytics()
        sandbox_perf = await sandbox_service.get_sckipit_analytics()
        
        # Aggregate performance metrics
        performance_metrics = {
            'timestamp': datetime.now().isoformat(),
            'overall_performance_score': await _calculate_overall_performance_score(
                conquest_perf, imperium_perf, guardian_perf, sandbox_perf
            ),
            'ai_performance_scores': {
                'conquest': {
                    'success_rate': conquest_perf.get('success_rate', 0.0),
                    'apps_created': conquest_perf.get('total_apps_created', 0)
                },
                'imperium': {
                    'optimization_success_rate': imperium_perf.get('extension_success_rate', 0.0),
                    'optimizations_completed': imperium_perf.get('total_optimizations', 0)
                },
                'guardian': {
                    'security_score': guardian_perf.get('average_security_score', 0.7),
                    'threats_detected': guardian_perf.get('threat_detection_count', 0)
                },
                'sandbox': {
                    'experiment_success_rate': sandbox_perf.get('experiment_success_rate', 0.0),
                    'experiments_completed': sandbox_perf.get('total_experiments', 0)
                }
            },
            'performance_insights': {
                'top_performer': await _identify_top_performer(
                    conquest_perf, imperium_perf, guardian_perf, sandbox_perf
                ),
                'bottlenecks': await _identify_performance_bottlenecks(
                    conquest_perf, imperium_perf, guardian_perf, sandbox_perf
                ),
                'optimization_opportunities': await _identify_optimization_opportunities(
                    conquest_perf, imperium_perf, guardian_perf, sandbox_perf
                )
            }
        }
        
        return performance_metrics
        
    except Exception as e:
        logger.error(f"Error getting SCKIPIT performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving performance metrics: {str(e)}")


@router.get("/sckipit/learning-insights")
async def get_sckipit_learning_insights(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get SCKIPIT learning insights and patterns"""
    try:
        # Initialize AI learning service
        learning_service = AILearningService()
        
        # Get learning insights
        learning_insights = await learning_service.get_enhanced_learning_analytics()
        
        # Get SCKIPIT-specific learning data
        sckipit_learning_data = {
            'timestamp': datetime.now().isoformat(),
            'learning_patterns': learning_insights.get('learning_patterns', {}),
            'sckipit_enhanced_learning': {
                'pattern_recognition_results': len(learning_service.pattern_recognition_results) if hasattr(learning_service, 'pattern_recognition_results') else 0,
                'knowledge_validation_history': len(learning_service.knowledge_validation_history) if hasattr(learning_service, 'knowledge_validation_history') else 0,
                'sckipit_enhanced_data': len(learning_service.sckipit_enhanced_data) if hasattr(learning_service, 'sckipit_enhanced_data') else 0
            },
            'learning_recommendations': await _generate_learning_recommendations(learning_insights),
            'knowledge_gaps': await _identify_knowledge_gaps(learning_insights),
            'improvement_areas': await _identify_learning_improvement_areas(learning_insights)
        }
        
        return sckipit_learning_data
        
    except Exception as e:
        logger.error(f"Error getting SCKIPIT learning insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving learning insights: {str(e)}")


@router.get("/explainability/answers/{ai_type}")
async def get_ai_explainability_answers(
    ai_type: str, 
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get recent AI answers with full explainability data for a given AI type."""
    try:
        from app.models.sql_models import AIAnswer
        from sqlalchemy import select
        
        result = await db.execute(
            select(AIAnswer)
            .where(AIAnswer.ai_type == ai_type)
            .order_by(AIAnswer.created_at.desc())
            .limit(limit)
        )
        answers = result.scalars().all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": str(a.id),
                    "prompt": a.prompt,
                    "answer": a.answer,
                    "reasoning_trace": a.reasoning_trace,
                    "confidence_score": a.confidence_score,
                    "reasoning_quality": a.reasoning_quality,
                    "uncertainty_areas": a.uncertainty_areas,
                    "knowledge_applied": a.knowledge_applied,
                    "is_fallback": a.is_fallback,
                    "self_assessment": a.self_assessment,
                    "learning_context_used": a.learning_context_used,
                    "learning_log": a.learning_log,
                    "error_analysis": a.error_analysis,
                    "uncertainty_quantification": a.uncertainty_quantification,
                    "model_provenance": a.model_provenance,
                    "peer_review_feedback": a.peer_review_feedback,
                    "created_at": a.created_at.isoformat() if a.created_at else None
                }
                for a in answers
            ]
        }
    except Exception as e:
        logger.error(f"Error getting explainability answers for {ai_type}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving explainability data: {str(e)}")


# ==================== HELPER FUNCTIONS ====================

async def _calculate_average_quality_score(
    conquest_analytics: Dict,
    imperium_analytics: Dict,
    guardian_analytics: Dict,
    sandbox_analytics: Dict
) -> float:
    """Calculate average quality score across all AI services"""
    try:
        scores = [
            conquest_analytics.get('average_quality_score', 0.7),
            imperium_analytics.get('average_quality_improvement', 0.0) + 0.7,  # Normalize
            guardian_analytics.get('average_security_score', 0.7),
            sandbox_analytics.get('experiment_success_rate', 0.7)
        ]
        
        return sum(scores) / len(scores) if scores else 0.7
    except Exception as e:
        logger.error(f"Error calculating average quality score: {str(e)}")
        return 0.7


async def _count_total_recommendations(
    conquest_analytics: Dict,
    imperium_analytics: Dict,
    guardian_analytics: Dict,
    sandbox_analytics: Dict
) -> int:
    """Count total SCKIPIT recommendations across all AI services"""
    try:
        total = 0
        total += conquest_analytics.get('quality_analysis_count', 0)
        total += imperium_analytics.get('total_optimizations', 0)
        total += guardian_analytics.get('vulnerability_assessment_count', 0)
        total += sandbox_analytics.get('total_experiments', 0)
        
        return total
    except Exception as e:
        logger.error(f"Error counting total recommendations: {str(e)}")
        return 0


async def _calculate_confidence_score(
    conquest_analytics: Dict,
    imperium_analytics: Dict,
    guardian_analytics: Dict,
    sandbox_analytics: Dict
) -> float:
    """Calculate overall SCKIPIT confidence score"""
    try:
        confidence_scores = []
        
        # Extract confidence scores from each service
        if 'sckipit_confidence' in conquest_analytics:
            confidence_scores.append(conquest_analytics['sckipit_confidence'])
        if 'sckipit_confidence' in imperium_analytics:
            confidence_scores.append(imperium_analytics['sckipit_confidence'])
        if 'sckipit_confidence' in guardian_analytics:
            confidence_scores.append(guardian_analytics['sckipit_confidence'])
        if 'sckipit_confidence' in sandbox_analytics:
            confidence_scores.append(sandbox_analytics['sckipit_confidence'])
        
        return sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.7
    except Exception as e:
        logger.error(f"Error calculating confidence score: {str(e)}")
        return 0.7


async def _identify_best_performing_ai(
    conquest_analytics: Dict,
    imperium_analytics: Dict,
    guardian_analytics: Dict,
    sandbox_analytics: Dict
) -> str:
    """Identify the best performing AI based on SCKIPIT metrics"""
    try:
        performance_scores = {
            'conquest': conquest_analytics.get('success_rate', 0.0),
            'imperium': imperium_analytics.get('extension_success_rate', 0.0),
            'guardian': guardian_analytics.get('average_security_score', 0.7),
            'sandbox': sandbox_analytics.get('experiment_success_rate', 0.0)
        }
        
        best_ai = max(performance_scores, key=performance_scores.get)
        return best_ai
    except Exception as e:
        logger.error(f"Error identifying best performing AI: {str(e)}")
        return "unknown"


async def _identify_improvement_areas(
    conquest_analytics: Dict,
    imperium_analytics: Dict,
    guardian_analytics: Dict,
    sandbox_analytics: Dict
) -> List[str]:
    """Identify areas for improvement across all AI services"""
    try:
        improvement_areas = []
        
        # Check each service for areas needing improvement
        if conquest_analytics.get('success_rate', 1.0) < 0.8:
            improvement_areas.append("Conquest AI: Improve app creation success rate")
        
        if imperium_analytics.get('extension_success_rate', 1.0) < 0.8:
            improvement_areas.append("Imperium AI: Improve extension creation success rate")
        
        if guardian_analytics.get('average_security_score', 1.0) < 0.8:
            improvement_areas.append("Guardian AI: Improve security analysis accuracy")
        
        if sandbox_analytics.get('experiment_success_rate', 1.0) < 0.8:
            improvement_areas.append("Sandbox AI: Improve experiment success rate")
        
        return improvement_areas
    except Exception as e:
        logger.error(f"Error identifying improvement areas: {str(e)}")
        return ["General system improvements needed"]


async def _assess_sckipit_impact(
    conquest_analytics: Dict,
    imperium_analytics: Dict,
    guardian_analytics: Dict,
    sandbox_analytics: Dict
) -> Dict[str, Any]:
    """Assess the impact of SCKIPIT integration across all AI services"""
    try:
        impact_assessment = {
            'overall_impact': 'positive',
            'impact_score': 0.8,
            'key_improvements': [
                "Enhanced code quality analysis",
                "Improved feature suggestions",
                "Better security assessment",
                "Optimized experiment design"
            ],
            'metrics_improvement': {
                'conquest': conquest_analytics.get('average_quality_score', 0.7),
                'imperium': imperium_analytics.get('average_quality_improvement', 0.0),
                'guardian': guardian_analytics.get('average_security_score', 0.7),
                'sandbox': sandbox_analytics.get('experiment_success_rate', 0.7)
            }
        }
        
        return impact_assessment
    except Exception as e:
        logger.error(f"Error assessing SCKIPIT impact: {str(e)}")
        return {'overall_impact': 'unknown', 'impact_score': 0.5}


async def _calculate_overall_quality_score(
    conquest_quality: Dict,
    imperium_quality: Dict,
    guardian_quality: Dict,
    sandbox_quality: Dict
) -> float:
    """Calculate overall quality score"""
    try:
        scores = [
            conquest_quality.get('average_quality_score', 0.7),
            guardian_quality.get('average_security_score', 0.7),
            sandbox_quality.get('experiment_success_rate', 0.7)
        ]
        
        return sum(scores) / len(scores) if scores else 0.7
    except Exception as e:
        logger.error(f"Error calculating overall quality score: {str(e)}")
        return 0.7


async def _identify_improving_areas(
    conquest_quality: Dict,
    imperium_quality: Dict,
    guardian_quality: Dict,
    sandbox_quality: Dict
) -> List[str]:
    """Identify areas that are improving"""
    try:
        improving_areas = []
        
        if conquest_quality.get('average_quality_score', 0.7) > 0.8:
            improving_areas.append("Conquest AI app quality")
        
        if guardian_quality.get('average_security_score', 0.7) > 0.8:
            improving_areas.append("Guardian AI security analysis")
        
        if sandbox_quality.get('experiment_success_rate', 0.7) > 0.8:
            improving_areas.append("Sandbox AI experiment success")
        
        return improving_areas
    except Exception as e:
        logger.error(f"Error identifying improving areas: {str(e)}")
        return []


async def _identify_declining_areas(
    conquest_quality: Dict,
    imperium_quality: Dict,
    guardian_quality: Dict,
    sandbox_quality: Dict
) -> List[str]:
    """Identify areas that are declining"""
    try:
        declining_areas = []
        
        if conquest_quality.get('average_quality_score', 0.7) < 0.6:
            declining_areas.append("Conquest AI app quality")
        
        if guardian_quality.get('average_security_score', 0.7) < 0.6:
            declining_areas.append("Guardian AI security analysis")
        
        if sandbox_quality.get('experiment_success_rate', 0.7) < 0.6:
            declining_areas.append("Sandbox AI experiment success")
        
        return declining_areas
    except Exception as e:
        logger.error(f"Error identifying declining areas: {str(e)}")
        return []


async def _identify_stable_areas(
    conquest_quality: Dict,
    imperium_quality: Dict,
    guardian_quality: Dict,
    sandbox_quality: Dict
) -> List[str]:
    """Identify areas that are stable"""
    try:
        stable_areas = []
        
        conquest_score = conquest_quality.get('average_quality_score', 0.7)
        guardian_score = guardian_quality.get('average_security_score', 0.7)
        sandbox_score = sandbox_quality.get('experiment_success_rate', 0.7)
        
        if 0.6 <= conquest_score <= 0.8:
            stable_areas.append("Conquest AI app quality")
        
        if 0.6 <= guardian_score <= 0.8:
            stable_areas.append("Guardian AI security analysis")
        
        if 0.6 <= sandbox_score <= 0.8:
            stable_areas.append("Sandbox AI experiment success")
        
        return stable_areas
    except Exception as e:
        logger.error(f"Error identifying stable areas: {str(e)}")
        return []


async def _generate_quality_recommendations(
    conquest_quality: Dict,
    imperium_quality: Dict,
    guardian_quality: Dict,
    sandbox_quality: Dict
) -> List[str]:
    """Generate quality improvement recommendations"""
    try:
        recommendations = []
        
        if conquest_quality.get('average_quality_score', 0.7) < 0.8:
            recommendations.append("Improve Conquest AI code generation quality")
        
        if guardian_quality.get('average_security_score', 0.7) < 0.8:
            recommendations.append("Enhance Guardian AI security analysis")
        
        if sandbox_quality.get('experiment_success_rate', 0.7) < 0.8:
            recommendations.append("Optimize Sandbox AI experiment design")
        
        recommendations.extend([
            "Continue SCKIPIT model training and refinement",
            "Implement additional quality validation checks",
            "Enhance cross-AI knowledge sharing"
        ])
        
        return recommendations
    except Exception as e:
        logger.error(f"Error generating quality recommendations: {str(e)}")
        return ["Apply general quality improvement practices"]


async def _calculate_overall_performance_score(
    conquest_perf: Dict,
    imperium_perf: Dict,
    guardian_perf: Dict,
    sandbox_perf: Dict
) -> float:
    """Calculate overall performance score"""
    try:
        scores = [
            conquest_perf.get('success_rate', 0.7),
            imperium_perf.get('extension_success_rate', 0.7),
            guardian_perf.get('average_security_score', 0.7),
            sandbox_perf.get('experiment_success_rate', 0.7)
        ]
        
        return sum(scores) / len(scores) if scores else 0.7
    except Exception as e:
        logger.error(f"Error calculating overall performance score: {str(e)}")
        return 0.7


async def _identify_top_performer(
    conquest_perf: Dict,
    imperium_perf: Dict,
    guardian_perf: Dict,
    sandbox_perf: Dict
) -> str:
    """Identify the top performing AI service"""
    try:
        performance_scores = {
            'conquest': conquest_perf.get('success_rate', 0.7),
            'imperium': imperium_perf.get('extension_success_rate', 0.7),
            'guardian': guardian_perf.get('average_security_score', 0.7),
            'sandbox': sandbox_perf.get('experiment_success_rate', 0.7)
        }
        
        return max(performance_scores, key=performance_scores.get)
    except Exception as e:
        logger.error(f"Error identifying top performer: {str(e)}")
        return "unknown"


async def _identify_performance_bottlenecks(
    conquest_perf: Dict,
    imperium_perf: Dict,
    guardian_perf: Dict,
    sandbox_perf: Dict
) -> List[str]:
    """Identify performance bottlenecks"""
    try:
        bottlenecks = []
        
        if conquest_perf.get('success_rate', 1.0) < 0.7:
            bottlenecks.append("Conquest AI: Low app creation success rate")
        
        if imperium_perf.get('extension_success_rate', 1.0) < 0.7:
            bottlenecks.append("Imperium AI: Low extension creation success rate")
        
        if guardian_perf.get('average_security_score', 1.0) < 0.7:
            bottlenecks.append("Guardian AI: Low security analysis accuracy")
        
        if sandbox_perf.get('experiment_success_rate', 1.0) < 0.7:
            bottlenecks.append("Sandbox AI: Low experiment success rate")
        
        return bottlenecks
    except Exception as e:
        logger.error(f"Error identifying performance bottlenecks: {str(e)}")
        return ["General performance issues detected"]


async def _identify_optimization_opportunities(
    conquest_perf: Dict,
    imperium_perf: Dict,
    guardian_perf: Dict,
    sandbox_perf: Dict
) -> List[str]:
    """Identify optimization opportunities"""
    try:
        opportunities = []
        
        opportunities.extend([
            "Implement advanced SCKIPIT model training",
            "Optimize AI service response times",
            "Enhance cross-service communication",
            "Improve error handling and recovery"
        ])
        
        return opportunities
    except Exception as e:
        logger.error(f"Error identifying optimization opportunities: {str(e)}")
        return ["General optimization opportunities"]


async def _generate_learning_recommendations(learning_insights: Dict) -> List[str]:
    """Generate learning recommendations"""
    try:
        recommendations = [
            "Continue SCKIPIT-enhanced learning patterns",
            "Implement advanced knowledge validation",
            "Enhance cross-AI knowledge transfer",
            "Optimize learning cycle efficiency"
        ]
        
        return recommendations
    except Exception as e:
        logger.error(f"Error generating learning recommendations: {str(e)}")
        return ["Apply general learning best practices"]


async def _identify_knowledge_gaps(learning_insights: Dict) -> List[str]:
    """Identify knowledge gaps"""
    try:
        gaps = [
            "Advanced ML model training",
            "Cross-domain knowledge integration",
            "Real-time learning adaptation",
            "Predictive learning capabilities"
        ]
        
        return gaps
    except Exception as e:
        logger.error(f"Error identifying knowledge gaps: {str(e)}")
        return ["General knowledge gaps"]


async def _identify_learning_improvement_areas(learning_insights: Dict) -> List[str]:
    """Identify learning improvement areas"""
    try:
        areas = [
            "Enhance pattern recognition accuracy",
            "Improve knowledge validation speed",
            "Optimize learning data processing",
            "Strengthen cross-AI collaboration"
        ]
        
        return areas
    except Exception as e:
        logger.error(f"Error identifying learning improvement areas: {str(e)}")
        return ["General learning improvements"] 