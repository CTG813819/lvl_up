"""
Enhanced Project Horus Router with Quantum Chaos Integration
Provides endpoints for quantum chaos generation, system testing, and learning from failures
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

from app.services.project_horus_service import project_horus_service

logger = structlog.get_logger()
router = APIRouter(prefix="/api/project-horus", tags=["Project Horus Enhanced"])

# Pydantic models
class QuantumChaosRequest(BaseModel):
    target_system: Optional[str] = None
    system_type: Optional[str] = None

class SystemTestRequest(BaseModel):
    target_systems: Optional[List[str]] = None
    test_mode: Optional[str] = "comprehensive"  # comprehensive, quick, targeted

class StealthAssimilationRequest(BaseModel):
    target_system: str
    quantum_chaos_id: str
    stealth_level: Optional[float] = 1.0

class LearningAnalysisRequest(BaseModel):
    failed_system: str
    error_details: str
    attack_context: Optional[Dict[str, Any]] = None

class SystemTestResponse(BaseModel):
    total_systems: int
    successful_attacks: int
    failed_attacks: int
    learning_opportunities: int
    systems_tested: List[Dict[str, Any]]
    failed_systems: List[Dict[str, Any]]
    quantum_evolution: Dict[str, Any]

class QuantumEvolutionResponse(BaseModel):
    quantum_complexity: float
    learning_progress: float
    total_evolutions: int
    failed_learning_opportunities: int
    successful_assimilations: int
    evolution_timeline: List[Dict[str, Any]]

@router.post("/quantum-chaos/generate")
async def generate_quantum_chaos_code(request: QuantumChaosRequest):
    """Generate quantum-based chaos code for target system"""
    try:
        result = await project_horus_service.generate_quantum_chaos_code(
            target_system=request.target_system
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return {
            "status": "success",
            "message": "Quantum chaos code generated successfully",
            "chaos_code": result,
            "timestamp": datetime.now().isoformat(),
            "quantum_complexity": project_horus_service.quantum_complexity
        }
    except Exception as e:
        logger.error(f"Failed to generate quantum chaos code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quantum-chaos/stealth-assimilate")
async def stealth_assimilate_system(request: StealthAssimilationRequest):
    """Perform stealth assimilation using quantum chaos code"""
    try:
        result = await project_horus_service.stealth_assimilate_system(
            target_system=request.target_system,
            quantum_chaos_id=request.quantum_chaos_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return {
            "status": "success",
            "message": "Stealth assimilation completed successfully",
            "assimilation_result": result,
            "timestamp": datetime.now().isoformat(),
            "target_system": request.target_system
        }
    except Exception as e:
        logger.error(f"Failed to perform stealth assimilation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system-test", response_model=SystemTestResponse)
async def test_against_systems(request: SystemTestRequest):
    """Test quantum chaos code against various systems and learn from failures"""
    try:
        result = await project_horus_service.test_against_systems(
            target_systems=request.target_systems
        )
        
        return SystemTestResponse(**result)
    except Exception as e:
        logger.error(f"Failed to test against systems: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/learning/analyze-failure")
async def analyze_failure_and_learn(request: LearningAnalysisRequest):
    """Analyze failed attack and learn to improve quantum chaos code"""
    try:
        # Store failure for learning
        project_horus_service.failed_attacks[request.failed_system] = {
            "system": request.failed_system,
            "error": request.error_details,
            "attack_context": request.attack_context,
            "timestamp": datetime.now().isoformat(),
            "quantum_complexity": project_horus_service.quantum_complexity
        }
        
        # Learn from failure
        await project_horus_service._learn_from_failure(
            request.failed_system, 
            request.error_details
        )
        
        return {
            "status": "success",
            "message": "Failure analyzed and learning applied",
            "failed_system": request.failed_system,
            "learning_progress": project_horus_service.learning_progress,
            "quantum_complexity": project_horus_service.quantum_complexity,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to analyze failure: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-test/results")
async def get_system_test_results():
    """Get comprehensive system test results and learning progress"""
    try:
        result = await project_horus_service.get_system_test_results()
        return result
    except Exception as e:
        logger.error(f"Failed to get system test results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quantum-evolution/status", response_model=QuantumEvolutionResponse)
async def get_quantum_evolution_status():
    """Get quantum evolution and learning status"""
    try:
        result = await project_horus_service.get_quantum_evolution_status()
        return QuantumEvolutionResponse(**result)
    except Exception as e:
        logger.error(f"Failed to get quantum evolution status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assimilated-systems")
async def get_assimilated_systems():
    """Get list of successfully assimilated systems"""
    try:
        return {
            "assimilated_systems": list(project_horus_service.assimilated_systems.keys()),
            "total_count": len(project_horus_service.assimilated_systems),
            "systems_details": project_horus_service.assimilated_systems
        }
    except Exception as e:
        logger.error(f"Failed to get assimilated systems: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/failed-attacks")
async def get_failed_attacks():
    """Get list of failed attacks for learning analysis"""
    try:
        return {
            "failed_attacks": list(project_horus_service.failed_attacks.keys()),
            "total_count": len(project_horus_service.failed_attacks),
            "failures_details": project_horus_service.failed_attacks
        }
    except Exception as e:
        logger.error(f"Failed to get failed attacks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chaos-repositories")
async def get_chaos_repositories():
    """Get generated chaos code repositories"""
    try:
        return {
            "chaos_repositories": project_horus_service.chaos_repositories,
            "total_count": len(project_horus_service.chaos_repositories),
            "latest_repositories": project_horus_service.chaos_repositories[-10:] if project_horus_service.chaos_repositories else []
        }
    except Exception as e:
        logger.error(f"Failed to get chaos repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/docker-test-environment/create")
async def create_docker_test_environment(system: str):
    """Create Docker test environment for system testing"""
    try:
        test_env = await project_horus_service._create_docker_test_environment(system)
        return {
            "status": "success",
            "message": f"Docker test environment created for {system}",
            "test_environment": test_env
        }
    except Exception as e:
        logger.error(f"Failed to create Docker test environment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-environments")
async def get_test_environments():
    """Get all created test environments"""
    try:
        return {
            "test_environments": project_horus_service.test_environments,
            "total_count": len(project_horus_service.test_environments)
        }
    except Exception as e:
        logger.error(f"Failed to get test environments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quantum-chaos/evolve")
async def evolve_quantum_chaos_from_failures():
    """Evolve quantum chaos code based on all recorded failures"""
    try:
        evolution_results = []
        
        for system, failure in project_horus_service.failed_attacks.items():
            try:
                await project_horus_service._evolve_quantum_chaos_from_failure(
                    system, failure["error"]
                )
                evolution_results.append({
                    "system": system,
                    "status": "evolved",
                    "new_quantum_complexity": project_horus_service.quantum_complexity
                })
            except Exception as e:
                evolution_results.append({
                    "system": system,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "message": "Quantum chaos evolution completed",
            "evolution_results": evolution_results,
            "final_quantum_complexity": project_horus_service.quantum_complexity,
            "learning_progress": project_horus_service.learning_progress
        }
    except Exception as e:
        logger.error(f"Failed to evolve quantum chaos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_project_horus_status():
    """Get overall Project Horus status"""
    try:
        # Use the service method that handles async properly
        status_data = await project_horus_service.get_project_horus_status()
        
        if "error" in status_data:
            raise HTTPException(status_code=500, detail=status_data["error"])
            
        return status_data
    except Exception as e:
        logger.error(f"Failed to get Project Horus status: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 