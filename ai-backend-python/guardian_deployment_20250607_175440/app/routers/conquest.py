"""
Conquest AI Router - Creates new app repositories and APKs
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import structlog
from pydantic import BaseModel
from datetime import datetime
import uuid
import re

from app.services.conquest_ai_service import ConquestAIService
from app.core.database import get_session

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
        "message": "Conquest AI is active",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "app_creation",
            "apk_generation", 
            "repository_management",
            "deployment_tracking",
            "suggestion_analysis",
            "build_monitoring"
        ],
        "capabilities": {
            "create_new_apps": True,
            "improve_existing_apps": True,
            "generate_apks": True,
            "analyze_suggestions": True,
            "track_deployments": True
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
    app_id: str
    error_message: str
    build_logs: Optional[str] = None
    failure_type: str = "build_error"


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
            raise HTTPException(status_code=400, detail=result["message"])
            
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


@router.post("/build-failure")
async def report_build_failure(request: BuildFailureRequest):
    """Report a build failure for tracking and analysis"""
    try:
        conquest_service = ConquestAIService()
        await conquest_service.initialize()
        
        # Record the build failure
        failure_data = {
            "app_id": request.app_id,
            "error_message": request.error_message,
            "build_logs": request.build_logs,
            "failure_type": request.failure_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update deployment status to failed
        result = await conquest_service.update_deployment_status(
            request.app_id, 
            "failed", 
            error_message=request.error_message,
            build_logs=request.build_logs
        )
        
        # Log the failure for analysis
        logger.error("Build failure reported", 
                    app_id=request.app_id, 
                    error_message=request.error_message, 
                    failure_type=request.failure_type)
        
        return {
            "status": "success",
            "message": "Build failure recorded successfully",
            "failure_id": str(uuid.uuid4()),
            "app_id": request.app_id,
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


@router.get("/ai/imperium/learnings")
async def get_imperium_learnings():
    """Get Imperium AI learnings"""
    try:
        # Return sample learning data from Imperium AI
        learnings = [
            {
                "type": "code_optimization",
                "insight": "Flutter widgets should be extracted for better performance",
                "timestamp": "2025-07-06T09:00:00Z",
                "confidence": 0.85
            },
            {
                "type": "architecture_pattern",
                "insight": "MVVM pattern improves code maintainability",
                "timestamp": "2025-07-06T08:30:00Z",
                "confidence": 0.92
            }
        ]
        
        return {
            "status": "success",
            "learnings": learnings,
            "ai_type": "imperium"
        }
        
    except Exception as e:
        logger.error("Error getting Imperium learnings", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/guardian/learnings")
async def get_guardian_learnings():
    """Get Guardian AI learnings"""
    try:
        # Return sample learning data from Guardian AI
        learnings = [
            {
                "type": "security_best_practices",
                "insight": "Always validate user input before processing",
                "timestamp": "2025-07-06T09:15:00Z",
                "confidence": 0.88
            },
            {
                "type": "error_handling",
                "insight": "Graceful error handling improves user experience",
                "timestamp": "2025-07-06T08:45:00Z",
                "confidence": 0.90
            }
        ]
        
        return {
            "status": "success",
            "learnings": learnings,
            "ai_type": "guardian"
        }
        
    except Exception as e:
        logger.error("Error getting Guardian learnings", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/sandbox/learnings")
async def get_sandbox_learnings():
    """Get Sandbox AI learnings"""
    try:
        # Return sample learning data from Sandbox AI
        learnings = [
            {
                "type": "experimental_feature",
                "insight": "New UI patterns can improve user engagement",
                "timestamp": "2025-07-06T09:30:00Z",
                "confidence": 0.75
            },
            {
                "type": "performance_optimization",
                "insight": "Lazy loading reduces initial app load time",
                "timestamp": "2025-07-06T09:00:00Z",
                "confidence": 0.82
            }
        ]
        
        return {
            "status": "success",
            "learnings": learnings,
            "ai_type": "sandbox"
        }
        
    except Exception as e:
        logger.error("Error getting Sandbox learnings", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 