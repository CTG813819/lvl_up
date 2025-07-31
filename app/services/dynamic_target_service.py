#!/usr/bin/env python3
"""
Dynamic Target Service
Manages Docker containers for vulnerable app templates and provides real targets for AI testing.
"""

import os
import sys
import json
import random
import string
import asyncio
import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import docker
from docker.errors import DockerException, ImageNotFound, ContainerError

logger = logging.getLogger(__name__)

class DynamicTargetService:
    def __init__(self, templates_dir: str = "vuln_templates"):
        """
        Initialize the Dynamic Target Service.
        
        Args:
            templates_dir: Directory containing vulnerable app templates
        """
        self.templates_dir = Path(templates_dir)
        self.docker_client = None
        self.active_containers = {}  # container_id -> target_info
        self.template_cache = {}
        
        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise
        
        # Load available templates
        self._load_templates()
    
    def _load_templates(self):
        """Load all available templates from the templates directory."""
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory {self.templates_dir} does not exist")
            return
        
        for template_dir in self.templates_dir.iterdir():
            if template_dir.is_dir():
                config_file = template_dir / "config.json"
                if config_file.exists():
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        self.template_cache[template_dir.name] = {
                            'path': template_dir,
                            'config': config
                        }
                        logger.info(f"Loaded template: {template_dir.name}")
                    except Exception as e:
                        logger.error(f"Failed to load template {template_dir.name}: {e}")
    
    def get_available_templates(self, difficulty: str = None, category: str = None) -> List[Dict]:
        """Get available templates filtered by difficulty and category."""
        templates = []
        
        for name, template_info in self.template_cache.items():
            config = template_info['config']
            
            if difficulty and config.get('difficulty') != difficulty:
                continue
            
            if category and config.get('category') != category:
                continue
            
            templates.append({
                'name': name,
                'config': config,
                'path': str(template_info['path'])
            })
        
        return templates
    
    def select_template(self, difficulty: str, ai_strengths: List[str] = None, 
                       ai_weaknesses: List[str] = None) -> Optional[Dict]:
        """
        Select the best template based on difficulty and AI capabilities.
        
        Args:
            difficulty: Target difficulty level
            ai_strengths: List of AI's strong areas
            ai_weaknesses: List of AI's weak areas
        
        Returns:
            Selected template info or None
        """
        available = self.get_available_templates(difficulty=difficulty)
        
        if not available:
            logger.warning(f"No templates available for difficulty: {difficulty}")
            return None
        
        # If AI has weaknesses, prioritize templates that target those weaknesses
        if ai_weaknesses:
            for weakness in ai_weaknesses:
                for template in available:
                    if weakness.lower() in [v.lower() for v in template['config'].get('vulnerabilities', [])]:
                        logger.info(f"Selected template {template['name']} targeting AI weakness: {weakness}")
                        return template
        
        # Otherwise, select randomly from available templates
        selected = random.choice(available)
        logger.info(f"Randomly selected template: {selected['name']}")
        return selected
    
    def mutate_template(self, template_path: str, difficulty: str) -> str:
        """
        Apply mutations to a template to make it more dynamic and challenging.
        
        Args:
            template_path: Path to the template
            difficulty: Difficulty level for mutation intensity
        
        Returns:
            Path to the mutated template
        """
        template_dir = Path(template_path)
        mutate_script = template_dir / "mutate.py"
        
        if not mutate_script.exists():
            logger.info(f"No mutation script found for {template_path}, using as-is")
            return template_path
        
        try:
            # Create a temporary copy for mutation
            temp_dir = Path(tempfile.mkdtemp())
            shutil.copytree(template_dir, temp_dir, dirs_exist_ok=True)
            
            # Run mutation script
            result = subprocess.run(
                [sys.executable, str(temp_dir / "mutate.py"), str(temp_dir)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully mutated template: {template_path}")
                return str(temp_dir)
            else:
                logger.warning(f"Mutation failed for {template_path}: {result.stderr}")
                return template_path
                
        except Exception as e:
            logger.error(f"Error during template mutation: {e}")
            return template_path
    
    async def provision_target(self, difficulty: str, ai_strengths: List[str] = None,
                             ai_weaknesses: List[str] = None) -> Dict[str, Any]:
        """
        Provision a real Docker target for testing.
        
        Args:
            difficulty: Target difficulty level
            ai_strengths: List of AI's strong areas
            ai_weaknesses: List of AI's weak areas
        
        Returns:
            Target information including URL, credentials, container_id, etc.
        """
        try:
            # Select appropriate template
            template = self.select_template(difficulty, ai_strengths, ai_weaknesses)
            if not template:
                raise Exception(f"No suitable template found for difficulty: {difficulty}")
            
            # Apply mutations if enabled
            template_path = template['path']
            if template['config'].get('mutation_options', {}).get('randomization', False):
                template_path = self.mutate_template(template_path, difficulty)
            
            # Generate unique container name
            container_name = f"vuln_target_{template['name']}_{self._generate_id()}"
            
            # Find available port
            port = self._find_available_port()
            
            # Build and run container
            container_id = await self._build_and_run_container(
                template_path, container_name, port
            )
            
            # Wait for container to be ready
            await self._wait_for_container_ready(container_id, port)
            
            # Get target information
            target_info = {
                'container_id': container_id,
                'container_name': container_name,
                'target_url': f"http://localhost:{port}",
                'port': port,
                'template_name': template['name'],
                'difficulty': difficulty,
                'vulnerabilities': template['config'].get('vulnerabilities', []),
                'credentials': template['config'].get('credentials', {}),
                'hints': template['config'].get('hints', []),
                'success_criteria': template['config'].get('success_criteria', {}),
                'provisioned_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=2)).isoformat()
            }
            
            # Store active container info
            self.active_containers[container_id] = target_info
            
            logger.info(f"Successfully provisioned target: {target_info['target_url']}")
            return target_info
            
        except Exception as e:
            logger.error(f"Failed to provision target: {e}")
            raise
    
    def _generate_id(self, length: int = 8) -> str:
        """Generate a random ID for container naming."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def _find_available_port(self, start_port: int = 8080) -> int:
        """Find an available port starting from start_port."""
        port = start_port
        max_attempts = 100
        
        for _ in range(max_attempts):
            try:
                # Check if port is in use by active containers
                used_ports = {info['port'] for info in self.active_containers.values()}
                
                # Also check if port is actually available on the system
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if port not in used_ports and result != 0:  # Port is available
                    return port
                port += 1
            except Exception:
                port += 1
        
        raise Exception("No available ports found")
    
    async def _build_and_run_container(self, template_path: str, container_name: str, port: int) -> str:
        """Build and run a Docker container from template."""
        try:
            # Build the image
            image_name = f"vuln_target_{self._generate_id()}"
            image, logs = self.docker_client.images.build(
                path=template_path,
                tag=image_name,
                rm=True
            )
            
            # Run the container
            container = self.docker_client.containers.run(
                image_name,
                name=container_name,
                ports={"8080/tcp": port},
                detach=True,
                remove=True,
                environment={
                    "FLASK_ENV": "development",
                    "FLASK_DEBUG": "1"
                }
            )
            
            logger.info(f"Container {container_name} started with ID: {container.id}")
            return container.id
            
        except Exception as e:
            logger.error(f"Failed to build/run container: {e}")
            raise
    
    async def _wait_for_container_ready(self, container_id: str, port: int, timeout: int = 60) -> bool:
        """Wait for container to be ready and responding."""
        import aiohttp
        import time
        
        start_time = time.time()
        url = f"http://localhost:{port}"
        
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            logger.info(f"Container {container_id} is ready")
                            return True
            except Exception:
                pass
            
            await asyncio.sleep(2)
        
        raise Exception(f"Container {container_id} failed to become ready within {timeout} seconds")
    
    async def cleanup_target(self, container_id: str) -> bool:
        """
        Clean up a target container.
        
        Args:
            container_id: ID of the container to clean up
        
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            if container_id in self.active_containers:
                del self.active_containers[container_id]
            
            container = self.docker_client.containers.get(container_id)
            container.stop(timeout=10)
            container.remove()
            
            logger.info(f"Successfully cleaned up container: {container_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup container {container_id}: {e}")
            return False
    
    async def cleanup_expired_targets(self) -> int:
        """Clean up expired targets."""
        now = datetime.now()
        expired_containers = []
        
        for container_id, target_info in self.active_containers.items():
            expires_at = datetime.fromisoformat(target_info['expires_at'])
            if now > expires_at:
                expired_containers.append(container_id)
        
        cleaned_count = 0
        for container_id in expired_containers:
            if await self.cleanup_target(container_id):
                cleaned_count += 1
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired targets")
        
        return cleaned_count
    
    def get_target_info(self, container_id: str) -> Optional[Dict]:
        """Get information about a specific target."""
        return self.active_containers.get(container_id)
    
    def list_active_targets(self) -> List[Dict]:
        """List all active targets."""
        return list(self.active_containers.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the service."""
        try:
            # Check Docker connectivity
            self.docker_client.ping()
            docker_healthy = True
        except Exception as e:
            logger.error(f"Docker health check failed: {e}")
            docker_healthy = False
        
        # Check active containers
        active_count = len(self.active_containers)
        
        # Clean up expired targets
        cleaned_count = await self.cleanup_expired_targets()
        
        return {
            'docker_healthy': docker_healthy,
            'active_targets': active_count,
            'templates_loaded': len(self.template_cache),
            'expired_targets_cleaned': cleaned_count,
            'service_healthy': docker_healthy
        } 