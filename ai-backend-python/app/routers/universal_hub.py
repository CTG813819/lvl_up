from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import asyncio
import json
from datetime import datetime

from app.core.database import get_db
from app.services.universal_warmaster_deployment import UniversalWarmasterDeployment

router = APIRouter(prefix="/api/project-warmaster/universal-hub", tags=["Universal Hub"])

# Global deployment instance
deployment_system = UniversalWarmasterDeployment()

@router.get("/status")
async def get_hub_status(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get universal hub status"""
    try:
        hub_status = await deployment_system.create_universal_hub()
        return {
            "status": "success",
            "hub_status": hub_status,
            "total_devices": len(deployment_system.chaos_code_hub),
            "active_connections": len(deployment_system.active_connections),
            "cpu_usage": 0.0,  # Will be calculated from assimilated devices
            "memory_usage": 0.0,  # Will be calculated from assimilated devices
            "network_traffic": 0.0,  # Will be calculated from assimilated devices
            "devices": list(deployment_system.chaos_code_hub.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting hub status: {str(e)}")

@router.post("/scan-network")
async def scan_network(
    scan_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Scan network for devices"""
    try:
        scan_range = scan_data.get('scan_range', '192.168.1.0/24')
        scan_ports = scan_data.get('scan_ports', [22, 23, 80, 443, 8080, 8000])
        
        # Simulate network scanning
        devices_found = []
        
        # Scan the network range
        network_prefix = scan_range.split('/')[0].rsplit('.', 1)[0]
        
        for i in range(1, 255):
            target_ip = f"{network_prefix}.{i}"
            
            # Check if device is reachable
            try:
                # Quick port scan
                open_ports = await deployment_system._scan_ports(target_ip, scan_ports)
                
                if open_ports:
                    device_info = await deployment_system._probe_device(target_ip, open_ports)
                    if device_info:
                        devices_found.append(device_info)
                        
            except Exception as e:
                print(f"Error scanning {target_ip}: {e}")
                continue
        
        return {
            "status": "success",
            "devices_found": len(devices_found),
            "devices": devices_found,
            "scan_range": scan_range,
            "scan_ports": scan_ports
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scanning network: {str(e)}")

@router.post("/deploy")
async def deploy_to_device(
    deployment_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Deploy Project Warmaster to a device"""
    try:
        device_info = {
            "type": deployment_data.get("device_type", "unknown"),
            "ip": deployment_data.get("device_ip"),
            "credentials": deployment_data.get("credentials", {})
        }
        
        result = await deployment_system.deploy_to_device(device_info)
        
        return {
            "status": "success",
            "deployment_result": result,
            "device_info": device_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deploying to device: {str(e)}")

@router.post("/brute-force")
async def brute_force_device(
    brute_force_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Brute force attempt on target device"""
    try:
        target_ip = brute_force_data.get("target_ip")
        device_type = brute_force_data.get("device_type", "unknown")
        
        if not target_ip:
            raise HTTPException(status_code=400, detail="Target IP is required")
        
        result = await deployment_system.brute_force_device(target_ip, device_type)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error brute forcing device: {str(e)}")

@router.get("/devices")
async def get_assimilated_devices(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get list of assimilated devices"""
    try:
        devices = list(deployment_system.chaos_code_hub.values())
        
        return {
            "status": "success",
            "devices": devices,
            "total_devices": len(devices)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting devices: {str(e)}")

@router.post("/exploit-capabilities")
async def exploit_device_capabilities(
    exploit_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Exploit specific device capabilities"""
    try:
        device_ip = exploit_data.get("device_ip")
        capability_type = exploit_data.get("capability_type", "all")
        
        if not device_ip:
            raise HTTPException(status_code=400, detail="Device IP is required")
        
        # Get device from hub
        device = deployment_system.chaos_code_hub.get(device_ip)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found in hub")
        
        capabilities = device.get("capabilities", {})
        
        # Simulate capability exploitation
        exploitation_results = {
            "device_ip": device_ip,
            "capability_type": capability_type,
            "exploited_capabilities": [],
            "results": {}
        }
        
        if capability_type == "all" or capability_type == "cameras":
            if capabilities.get("cameras"):
                exploitation_results["exploited_capabilities"].append("cameras")
                exploitation_results["results"]["cameras"] = "Camera access gained"
        
        if capability_type == "all" or capability_type == "sensors":
            if capabilities.get("sensors"):
                exploitation_results["exploited_capabilities"].append("sensors")
                exploitation_results["results"]["sensors"] = "Sensor data accessed"
        
        if capability_type == "all" or capability_type == "storage":
            if capabilities.get("storage"):
                exploitation_results["exploited_capabilities"].append("storage")
                exploitation_results["results"]["storage"] = "Storage space utilized"
        
        if capability_type == "all" or capability_type == "network":
            if capabilities.get("network"):
                exploitation_results["exploited_capabilities"].append("network")
                exploitation_results["results"]["network"] = "Network access established"
        
        return {
            "status": "success",
            "exploitation_results": exploitation_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exploiting capabilities: {str(e)}")

@router.post("/assimilate-device")
async def assimilate_device(
    assimilation_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Attempt to assimilate a device into the hub"""
    try:
        device_ip = assimilation_data.get("device_ip")
        device_type = assimilation_data.get("device_type", "unknown")
        credentials = assimilation_data.get("credentials", {})
        
        if not device_ip:
            raise HTTPException(status_code=400, detail="Device IP is required")
        
        # Create device info
        device_info = {
            "ip": device_ip,
            "type": device_type,
            "credentials": credentials
        }
        
        # Attempt assimilation
        result = await deployment_system._attempt_assimilation(device_info)
        
        if result:
            # Register in hub
            await deployment_system._register_device_in_hub(
                device_info, 
                {},  # Empty capabilities for now
                ""   # Empty chaos code for now
            )
            
            return {
                "status": "success",
                "message": f"Device {device_ip} assimilated successfully",
                "device_info": device_info
            }
        else:
            return {
                "status": "failed",
                "message": f"Failed to assimilate device {device_ip}",
                "device_info": device_info
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assimilating device: {str(e)}")

@router.delete("/remove-device/{device_ip}")
async def remove_device(
    device_ip: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Remove device from hub"""
    try:
        if device_ip in deployment_system.chaos_code_hub:
            del deployment_system.chaos_code_hub[device_ip]
            
            return {
                "status": "success",
                "message": f"Device {device_ip} removed from hub"
            }
        else:
            raise HTTPException(status_code=404, detail="Device not found in hub")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing device: {str(e)}")

@router.get("/capabilities/{device_ip}")
async def get_device_capabilities(
    device_ip: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get device capabilities"""
    try:
        device = deployment_system.chaos_code_hub.get(device_ip)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found in hub")
        
        capabilities = device.get("capabilities", {})
        
        return {
            "status": "success",
            "device_ip": device_ip,
            "capabilities": capabilities
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting device capabilities: {str(e)}")

@router.post("/update-capabilities/{device_ip}")
async def update_device_capabilities(
    device_ip: str,
    capabilities_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Update device capabilities"""
    try:
        device = deployment_system.chaos_code_hub.get(device_ip)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found in hub")
        
        # Update capabilities
        device["capabilities"].update(capabilities_data)
        device["last_updated"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "message": f"Capabilities updated for device {device_ip}",
            "capabilities": device["capabilities"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating device capabilities: {str(e)}")

@router.get("/hub-stats")
async def get_hub_statistics(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get hub statistics"""
    try:
        total_devices = len(deployment_system.chaos_code_hub)
        active_connections = len(deployment_system.active_connections)
        
        # Calculate aggregated capabilities
        total_cameras = 0
        total_sensors = 0
        total_storage = 0
        total_network_interfaces = 0
        
        for device in deployment_system.chaos_code_hub.values():
            capabilities = device.get("capabilities", {})
            
            if capabilities.get("cameras"):
                total_cameras += len(capabilities["cameras"])
            
            if capabilities.get("sensors"):
                total_sensors += len(capabilities["sensors"])
            
            total_storage += capabilities.get("storage", 0)
            
            if capabilities.get("network"):
                total_network_interfaces += len(capabilities["network"])
        
        return {
            "status": "success",
            "statistics": {
                "total_devices": total_devices,
                "active_connections": active_connections,
                "total_cameras": total_cameras,
                "total_sensors": total_sensors,
                "total_storage_gb": total_storage,
                "total_network_interfaces": total_network_interfaces,
                "hub_created": deployment_system.chaos_code_hub.get("created", datetime.now().isoformat())
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting hub statistics: {str(e)}") 