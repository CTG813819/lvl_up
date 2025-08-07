"""
App Assimilation Router - Handles APK/iOS file upload and assimilation
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import structlog
import os
import tempfile
import shutil
from datetime import datetime

from ..services.app_assimilation_service import get_app_assimilation_service

logger = structlog.get_logger()
router = APIRouter(prefix="/api/app-assimilation", tags=["app-assimilation"])

@router.post("/upload-and-analyze")
async def upload_and_analyze_app(
    file: UploadFile = File(...),
    user_id: str = "default_user"  # In production, get from auth
) -> Dict[str, Any]:
    """Upload and analyze an APK/iOS file for assimilation"""
    logger.info(f"📤 File upload received: {file.filename}")
    
    # Validate file type
    file_extension = file.filename.lower().split('.')[-1] if file.filename else ""
    if file_extension not in ['apk', 'ipa', 'app']:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Only APK and iOS app files are supported."
        )
    
    # Determine file type
    file_type = "apk" if file_extension == "apk" else "ios"
    
    # Save uploaded file temporarily
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        logger.info(f"💾 File saved temporarily: {temp_file_path}")
        
        # Analyze the file
        app_assimilation_service = get_app_assimilation_service()
        analysis = await app_assimilation_service.analyze_uploaded_app(temp_file_path, file_type)
        
        # Assimilate the app
        assimilation_result = await app_assimilation_service.assimilate_app(analysis, user_id)
        
        logger.info(f"✅ App analysis and assimilation completed: {assimilation_result['app_id']}")
        
        return {
            "status": "success",
            "message": "App uploaded, analyzed, and assimilated successfully",
            "app_id": assimilation_result["app_id"],
            "analysis": analysis,
            "assimilation": assimilation_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ File upload and analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info(f"🧹 Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.error(f"❌ Failed to clean up temporary file: {e}")

@router.get("/assimilated-apps")
async def get_assimilated_apps(user_id: str = "default_user") -> Dict[str, Any]:
    """Get all assimilated apps for a user"""
    try:
        app_assimilation_service = get_app_assimilation_service()
        apps = await app_assimilation_service.get_assimilated_apps(user_id)
        
        logger.info(f"📱 Retrieved {len(apps)} assimilated apps for user: {user_id}")
        
        return {
            "status": "success",
            "apps": apps,
            "total_count": len(apps),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get assimilated apps: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve apps: {str(e)}")

@router.get("/app-status/{app_id}")
async def get_app_status(app_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Get the current status of an assimilated app"""
    try:
        app_assimilation_service = get_app_assimilation_service()
        status = await app_assimilation_service.get_app_assimilation_status(app_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Verify user ownership
        if status.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"📊 Retrieved status for app: {app_id}")
        
        return {
            "status": "success",
            "app_status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get app status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve app status: {str(e)}")

@router.delete("/delete-app/{app_id}")
async def delete_assimilated_app(app_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Delete an assimilated app"""
    try:
        app_assimilation_service = get_app_assimilation_service()
        success = await app_assimilation_service.delete_assimilated_app(app_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="App not found or access denied")
        
        logger.info(f"🗑️ Deleted assimilated app: {app_id}")
        
        return {
            "status": "success",
            "message": "App deleted successfully",
            "app_id": app_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete app: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete app: {str(e)}")

@router.get("/integration-progress/{app_id}")
async def get_integration_progress(app_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Get the real-time integration progress of an assimilated app"""
    try:
        app_assimilation_service = get_app_assimilation_service()
        status = await app_assimilation_service.get_app_assimilation_status(app_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Verify user ownership
        if status.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        real_time_monitoring = status.get("real_time_monitoring", {})
        
        logger.info(f"📈 Retrieved integration progress for app: {app_id}")
        
        return {
            "status": "success",
            "app_id": app_id,
            "integration_progress": real_time_monitoring.get("integration_progress", 0),
            "chaos_code_applied": real_time_monitoring.get("chaos_code_applied", False),
            "synthetic_code_applied": real_time_monitoring.get("synthetic_code_applied", False),
            "chaos_integration_status": status.get("chaos_integration_status", "pending"),
            "synthetic_code_status": status.get("synthetic_code_status", "pending"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get integration progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve progress: {str(e)}")

@router.get("/chaos-integration-points/{app_id}")
async def get_chaos_integration_points(app_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Get the identified chaos integration points for an assimilated app"""
    try:
        app_assimilation_service = get_app_assimilation_service()
        status = await app_assimilation_service.get_app_assimilation_status(app_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Verify user ownership
        if status.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        original_analysis = status.get("original_analysis", {})
        integration_points = original_analysis.get("chaos_integration_points", [])
        
        logger.info(f"🎯 Retrieved {len(integration_points)} chaos integration points for app: {app_id}")
        
        return {
            "status": "success",
            "app_id": app_id,
            "integration_points": integration_points,
            "total_points": len(integration_points),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get chaos integration points: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve integration points: {str(e)}")

@router.get("/security-analysis/{app_id}")
async def get_security_analysis(app_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Get the security analysis for an assimilated app"""
    try:
        app_assimilation_service = get_app_assimilation_service()
        status = await app_assimilation_service.get_app_assimilation_status(app_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="App not found")
        
        # Verify user ownership
        if status.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        original_analysis = status.get("original_analysis", {})
        security_analysis = original_analysis.get("security_analysis", {})
        
        logger.info(f"🔒 Retrieved security analysis for app: {app_id}")
        
        return {
            "status": "success",
            "app_id": app_id,
            "security_analysis": security_analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get security analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve security analysis: {str(e)}")
