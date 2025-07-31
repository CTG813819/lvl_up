"""
Offline Chaos Router - Handles offline functionality, rolling passwords, and Chaos Code operations
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.services.offline_chaos_service import OfflineChaosService

logger = structlog.get_logger()
router = APIRouter(prefix="/api/offline-chaos", tags=["Offline Chaos"])

# Global offline service instance
offline_service = OfflineChaosService()


class RollingPasswordRequest(BaseModel):
    current_password: Optional[str] = None
    old_password: Optional[str] = None


class VoiceCommandRequest(BaseModel):
    command: str
    user_id: str = "user_001"


class DeviceScanRequest(BaseModel):
    scan_type: str = "bluetooth"  # bluetooth, wifi, comprehensive


class DeviceAssimilationRequest(BaseModel):
    device_id: str
    device_type: str
    assimilation_method: Optional[str] = None


class ChaosCodeRequest(BaseModel):
    code_type: str = "comprehensive"  # comprehensive, neural_evolution, device_assimilation, chaos_security, voice_interface


class LegionDirectiveRequest(BaseModel):
    legion_name: str
    directive: Dict[str, Any]


@router.get("/status")
async def get_offline_status(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get comprehensive offline system status"""
    try:
        status = offline_service.get_offline_status()
        return {
            "status": "success",
            "message": "Offline Chaos system is active",
            "data": status
        }
    except Exception as e:
        logger.error(f"Error getting offline status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get offline status: {str(e)}")


