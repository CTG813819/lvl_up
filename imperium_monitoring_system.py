#!/usr/bin/env python3
"""
Enhanced Imperium AI - Master Monitoring and Self-Improvement System
Acts as the central monitoring system that fixes and improves all other AIs and the backend
"""

import asyncio
import sys
import os
import json
import time
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Add backend path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_session, init_database
from app.models.proposal import Proposal
from app.services.ai_learning_service import AILearningService
from sqlalchemy import text

class ImperiumMonitoringSystem:
    """
    Enhanced Imperium AI - Master Monitoring and Self-Improvement System
    """
    
    def __init__(self):
        self.base_url = "http://localhost:4000"
        self.session = requests.Session()
        self.session.timeout = 30
        self.monitoring_data = {}
        self.issues_detected = []
        self.improvements_made = []
        self.system_health = {}
        self.ai_agents_status = {}
        self.performance_metrics = {}
        
        # Monitoring thresholds
        self.thresholds = {
            "response_time": 5.0,  # seconds
            "cpu_usage": 80.0,     # percentage
            "memory_usage": 85.0,  # percentage
            "error_rate": 5.0,     # percentage
            "success_rate": 90.0,  # percentage
            "database_connections": 80,  # max connections
            "learning_success_rate": 85.0  # percentage
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('imperium_monitoring.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ImperiumMonitoring')
        
    async def initialize(self):
        """Initialize the monitoring system"""
        self.logger.info("🚀 Initializing Imperium Monitoring System...")
        
        # Initialize database
        await init_database()
        
        # Create monitoring tables if they don't exist
        await self.create_monitoring_tables()
        
        # Start initial system scan
        await self.perform_system_scan()
        
        self.logger.info("✅ Imperium Monitoring System initialized")
    
    async def create_monitoring_tables(self):
        """Create monitoring and improvement tracking tables"""
        session = get_session()
        
        async with session as s:
            # Create system_monitoring table
            await s.execute(text("""
                CREATE TABLE IF NOT EXISTS system_monitoring (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    timestamp TIMESTAMP DEFAULT NOW(),
                    metric_name VARCHAR(100) NOT NULL,
                    metric_value FLOAT NOT NULL,
                    threshold FLOAT NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    details JSONB
                )
            """))
            
            # Create ai_improvements table
            await s.execute(text("""
                CREATE TABLE IF NOT EXISTS ai_improvements (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    timestamp TIMESTAMP DEFAULT NOW(),
                    ai_type VARCHAR(50) NOT NULL,
                    improvement_type VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    impact_score FLOAT NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    implementation_details JSONB,
                    results JSONB
                )
            """))
            
            # Create system_issues table
            await s.execute(text("""
                CREATE TABLE IF NOT EXISTS system_issues (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    timestamp TIMESTAMP DEFAULT NOW(),
                    issue_type VARCHAR(100) NOT NULL,
                    severity VARCHAR(20) NOT NULL,
                    description TEXT NOT NULL,
                    affected_components JSONB,
                    resolution_status VARCHAR(20) DEFAULT 'open',
                    resolution_details JSONB
                )
            """))
            
            await s.commit()
    
    async def perform_system_scan(self):
        """Perform comprehensive system scan"""
        self.logger.info("🔍 Performing comprehensive system scan...")
        
        # Monitor system health
        await self.monitor_system_health()
        
        # Monitor AI agents
        await self.monitor_ai_agents()
        
        # Monitor performance
        await self.monitor_performance()
        
        # Monitor learning systems
        await self.monitor_learning_systems()
        
        # Monitor database health
        await self.monitor_database_health()
        
        # Analyze and detect issues
        await self.analyze_issues()
        
        # Generate improvements
        await self.generate_improvements()
        
        self.logger.info("✅ System scan completed")
    
    async def monitor_system_health(self):
        """Monitor overall system health"""
        self.logger.info("💻 Monitoring system health...")
        
        try:
            # Health check
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                self.system_health["status"] = health_data.get("status", "unknown")
                self.system_health["version"] = health_data.get("version", "unknown")
            else:
                self.system_health["status"] = "unhealthy"
                self.issues_detected.append({
                    "type": "system_health",
                    "severity": "critical",
                    "description": f"Health check failed: {response.status_code}"
                })
            
            # System resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.system_health.update({
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "memory_available": memory.available / (1024**3),  # GB
                "timestamp": datetime.now().isoformat()
            })
            
            # Check thresholds
            if cpu_percent > self.thresholds["cpu_usage"]:
                self.issues_detected.append({
                    "type": "high_cpu",
                    "severity": "warning",
                    "description": f"High CPU usage: {cpu_percent}%"
                })
            
            if memory.percent > self.thresholds["memory_usage"]:
                self.issues_detected.append({
                    "type": "high_memory",
                    "severity": "warning",
                    "description": f"High memory usage: {memory.percent}%"
                })
                
        except Exception as e:
            self.logger.error(f"Error monitoring system health: {e}")
            self.issues_detected.append({
                "type": "monitoring_error",
                "severity": "error",
                "description": f"System health monitoring failed: {e}"
            })
    
    async def monitor_ai_agents(self):
        """Monitor all AI agents"""
        self.logger.info("🤖 Monitoring AI agents...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/agents/status")
            if response.status_code == 200:
                agents_data = response.json()
                agents = agents_data.get("agents", {})
                
                for agent_name, agent_data in agents.items():
                    status = agent_data.get("status", "unknown")
                    last_run = agent_data.get("last_run", "unknown")
                    
                    self.ai_agents_status[agent_name] = {
                        "status": status,
                        "last_run": last_run,
                        "healthy": status == "healthy"
                    }
                    
                    # Check for issues
                    if status != "healthy":
                        self.issues_detected.append({
                            "type": "ai_agent_issue",
                            "severity": "warning",
                            "description": f"{agent_name} agent status: {status}",
                            "affected_components": [agent_name]
                        })
                    
                    # Generate improvements for each agent
                    await self.analyze_agent_improvements(agent_name, agent_data)
            else:
                self.issues_detected.append({
                    "type": "ai_agents_monitoring",
                    "severity": "error",
                    "description": f"Failed to get AI agents status: {response.status_code}"
                })
                
        except Exception as e:
            self.logger.error(f"Error monitoring AI agents: {e}")
            self.issues_detected.append({
                "type": "ai_agents_error",
                "severity": "error",
                "description": f"AI agents monitoring failed: {e}"
            })
    
    async def monitor_performance(self):
        """Monitor system performance"""
        self.logger.info("⚡ Monitoring performance...")
        
        try:
            # Test response times for key endpoints
            endpoints = [
                "/health",
                "/api/agents/status",
                "/api/learning/status",
                "/api/proposals/",
                "/api/growth/status"
            ]
            
            for endpoint in endpoints:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                response_time = end_time - start_time
                
                if endpoint not in self.performance_metrics:
                    self.performance_metrics[endpoint] = []
                
                self.performance_metrics[endpoint].append({
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Check for slow responses
                if response_time > self.thresholds["response_time"]:
                    self.issues_detected.append({
                        "type": "slow_response",
                        "severity": "warning",
                        "description": f"Slow response time for {endpoint}: {response_time:.2f}s"
                    })
                
                # Keep only last 10 measurements
                if len(self.performance_metrics[endpoint]) > 10:
                    self.performance_metrics[endpoint] = self.performance_metrics[endpoint][-10:]
                    
        except Exception as e:
            self.logger.error(f"Error monitoring performance: {e}")
    
    async def monitor_learning_systems(self):
        """Monitor learning systems"""
        self.logger.info("🧠 Monitoring learning systems...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/learning/status")
            if response.status_code == 200:
                learning_data = response.json()
                
                total_experiments = learning_data.get("total_experiments", 0)
                success_rate = learning_data.get("success_rate", 0) * 100
                
                # Check learning success rate
                if success_rate < self.thresholds["learning_success_rate"]:
                    self.issues_detected.append({
                        "type": "low_learning_success",
                        "severity": "warning",
                        "description": f"Low learning success rate: {success_rate:.1f}%"
                    })
                
                # Monitor each AI type's learning
                for ai_type in ["Imperium", "Guardian", "Sandbox", "Conquest"]:
                    await self.monitor_ai_learning(ai_type)
                    
        except Exception as e:
            self.logger.error(f"Error monitoring learning systems: {e}")
    
    async def monitor_ai_learning(self, ai_type: str):
        """Monitor specific AI learning"""
        try:
            response = self.session.get(f"{self.base_url}/api/learning/insights/{ai_type}")
            if response.status_code == 200:
                insights = response.json()
                stats = insights.get("stats", {})
                
                total_entries = stats.get("total_learning_entries", 0)
                recent_entries = stats.get("recent_learning_entries", 0)
                
                # Check if AI is actively learning
                if recent_entries == 0:
                    self.issues_detected.append({
                        "type": "inactive_learning",
                        "severity": "info",
                        "description": f"{ai_type} AI is not actively learning",
                        "affected_components": [ai_type]
                    })
                    
        except Exception as e:
            self.logger.error(f"Error monitoring {ai_type} learning: {e}")
    
    async def monitor_database_health(self):
        """Monitor database health"""
        self.logger.info("🗄️ Monitoring database health...")
        
        try:
            session = get_session()
            async with session as s:
                # Check connection pool
                pool_info = await s.execute(text("SELECT count(*) FROM pg_stat_activity"))
                active_connections = pool_info.scalar()
                
                if active_connections > self.thresholds["database_connections"]:
                    self.issues_detected.append({
                        "type": "high_db_connections",
                        "severity": "warning",
                        "description": f"High database connections: {active_connections}"
                    })
                
                # Check table sizes
                tables = ["proposals", "oath_papers", "learning_entries"]
                for table in tables:
                    try:
                        count_result = await s.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = count_result.scalar()
                        
                        if count > 10000:  # Large table threshold
                            self.issues_detected.append({
                                "type": "large_table",
                                "severity": "info",
                                "description": f"Large table {table}: {count} records"
                            })
                    except Exception as e:
                        self.logger.warning(f"Could not check table {table}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error monitoring database health: {e}")
    
    async def analyze_issues(self):
        """Analyze detected issues and prioritize them"""
        self.logger.info("🔍 Analyzing detected issues...")
        
        # Categorize issues by severity
        critical_issues = [issue for issue in self.issues_detected if issue["severity"] == "critical"]
        warning_issues = [issue for issue in self.issues_detected if issue["severity"] == "warning"]
        info_issues = [issue for issue in self.issues_detected if issue["severity"] == "info"]
        
        self.logger.info(f"Found {len(critical_issues)} critical, {len(warning_issues)} warning, {len(info_issues)} info issues")
        
        # Store issues in database
        await self.store_issues()
        
        # Auto-resolve simple issues
        await self.auto_resolve_issues()
    
    async def store_issues(self):
        """Store issues in database"""
        session = get_session()
        
        async with session as s:
            for issue in self.issues_detected:
                await s.execute(text("""
                    INSERT INTO system_issues (issue_type, severity, description, affected_components)
                    VALUES (:issue_type, :severity, :description, :affected_components)
                """), {
                    "issue_type": issue["type"],
                    "severity": issue["severity"],
                    "description": issue["description"],
                    "affected_components": json.dumps(issue.get("affected_components", []))
                })
            
            await s.commit()
    
    async def auto_resolve_issues(self):
        """Automatically resolve simple issues"""
        self.logger.info("🔧 Attempting to auto-resolve issues...")
        
        for issue in self.issues_detected:
            if issue["type"] == "inactive_learning":
                # Trigger learning for inactive AIs
                affected_components = issue.get("affected_components", [])
                for ai_type in affected_components:
                    await self.trigger_ai_learning(ai_type)
                    
            elif issue["type"] == "slow_response":
                # Optimize performance
                await self.optimize_performance()
                
            elif issue["type"] == "high_cpu" or issue["type"] == "high_memory":
                # Optimize resource usage
                await self.optimize_resources()
    
    async def trigger_ai_learning(self, ai_type: str):
        """Trigger learning for specific AI"""
        try:
            self.logger.info(f"Triggering learning for {ai_type}...")
            
            # Create a learning proposal
            learning_proposal = {
                "title": f"{ai_type} Learning Trigger",
                "description": f"Automated learning trigger for {ai_type} AI",
                "ai_type": ai_type,
                "status": "pending",
                "confidence": 0.9,
                "improvement_type": "learning_trigger"
            }
            
            # Store the proposal
            session = get_session()
            async with session as s:
                await s.execute(text("""
                    INSERT INTO proposals (title, description, ai_type, status, confidence, improvement_type, created_at, updated_at)
                    VALUES (:title, :description, :ai_type, :status, :confidence, :improvement_type, NOW(), NOW())
                """), learning_proposal)
                await s.commit()
            
            self.improvements_made.append({
                "type": "learning_trigger",
                "ai_type": ai_type,
                "description": f"Triggered learning for {ai_type}",
                "impact_score": 0.7
            })
            
        except Exception as e:
            self.logger.error(f"Error triggering learning for {ai_type}: {e}")
    
    async def optimize_performance(self):
        """Optimize system performance"""
        self.logger.info("⚡ Optimizing performance...")
        
        try:
            # Analyze slow endpoints
            for endpoint, metrics in self.performance_metrics.items():
                if metrics:
                    avg_response_time = sum(m["response_time"] for m in metrics) / len(metrics)
                    
                    if avg_response_time > self.thresholds["response_time"]:
                        # Create performance improvement proposal
                        improvement = {
                            "title": f"Performance Optimization for {endpoint}",
                            "description": f"Optimize response time for {endpoint} (current: {avg_response_time:.2f}s)",
                            "ai_type": "Imperium",
                            "status": "pending",
                            "confidence": 0.8,
                            "improvement_type": "performance_optimization"
                        }
                        
                        await self.create_improvement_proposal(improvement)
                        
        except Exception as e:
            self.logger.error(f"Error optimizing performance: {e}")
    
    async def optimize_resources(self):
        """Optimize resource usage"""
        self.logger.info("💾 Optimizing resource usage...")
        
        try:
            # Create resource optimization proposal
            improvement = {
                "title": "Resource Usage Optimization",
                "description": f"Optimize system resources (CPU: {self.system_health.get('cpu_usage', 0):.1f}%, Memory: {self.system_health.get('memory_usage', 0):.1f}%)",
                "ai_type": "Imperium",
                "status": "pending",
                "confidence": 0.85,
                "improvement_type": "resource_optimization"
            }
            
            await self.create_improvement_proposal(improvement)
            
        except Exception as e:
            self.logger.error(f"Error optimizing resources: {e}")
    
    async def generate_improvements(self):
        """Generate improvement proposals"""
        self.logger.info("🚀 Generating improvement proposals...")
        
        # Analyze each AI agent for improvements
        for agent_name, agent_data in self.ai_agents_status.items():
            await self.analyze_agent_improvements(agent_name, agent_data)
        
        # Generate system-wide improvements
        await self.generate_system_improvements()
        
        # Store improvements
        await self.store_improvements()
    
    async def analyze_agent_improvements(self, agent_name: str, agent_data: Dict):
        """Analyze improvements for specific agent"""
        try:
            # Check agent performance
            if agent_data.get("status") != "healthy":
                improvement = {
                    "title": f"{agent_name} Health Recovery",
                    "description": f"Recover {agent_name} agent to healthy status",
                    "ai_type": agent_name,
                    "status": "pending",
                    "confidence": 0.9,
                    "improvement_type": "health_recovery"
                }
                await self.create_improvement_proposal(improvement)
            
            # Check for learning opportunities
            if agent_name != "Imperium":  # Don't analyze self
                improvement = {
                    "title": f"{agent_name} Learning Enhancement",
                    "description": f"Enhance learning capabilities for {agent_name}",
                    "ai_type": agent_name,
                    "status": "pending",
                    "confidence": 0.7,
                    "improvement_type": "learning_enhancement"
                }
                await self.create_improvement_proposal(improvement)
                
        except Exception as e:
            self.logger.error(f"Error analyzing improvements for {agent_name}: {e}")
    
    async def generate_system_improvements(self):
        """Generate system-wide improvements"""
        try:
            # Database optimization
            improvement = {
                "title": "Database Query Optimization",
                "description": "Optimize database queries for better performance",
                "ai_type": "Imperium",
                "status": "pending",
                "confidence": 0.8,
                "improvement_type": "database_optimization"
            }
            await self.create_improvement_proposal(improvement)
            
            # Caching improvement
            improvement = {
                "title": "Caching Layer Enhancement",
                "description": "Enhance caching layer for faster responses",
                "ai_type": "Imperium",
                "status": "pending",
                "confidence": 0.75,
                "improvement_type": "caching_enhancement"
            }
            await self.create_improvement_proposal(improvement)
            
        except Exception as e:
            self.logger.error(f"Error generating system improvements: {e}")
    
    async def create_improvement_proposal(self, improvement: Dict):
        """Create an improvement proposal"""
        try:
            session = get_session()
            async with session as s:
                await s.execute(text("""
                    INSERT INTO proposals (title, description, ai_type, status, confidence, improvement_type, created_at, updated_at)
                    VALUES (:title, :description, :ai_type, :status, :confidence, :improvement_type, NOW(), NOW())
                """), improvement)
                await s.commit()
            
            self.improvements_made.append({
                "type": improvement["improvement_type"],
                "ai_type": improvement["ai_type"],
                "description": improvement["description"],
                "impact_score": improvement["confidence"]
            })
            
        except Exception as e:
            self.logger.error(f"Error creating improvement proposal: {e}")
    
    async def store_improvements(self):
        """Store improvements in database"""
        session = get_session()
        
        async with session as s:
            for improvement in self.improvements_made:
                await s.execute(text("""
                    INSERT INTO ai_improvements (ai_type, improvement_type, description, impact_score, status)
                    VALUES (:ai_type, :improvement_type, :description, :impact_score, :status)
                """), {
                    "ai_type": improvement["ai_type"],
                    "improvement_type": improvement["type"],
                    "description": improvement["description"],
                    "impact_score": improvement["impact_score"],
                    "status": "pending"
                })
            
            await s.commit()
    
    async def run_continuous_monitoring(self):
        """Run continuous monitoring loop"""
        self.logger.info("🔄 Starting continuous monitoring...")
        
        while True:
            try:
                # Perform system scan
                await self.perform_system_scan()
                
                # Generate monitoring report
                await self.generate_monitoring_report()
                
                # Wait for next scan (every 5 minutes)
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def generate_monitoring_report(self):
        """Generate comprehensive monitoring report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_health": self.system_health,
            "ai_agents_status": self.ai_agents_status,
            "performance_metrics": self.performance_metrics,
            "issues_detected": len(self.issues_detected),
            "improvements_made": len(self.improvements_made),
            "monitoring_status": "active"
        }
        
        # Save report
        with open("imperium_monitoring_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📊 Monitoring report generated: {len(self.issues_detected)} issues, {len(self.improvements_made)} improvements")

async def main():
    """Main function to run Imperium Monitoring System"""
    imperium = ImperiumMonitoringSystem()
    
    # Initialize the system
    await imperium.initialize()
    
    # Run continuous monitoring
    await imperium.run_continuous_monitoring()

if __name__ == "__main__":
    asyncio.run(main()) 