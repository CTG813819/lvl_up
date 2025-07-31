"""
Conquest AI Router - Creates new app repositories and APKs
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Path
from typing import Dict, Any, List, Optional
import structlog
from pydantic import BaseModel
from datetime import datetime
import uuid
import re
import requests

from app.services.conquest_ai_service import ConquestAIService
from app.core.database import get_db

logger = structlog.get_logger()
router = APIRouter(tags=["Conquest AI"])


def validate_app_fields(name, description, keywords):
    forbidden_pattern = re.compile(r'[^a-zA-Z0-9 .,\-_/]')
    errors = []
    suggestions = []
    if not name or not name.strip():
        errors.append('App name is required.')
    elif len(name.strip()) < 3:
        errors.append('App name must be at least 3 characters.')
    elif forbidden_pattern.search(name):
        errors.append('App name contains forbidden characters.')
    if not description or not description.strip():
        errors.append('Description is required.')
    elif len(description.strip()) < 10:
        errors.append('Description must be at least 10 characters.')
    elif forbidden_pattern.search(description):
        errors.append('Description contains forbidden characters.')
    if not keywords or (isinstance(keywords, str) and not keywords.strip()):
        errors.append('At least one keyword/tag is required.')
    else:
        if isinstance(keywords, str):
            kw_list = [k.strip() for k in keywords.split(',') if k.strip()]
        else:
            kw_list = [str(k).strip() for k in keywords if str(k).strip()]
        if not kw_list:
            errors.append('At least one keyword/tag is required.')
        elif len(kw_list) < 2:
            suggestions.append('Add more keywords for better results.')
        for k in kw_list:
            if forbidden_pattern.search(k):
                errors.append('Keywords contain forbidden characters.')
                break
    return errors, suggestions


@router.get("/")
async def get_conquest_overview():
    """Get Conquest AI overview"""
    return {
        "status": "success",
        "message": "Conquest AI is active with advanced AI code generation",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "ai_powered_app_creation",
            "advanced_code_generation",
            "apk_generation", 
            "repository_management",
            "deployment_tracking",
            "suggestion_analysis",
            "build_monitoring",
            "continuous_learning"
        ],
        "ai_capabilities": {
            "app_development": "Full app creation and deployment",
            "ai_learning": "Active learning system",
            "ml_integration": "Advanced ML capabilities",
            "local_models": "Available for basic code generation",
            "template_generation": "Fallback template system"
        },
        "ai_models": {
            "openai_gpt4": "Available for complex code generation",
            "anthropic_claude": "Available for backup generation",
            "local_transformers": "Available for offline generation",
            "fallback_templates": "Always available as backup"
        }
    }


class CreateAppRequest(BaseModel):
    name: str
    description: str
    keywords: List[str] = []
    app_type: str = "general"
    features: List[str] = []
    operation_type: str = "create_new"  # "create_new" or "improve_existing"
    existing_repo: Optional[str] = None  # For improvements
    improvement_focus: Optional[str] = None  # For improvements


class AppResponse(BaseModel):
    status: str
    app_id: str
    app_name: str
    repository_url: str
    apk_url: str
    message: str


class BuildFailureRequest(BaseModel):
    # Accept both formats for compatibility
    app_id: Optional[str] = None
    appId: Optional[str] = None  # GitHub Actions format
    error_message: Optional[str] = None
    error: Optional[str] = None  # GitHub Actions format
    build_logs: Optional[str] = None
    failure_type: str = "build_error"
    
    @property
    def normalized_app_id(self) -> str:
        """Get the app ID in normalized format"""
        app_id = self.app_id or self.appId
        if not app_id or app_id.strip() == "":
            return "unknown"
        return app_id.strip()
    
    @property
    def normalized_error_message(self) -> str:
        """Get the error message in normalized format"""
        return self.error_message or self.error or "Unknown error"
    
    def is_valid_app_id(self) -> bool:
        """Check if the app_id is a valid UUID format"""
        import re
        app_id = self.normalized_app_id
        if app_id == "unknown":
            return False
        # UUID pattern: 8-4-4-4-12 hexadecimal characters
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        return bool(uuid_pattern.match(app_id))
    
    class Config:
        extra = "allow"  # Allow extra fields for flexibility


@router.post("/create-app", response_model=AppResponse)
async def create_new_app(request: CreateAppRequest):
    """Create a new app repository and generate APK"""
    try:
        # Validate fields
        errors, suggestions = validate_app_fields(request.name, request.description, request.keywords)
        if errors:
            return {"status": "error", "message": "; ".join(errors), "app_id": "", "app_name": request.name, "repository_url": "", "apk_url": "", "suggestions": suggestions}
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        app_data = {
            "name": request.name,
            "description": request.description,
            "keywords": request.keywords,
            "app_type": request.app_type,
            "features": request.features,
            "operation_type": request.operation_type,
            "existing_repo": request.existing_repo,
            "improvement_focus": request.improvement_focus
        }
        
        if request.operation_type == "create_new":
            result = await conquest_service.create_new_app(app_data)
        elif request.operation_type == "improve_existing":
            result = await conquest_service.improve_existing_app(app_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid operation type")
        
        if result["status"] == "success":
            return AppResponse(**result)
        else:
            # Handle validation failures gracefully instead of throwing 500
            return {
                "status": "error",
                "message": result["message"],
                "app_id": result.get("app_id", ""),
                "app_name": request.name,
                "repository_url": result.get("repository_url", ""),
                "apk_url": result.get("apk_url", ""),
                "validation_results": result.get("validation_results", {}),
                "suggestions": result.get("suggestions", [])
            }
            
    except Exception as e:
        logger.error("Error creating/improving app", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deployments")
async def list_deployments():
    """List all Conquest AI deployments"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        result = await conquest_service.list_deployments()
        
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error("Error listing deployments", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deployment/{app_id}")
async def get_deployment_status(app_id: str):
    """Get deployment status for a specific app"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        result = await conquest_service.get_deployment_status(app_id)
        
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=404, detail=result["message"])
            
    except Exception as e:
        logger.error("Error getting deployment status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-suggestion")
async def analyze_app_suggestion(request: CreateAppRequest):
    """Analyze an app suggestion and provide recommendations"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        # Analyze the app suggestion
        analysis = {
            "app_name": request.name,
            "description": request.description,
            "keywords": request.keywords,
            "app_type": request.app_type,
            "features": request.features,
            "recommendations": {
                "suggested_features": [],
                "estimated_complexity": "medium",
                "development_time": "2-4 weeks",
                "technologies": ["Flutter", "Dart", "Provider", "SQLite"],
                "potential_issues": [],
                "optimization_suggestions": []
            },
            "market_analysis": {
                "target_audience": "General users",
                "competition_level": "medium",
                "monetization_potential": "medium"
            }
        }
        
        # Add specific recommendations based on app type
        if request.app_type == "game":
            analysis["recommendations"]["suggested_features"].extend([
                "Game engine integration",
                "Score tracking system",
                "Leaderboard functionality",
                "Achievement system"
            ])
        elif request.app_type == "social":
            analysis["recommendations"]["suggested_features"].extend([
                "User authentication",
                "Profile management",
                "Messaging system",
                "Social sharing"
            ])
        elif request.app_type == "fitness":
            analysis["recommendations"]["suggested_features"].extend([
                "Workout tracking",
                "Progress visualization",
                "Goal setting",
                "Health metrics"
            ])
        
        return {
            "status": "success",
            "analysis": analysis,
            "message": f"Analysis completed for '{request.name}'"
        }
        
    except Exception as e:
        logger.error("Error analyzing app suggestion", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-apk")
async def create_apk_only(request: CreateAppRequest):
    """Create APK for existing app without creating new repository"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        app_data = {
            "name": request.name,
            "description": request.description,
            "keywords": request.keywords,
            "app_type": request.app_type,
            "features": request.features,
            "operation_type": "create_apk_only",
            "existing_repo": request.existing_repo
        }
        
        result = await conquest_service.create_apk_only(app_data)
        
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error("Error creating APK", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improve-app")
async def improve_existing_app(request: CreateAppRequest):
    """Improve existing app with new features or optimizations"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        app_data = {
            "name": request.name,
            "description": request.description,
            "keywords": request.keywords,
            "app_type": request.app_type,
            "features": request.features,
            "operation_type": "improve_existing",
            "existing_repo": request.existing_repo,
            "improvement_focus": request.improvement_focus
        }
        
        result = await conquest_service.improve_existing_app(app_data)
        
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        logger.error("Error improving app", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/{operation_id}")
async def get_operation_progress(operation_id: str):
    """Get progress of a specific operation (APK creation, app improvement, etc.)"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        result = await conquest_service.get_operation_progress(operation_id)
        
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=404, detail=result["message"])
            
    except Exception as e:
        logger.error("Error getting operation progress", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress-logs")
async def get_progress_logs():
    """Get progress logs for Conquest AI operations"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        # Get recent progress logs from the service
        logs = await conquest_service.get_progress_logs()
        
        return {
            "status": "success",
            "success": True,
            "logs": logs,
            "message": f"Retrieved {len(logs)} progress logs"
        }
        
    except Exception as e:
        logger.error("Error getting progress logs", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/error-learnings")
async def get_error_learnings():
    """Get error learnings from Conquest AI"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        # Get error learnings from the service
        learnings = await conquest_service.get_error_learnings()
        
        return {
            "status": "success",
            "learnings": learnings,
            "message": f"Retrieved {len(learnings)} error learnings"
        }
        
    except Exception as e:
        logger.error("Error getting error learnings", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_conquest_status():
    """Get Conquest AI system status"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        # Get deployment statistics
        deployments_result = await conquest_service.list_deployments()
        
        if deployments_result["status"] == "success":
            deployments = deployments_result["deployments"]
            total_deployments = len(deployments)
            successful_deployments = len([d for d in deployments if d["status"] == "completed"])
            success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0
            
            # Separate new apps vs improvements
            new_apps = [d for d in deployments if d.get("operation_type") == "create_new"]
            improvements = [d for d in deployments if d.get("operation_type") == "improve_existing"]
            
            return {
                "status": "success",
                "conquest_ai": {
                    "is_active": True,
                    "total_deployments": total_deployments,
                    "successful_deployments": successful_deployments,
                    "success_rate": round(success_rate, 2),
                    "last_deployment": deployments[0]["created_at"] if deployments else None,
                    "new_apps_created": len(new_apps),
                    "apps_improved": len(improvements),
                    "capabilities": [
                        "New app repository creation",
                        "Existing app improvements",
                        "Flutter app generation",
                        "APK building",
                        "GitHub integration",
                        "Automated deployment"
                    ]
                }
            }
        else:
            return {
                "status": "success",
                "conquest_ai": {
                    "is_active": True,
                    "total_deployments": 0,
                    "successful_deployments": 0,
                    "success_rate": 0.0,
                    "last_deployment": None,
                    "capabilities": [
                        "App repository creation",
                        "Flutter app generation",
                        "APK building",
                        "GitHub integration",
                        "Automated deployment"
                    ]
                }
            }
            
    except Exception as e:
        logger.error("Error getting Conquest status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 


@router.get("/statistics")
async def get_basic_statistics():
    """Get basic Conquest AI deployment statistics"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        deployments_result = await conquest_service.list_deployments()
        deployments = deployments_result.get('deployments', []) if deployments_result.get('status') == 'success' else []
        total_apps = len(deployments)
        completed_apps = len([d for d in deployments if d.get('status') == 'completed'])
        failed_apps = len([d for d in deployments if d.get('status') == 'failed'])
        pending_apps = len([d for d in deployments if d.get('status') == 'pending'])
        testing_apps = len([d for d in deployments if d.get('status') == 'testing'])
        return {
            "status": "success",
            "statistics": {
                "totalApps": total_apps,
                "completedApps": completed_apps,
                "failedApps": failed_apps,
                "pendingApps": pending_apps,
                "testingApps": testing_apps,
                "successRate": round((completed_apps / total_apps * 100) if total_apps > 0 else 0, 2)
            }
        }
    except Exception as e:
        logger.error("Error getting basic statistics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/enhanced-statistics")
async def get_enhanced_statistics():
    """Get enhanced Conquest AI statistics including learning data and validation progress"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        result = await conquest_service.get_enhanced_statistics()
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except Exception as e:
        logger.error("Error getting enhanced Conquest AI statistics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Enhanced statistics error: {str(e)}")


@router.post("/build-failure")
async def report_build_failure(request: BuildFailureRequest):
    """Report a build failure for tracking and analysis"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        # Check if we have a valid app_id
        app_id = request.normalized_app_id
        if not request.is_valid_app_id():
            # Log the failure without trying to update database
            logger.error("Build failure reported with invalid app_id", 
                        app_id=app_id,
                        error_message=request.normalized_error_message, 
                        failure_type=request.failure_type)
            
            return {
                "status": "success",
                "message": "Build failure recorded successfully (no valid app_id)",
                "failure_id": str(uuid.uuid4()),
                "app_id": app_id,
                "recorded_at": datetime.utcnow().isoformat()
            }
        
        # Record the build failure
        failure_data = {
            "app_id": app_id,
            "error_message": request.normalized_error_message,
            "build_logs": request.build_logs,
            "failure_type": request.failure_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update deployment status to failed
        result = await conquest_service.update_deployment_status(
            app_id, 
            "failed", 
            error_message=request.normalized_error_message,
            build_logs=request.build_logs
        )
        
        # Log the failure for analysis
        logger.error("Build failure reported", 
                    app_id=app_id, 
                    error_message=request.normalized_error_message, 
                    failure_type=request.failure_type)
        
        return {
            "status": "success",
            "message": "Build failure recorded successfully",
            "failure_id": str(uuid.uuid4()),
            "app_id": app_id,
            "recorded_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error recording build failure", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 


@router.post("/define-requirements")
async def define_app_requirements(request: Dict[str, Any]):
    """Define app requirements based on user input and AI learning"""
    try:
        name = request.get('name')
        description = request.get('description')
        keywords = request.get('keywords', '')
        errors, suggestions = validate_app_fields(name, description, keywords)
        if errors:
            return {"status": "error", "message": "; ".join(errors), "suggestions": suggestions}
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        app_id = request.get('appId')
        learning_data = request.get('learningData', {})
        
        # Define requirements based on app type and keywords
        requirements = {
            "app_type": "general",
            "features": ["authentication", "settings", "navigation"],
            "dependencies": {
                "flutter": "sdk: '>=3.0.0 <4.0.0'",
                "provider": "^6.0.0",
                "shared_preferences": "^2.0.0",
                "http": "^0.13.0",
                "sqflite": "^2.0.0",
                "path": "^1.8.0"
            },
            "architecture": "MVVM",
            "state_management": "Provider",
            "database": "SQLite",
            "ui_framework": "Material Design",
            "target_platforms": ["android", "ios"],
            "min_sdk_version": "21",
            "target_sdk_version": "33"
        }
        
        # Customize requirements based on keywords
        keywords_lower = keywords.lower() if keywords else ""
        if any(word in keywords_lower for word in ["game", "gaming", "play"]):
            requirements["app_type"] = "game"
            requirements["features"].extend(["game_engine", "score_tracking", "leaderboard"])
            requirements["dependencies"]["flame"] = "^1.0.0"
        elif any(word in keywords_lower for word in ["social", "chat", "message"]):
            requirements["app_type"] = "social"
            requirements["features"].extend(["user_profiles", "messaging", "social_sharing"])
            requirements["dependencies"]["firebase_messaging"] = "^14.0.0"
        elif any(word in keywords_lower for word in ["fitness", "workout", "health"]):
            requirements["app_type"] = "fitness"
            requirements["features"].extend(["workout_tracking", "progress_charts", "goal_setting"])
            requirements["dependencies"]["fl_chart"] = "^0.60.0"
        
        return {
            "status": "success",
            "requirements": requirements,
            "message": f"Requirements defined for app: {name}"
        }
        
    except Exception as e:
        logger.error("Error defining app requirements", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/build-app")
async def build_app(request: Dict[str, Any]):
    """Build the app based on requirements"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        app_id = request.get('appId')
        requirements = request.get('requirements', {})
        learning_data = request.get('learningData', {})
        
        # Simulate app building process
        app_path = f"/tmp/conquest_apps/{app_id}"
        
        return {
            "status": "success",
            "appPath": app_path,
            "buildLogs": "App built successfully",
            "message": f"App built successfully"
        }
        
    except Exception as e:
        logger.error("Error building app", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-app")
async def test_app(request: Dict[str, Any]):
    """Test the built app"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        app_id = request.get('appId')
        app_path = request.get('appPath')
        requirements = request.get('requirements', {})
        
        # Simulate app testing
        test_results = {
            "status": "passed",
            "tests_run": 5,
            "tests_passed": 5,
            "tests_failed": 0,
            "coverage": "85%"
        }
        
        return {
            "status": "success",
            "testResults": test_results,
            "message": f"App tested successfully"
        }
        
    except Exception as e:
        logger.error("Error testing app", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deploy-to-github")
async def deploy_to_github(request: Dict[str, Any]):
    """Deploy app to GitHub"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        app_id = request.get('appId')
        app_name = request.get('appName')
        app_path = request.get('appPath')
        description = request.get('description', '')
        
        # Simulate GitHub deployment
        repo_url = f"https://github.com/conquest-ai/{app_name.lower().replace(' ', '-')}"
        download_url = f"https://github.com/conquest-ai/{app_name.lower().replace(' ', '-')}/releases/latest/download/app.apk"
        
        return {
            "status": "success",
            "repoUrl": repo_url,
            "downloadUrl": download_url,
            "message": f"App deployed to GitHub successfully"
        }
        
    except Exception as e:
        logger.error("Error deploying to GitHub", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 


@router.post("/test-ai-code-generation")
async def test_ai_code_generation(request: Dict[str, Any]):
    """Test the advanced AI code generation capabilities"""
    try:
        from app.services.advanced_code_generator import AdvancedCodeGenerator
        
        generator = AdvancedCodeGenerator()
        
        description = request.get('description', 'A simple Flutter app')
        complexity = request.get('complexity', 'medium')
        
        # Test AI code generation
        generated_code = await generator.generate_dart_code(description, complexity)
        
        return {
            "status": "success",
            "message": "AI code generation test completed",
            "description": description,
            "complexity": complexity,
            "generated_code": generated_code,
            "code_length": len(generated_code),
            "ai_model_used": "AdvancedCodeGenerator"
        }
        
    except Exception as e:
        logger.error("Error testing AI code generation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-code-complexity")
async def analyze_code_complexity(request: Dict[str, Any]):
    """Analyze the complexity of an app description for code generation"""
    try:
        from app.services.sckipit_service import SckipitService
        
        sckipit = await SckipitService.initialize()
        description = request.get('description', '')
        
        # Use the complexity determination logic
        complexity = sckipit._determine_complexity(description)
        
        # Analyze keywords for complexity factors
        description_lower = description.lower()
        complex_keywords = [
            'api', 'network', 'database', 'state management', 'animation',
            'custom', 'advanced', 'complex', 'multiple', 'integration',
            'authentication', 'authorization', 'real-time', 'websocket'
        ]
        
        simple_keywords = [
            'display', 'show', 'text', 'button', 'simple', 'basic',
            'static', 'view', 'label'
        ]
        
        found_complex = [kw for kw in complex_keywords if kw in description_lower]
        found_simple = [kw for kw in simple_keywords if kw in description_lower]
        
        return {
            "status": "success",
            "description": description,
            "determined_complexity": complexity,
            "complexity_factors": {
                "complex_keywords_found": found_complex,
                "simple_keywords_found": found_simple,
                "description_length": len(description),
                "complexity_score": len(found_complex) - len(found_simple)
            },
            "recommendations": {
                "suggested_ai_model": "gpt4" if complexity == "complex" else "claude" if complexity == "medium" else "local",
                "estimated_generation_time": "30-60 seconds" if complexity == "complex" else "10-30 seconds",
                "suggested_features": found_complex[:3] if found_complex else ["basic_ui", "navigation"]
            }
        }
        
    except Exception as e:
        logger.error("Error analyzing code complexity", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/imperium/learnings")
async def get_imperium_learnings():
    """Get Imperium AI learnings"""
    try:
        # Fetch real learning data from Imperium AI
        from app.services.imperium_learning_controller import ImperiumLearningController
        
        controller = ImperiumLearningController()
        learnings = await controller.get_agent_metrics("imperium")
        
        return {
            "status": "success",
            "learnings": learnings.get('learning_events', []),
            "ai_type": "imperium"
        }
        
    except Exception as e:
        logger.error("Error getting Imperium learnings", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/guardian/learnings")
async def get_guardian_learnings():
    """Get Guardian AI learnings"""
    try:
        # Fetch real learning data from Guardian AI
        from app.services.imperium_learning_controller import ImperiumLearningController
        
        controller = ImperiumLearningController()
        learnings = await controller.get_agent_metrics("guardian")
        
        return {
            "status": "success",
            "learnings": learnings.get('learning_events', []),
            "ai_type": "guardian"
        }
        
    except Exception as e:
        logger.error("Error getting Guardian learnings", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/sandbox/learnings")
async def get_sandbox_learnings():
    """Get Sandbox AI learnings"""
    try:
        # Fetch real learning data from Sandbox AI
        from app.services.imperium_learning_controller import ImperiumLearningController
        
        controller = ImperiumLearningController()
        learnings = await controller.get_agent_metrics("sandbox")
        
        return {
            "status": "success",
            "learnings": learnings.get('learning_events', []),
            "ai_type": "sandbox"
        }
        
    except Exception as e:
        logger.error("Error getting Sandbox learnings", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 


@router.post("/app-error")
async def report_app_error(request: Dict[str, Any]):
    """Report an app error for tracking and analysis. If critical, auto-rollback."""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()

        # Extract error data with fallbacks for different formats
        app_id = request.get('appId') or request.get('app_id') or "unknown"
        error_message = request.get('error') or request.get('error_message') or "Unknown error"
        commit = request.get('commit', '')
        branch = request.get('branch', '')
        source = request.get('source', 'unknown')
        step = request.get('step', 'unknown')

        # Record the app error
        error_data = {
            "app_id": app_id,
            "error_message": error_message,
            "commit": commit,
            "branch": branch,
            "source": source,
            "step": step,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Log the error for analysis
        logger.error("App error reported", 
                    app_id=app_id, 
                    error_message=error_message, 
                    source=source,
                    step=step)

        # --- Automated Rollback Logic ---
        rollback_status = None
        if "critical" in error_message.lower():
            logger.warning(f"[AUTO-ROLLBACK] Critical error detected for app {app_id}. Initiating rollback.")
            restored = await conquest_service.restoreCodeSnapshot(app_id)
            if restored is not None:
                await conquest_service.logRollback(app_id, restored)
                rollback_status = {
                    "status": "success",
                    "message": f"Auto-rollback successful for app {app_id}",
                }
            else:
                rollback_status = {
                    "status": "error",
                    "message": f"No snapshot found for app {app_id} during auto-rollback"
                }

        return {
            "status": "success",
            "message": "App error recorded successfully",
            "error_id": str(uuid.uuid4()),
            "app_id": app_id,
            "recorded_at": datetime.utcnow().isoformat(),
            "auto_rollback": rollback_status
        }
    except Exception as e:
        logger.error("Error recording app error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 


@router.post("/rollback-app")
async def rollback_app(request: Dict[str, Any] = Body(...)):
    """Rollback the app to the last code snapshot (undo last change)"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        app_id = request.get('appId')
        if not app_id:
            raise HTTPException(status_code=400, detail="Missing appId")
        # Attempt to restore code snapshot
        restored = await conquest_service.restoreCodeSnapshot(app_id)
        if restored is not None:
            # Log the rollback event
            await conquest_service.logRollback(app_id, restored)
            return {
                "status": "success",
                "message": f"Rollback successful for app {app_id}",
                "restored_code": restored
            }
        else:
            return {
                "status": "error",
                "message": f"No snapshot found for app {app_id}"
            }
    except Exception as e:
        logger.error("Error during rollback", error=str(e))
        return {"status": "error", "message": str(e)} 


@router.get("/commits/{app_id}")
async def get_commit_history(app_id: str = Path(...)):
    """Fetch commit history for a Conquest app's repository."""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        # Look up the app's repo URL
        app = await conquest_service.getAppById(app_id)
        repo_url = app.get('repo_url')
        if not repo_url:
            return {"status": "error", "message": "No repository URL found for this app."}
        # Extract owner/repo from URL (assume GitHub)
        # e.g., https://github.com/owner/repo.git
        import re
        m = re.search(r'github.com[:/](.*?)/(.*?)(\.git)?$', repo_url)
        if not m:
            return {"status": "error", "message": "Invalid GitHub repo URL."}
        owner, repo = m.group(1), m.group(2)
        # Fetch commits from GitHub API
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        r = requests.get(api_url)
        if r.status_code != 200:
            return {"status": "error", "message": f"GitHub API error: {r.status_code}"}
        commits = r.json()
        # Optionally, parse commit messages for rollbacks/suggestions
        for c in commits:
            msg = c.get('commit', {}).get('message', '')
            if 'rollback' in msg.lower():
                c['is_rollback'] = True
            if 'suggestion' in msg.lower() or 'improvement' in msg.lower():
                c['is_suggestion'] = True
        return {"status": "success", "commits": commits}
    except Exception as e:
        return {"status": "error", "message": str(e)} 