@router.post("/rolling-password/generate")
async def generate_rolling_password(
    request: RollingPasswordRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Generate a new rolling password"""
    try:
        password_data = offline_service.generate_rolling_password(request.current_password)
        return {
            "status": "success",
            "message": "Rolling password generated",
            "data": password_data
        }
    except Exception as e:
        logger.error(f"Error generating rolling password: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate rolling password: {str(e)}")


@router.post("/rolling-password/verify")
async def verify_rolling_password(
    request: RollingPasswordRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Verify rolling password with support for old password authentication"""
    try:
        if not request.current_password:
            raise HTTPException(status_code=400, detail="Password is required")
        
        verification_result = offline_service.verify_rolling_password(
            request.current_password, 
            request.old_password
        )
        
        return {
            "status": "success",
            "message": verification_result["message"],
            "data": verification_result
        }
    except Exception as e:
        logger.error(f"Error verifying rolling password: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to verify rolling password: {str(e)}")


@router.post("/voice-command")
async def process_voice_command(
    request: VoiceCommandRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Process voice commands in offline mode"""
    try:
        result = offline_service.process_voice_command(request.command, request.user_id)
        return {
            "status": "success",
            "message": "Voice command processed",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error processing voice command: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process voice command: {str(e)}")


@router.post("/scan-devices")
async def scan_devices_offline(
    request: DeviceScanRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Scan for devices using offline capabilities"""
    try:
        scan_result = offline_service.scan_devices_offline(request.scan_type)
        return {
            "status": "success",
            "message": f"Device scan completed - found {scan_result['devices_found']} devices",
            "data": scan_result
        }
    except Exception as e:
        logger.error(f"Error scanning devices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to scan devices: {str(e)}")


@router.post("/assimilate-device")
async def assimilate_device_offline(
    request: DeviceAssimilationRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Attempt to assimilate a device using Chaos Code"""
    try:
        device_info = {
            "device_id": request.device_id,
            "device_type": request.device_type,
            "assimilation_method": request.assimilation_method
        }
        
        assimilation_result = offline_service.assimilate_device(device_info)
        return {
            "status": "success",
            "message": f"Device assimilation {assimilation_result['assimilation_status'].lower()}",
            "data": assimilation_result
        }
    except Exception as e:
        logger.error(f"Error assimilating device: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to assimilate device: {str(e)}")


@router.post("/generate-chaos-code")
async def generate_chaos_code_offline(
    request: ChaosCodeRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Generate Chaos Code for offline operation"""
    try:
        chaos_code = offline_service.generate_chaos_code(request.code_type)
        return {
            "status": "success",
            "message": "Chaos Code generated successfully",
            "data": chaos_code
        }
    except Exception as e:
        logger.error(f"Error generating Chaos Code: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate Chaos Code: {str(e)}")


@router.post("/legion-directive/create")
async def create_legion_directive(
    request: LegionDirectiveRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Create a Legion directive for Chaos Code deployment"""
    try:
        directive = offline_service.create_legion_directive(request.legion_name, request.directive)
        return {
            "status": "success",
            "message": f"Legion directive '{request.legion_name}' created successfully",
            "data": directive
        }
    except Exception as e:
        logger.error(f"Error creating Legion directive: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create Legion directive: {str(e)}")


@router.post("/legion-directive/execute/{directive_id}")
async def execute_legion_directive(
    directive_id: str,
    target_system: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Execute a Legion directive on a target system"""
    try:
        execution_result = offline_service.execute_legion_directive(directive_id, target_system)
        
        if not execution_result["success"]:
            return {
                "status": "error",
                "message": execution_result["error"],
                "data": execution_result
            }
        
        return {
            "status": "success",
            "message": f"Legion directive executed on {target_system}",
            "data": execution_result
        }
    except Exception as e:
        logger.error(f"Error executing Legion directive: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute Legion directive: {str(e)}")


@router.get("/legion-directives")
async def get_legion_directives(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get all Legion directives"""
    try:
        directives = offline_service.chaos_code_registry["legion_directives"]
        return {
            "status": "success",
            "message": f"Retrieved {len(directives)} Legion directives",
            "data": {
                "directives": directives,
                "total_count": len(directives)
            }
        }
    except Exception as e:
        logger.error(f"Error getting Legion directives: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Legion directives: {str(e)}")


@router.get("/chaos-code/components")
async def get_chaos_code_components(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get all Chaos Code components"""
    try:
        components = offline_service.chaos_code_registry["core_components"]
        return {
            "status": "success",
            "message": "Chaos Code components retrieved",
            "data": {
                "components": components,
                "total_components": len(components),
                "version": offline_service.chaos_code_version
            }
        }
    except Exception as e:
        logger.error(f"Error getting Chaos Code components: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Chaos Code components: {str(e)}")


@router.get("/assimilated-devices")
async def get_assimilated_devices(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get all assimilated devices"""
    try:
        devices = offline_service.device_assimilation_cache
        return {
            "status": "success",
            "message": f"Retrieved {len(devices)} assimilated devices",
            "data": {
                "devices": devices,
                "total_count": len(devices)
            }
        }
    except Exception as e:
        logger.error(f"Error getting assimilated devices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get assimilated devices: {str(e)}")


@router.get("/voice-commands")
async def get_voice_commands(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get processed voice commands"""
    try:
        commands = offline_service.voice_command_cache
        return {
            "status": "success",
            "message": f"Retrieved {len(commands)} voice commands",
            "data": {
                "commands": commands,
                "total_count": len(commands)
            }
        }
    except Exception as e:
        logger.error(f"Error getting voice commands: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get voice commands: {str(e)}")


@router.post("/sync-with-online")
async def sync_with_online_system(
    online_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Sync offline data with online system when connection is restored"""
    try:
        sync_results = offline_service.sync_with_online_system(online_data)
        return {
            "status": "success",
            "message": "Offline data synced with online system",
            "data": sync_results
        }
    except Exception as e:
        logger.error(f"Error syncing with online system: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to sync with online system: {str(e)}")


@router.post("/stealth-assimilation")
async def stealth_assimilation_offline(
    user_id: str = "user_001",
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Perform stealth assimilation of devices in the area"""
    try:
        # Scan for devices
        scan_result = offline_service.scan_devices_offline("bluetooth")
        assimilated_devices = []
        
        # Attempt assimilation on each device
        for device in scan_result["devices"]:
            if device.get("assimilation_ready", False):
                assimilation_result = offline_service.assimilate_device(device)
                if assimilation_result["assimilation_status"] == "SUCCESSFUL":
                    assimilated_devices.append(assimilation_result)
        
        return {
            "status": "success",
            "message": f"Stealth assimilation completed - {len(assimilated_devices)} devices assimilated",
            "data": {
                "devices_scanned": len(scan_result["devices"]),
                "devices_assimilated": len(assimilated_devices),
                "assimilated_devices": assimilated_devices,
                "stealth_mode": True,
                "trace_eliminated": True
            }
        }
    except Exception as e:
        logger.error(f"Error performing stealth assimilation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to perform stealth assimilation: {str(e)}")


@router.get("/chaos-code/dictionary")
async def get_chaos_code_dictionary(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get Chaos Code dictionary and structure"""
    try:
        dictionary = {
            "version": offline_service.chaos_code_version,
            "structure": {
                "neural_evolution": {
                    "description": "Self-evolving neural network system",
                    "keywords": ["EVOLUTION_CORE", "LEARNING_PROTOCOLS", "EVOLUTION_TRIGGERS"],
                    "capabilities": ["self_learning", "pattern_recognition", "adaptive_behavior"]
                },
                "device_assimilation": {
                    "description": "Device discovery and stealth assimilation system",
                    "keywords": ["SCANNING_PROTOCOLS", "ASSIMILATION_METHODS", "STEALTH_CAPABILITIES"],
                    "capabilities": ["bluetooth_scan", "wifi_penetration", "brute_force", "stealth_mode"]
                },
                "chaos_security": {
                    "description": "Advanced security and encryption system",
                    "keywords": ["ENCRYPTION_LAYERS", "AUTHENTICATION", "INTRUSION_DETECTION"],
                    "capabilities": ["encryption", "authentication", "intrusion_detection"]
                },
                "voice_interface": {
                    "description": "Voice command and speech processing system",
                    "keywords": ["SPEECH_PROCESSING", "VOICE_COMMANDS", "OFFLINE_CAPABILITIES"],
                    "capabilities": ["speech_recognition", "voice_commands", "offline_processing"]
                }
            },
            "deployment_ready": True,
            "cross_platform_compatibility": True,
            "trace_elimination": True
        }
        
        return {
            "status": "success",
            "message": "Chaos Code dictionary retrieved",
            "data": dictionary
        }
    except Exception as e:
        logger.error(f"Error getting Chaos Code dictionary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Chaos Code dictionary: {str(e)}")


@router.get("/capabilities")
async def get_offline_capabilities(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get offline system capabilities"""
    try:
        capabilities = {
            "neural_evolution": {
                "status": "ACTIVE",
                "description": "Self-learning and pattern recognition",
                "offline_operation": True
            },
            "device_assimilation": {
                "status": "ACTIVE",
                "description": "Bluetooth and WiFi device discovery and assimilation",
                "offline_operation": True
            },
            "chaos_security": {
                "status": "ACTIVE",
                "description": "Rolling password system and encryption",
                "offline_operation": True
            },
            "voice_interface": {
                "status": "ACTIVE",
                "description": "Voice command processing and speech recognition",
                "offline_operation": True
            },
            "chaos_code_generation": {
                "status": "ACTIVE",
                "description": "Self-evolving code generation system",
                "offline_operation": True
            },
            "legion_directives": {
                "status": "ACTIVE",
                "description": "Deployment directives for Chaos Code",
                "offline_operation": True
            }
        }
        
        return {
            "status": "success",
            "message": "Offline capabilities retrieved",
            "data": {
                "capabilities": capabilities,
                "total_capabilities": len(capabilities),
                "offline_mode": True
            }
        }
    except Exception as e:
        logger.error(f"Error getting offline capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get offline capabilities: {str(e)}") 