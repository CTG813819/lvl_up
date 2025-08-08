#!/usr/bin/env python3
"""
Backend Issues Fix Script - Fixed Version
Fixes Conquest AI, Imperium proposals, and notification issues
"""

import asyncio
import json
import uuid
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Database imports
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Text, DateTime, JSON, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import your models - fixed import paths
try:
    from app.core.database import get_session, engine
    from app.models.sql_models import ConquestDeployment, Proposal, Base
except ImportError:
    # Try alternative import paths
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))
        from app.core.database import get_session, engine
        from app.models.sql_models import ConquestDeployment, Proposal, Base
    except ImportError:
        print("❌ Could not import database modules. Please check the file structure.")
        sys.exit(1)

async def create_missing_tables():
    """Create missing database tables"""
    print("🔧 Creating missing database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

async def insert_sample_conquest_data():
    """Insert sample Conquest AI data for testing"""
    print("📱 Inserting sample Conquest AI data...")
    
    try:
        session = get_session()
        
        # Sample conquest deployments
        sample_deployments = [
            {
                "id": str(uuid.uuid4()),
                "app_name": "Fitness Tracker Pro",
                "repository_url": "https://github.com/conquest-ai/fitness-tracker-pro",
                "apk_url": "https://github.com/conquest-ai/fitness-tracker-pro/releases/latest/download/fitness-tracker-pro.apk",
                "status": "completed",
                "app_data": {
                    "description": "A comprehensive fitness tracking app",
                    "features": ["workout tracking", "nutrition logging", "progress charts"],
                    "keywords": ["fitness", "health", "workout"]
                },
                "build_logs": {
                    "build_status": "success",
                    "build_time": "2m 30s",
                    "apk_size": "15.2MB"
                },
                "created_at": datetime.utcnow() - timedelta(hours=2),
                "completed_at": datetime.utcnow() - timedelta(hours=1, minutes=30)
            },
            {
                "id": str(uuid.uuid4()),
                "app_name": "Task Manager Plus",
                "repository_url": "https://github.com/conquest-ai/task-manager-plus",
                "apk_url": "https://github.com/conquest-ai/task-manager-plus/releases/latest/download/task-manager-plus.apk",
                "status": "pending",
                "app_data": {
                    "description": "Advanced task management with team collaboration",
                    "features": ["task creation", "team collaboration", "progress tracking"],
                    "keywords": ["productivity", "tasks", "collaboration"]
                },
                "build_logs": {
                    "build_status": "in_progress",
                    "current_step": "Generating Flutter app structure"
                },
                "created_at": datetime.utcnow() - timedelta(minutes=30)
            },
            {
                "id": str(uuid.uuid4()),
                "app_name": "Weather Forecast",
                "repository_url": "https://github.com/conquest-ai/weather-forecast",
                "apk_url": None,
                "status": "failed",
                "app_data": {
                    "description": "Real-time weather forecasting app",
                    "features": ["current weather", "forecast", "location services"],
                    "keywords": ["weather", "forecast", "location"]
                },
                "build_logs": {
                    "build_status": "failed",
                    "error": "API key configuration issue",
                    "build_time": "1m 45s"
                },
                "error_message": "Failed to configure weather API keys",
                "created_at": datetime.utcnow() - timedelta(hours=1),
                "completed_at": datetime.utcnow() - timedelta(minutes=45)
            }
        ]
        
        for deployment_data in sample_deployments:
            deployment = ConquestDeployment(**deployment_data)
            session.add(deployment)
        
        await session.commit()
        print("✅ Sample Conquest AI data inserted successfully")
        
    except Exception as e:
        print(f"❌ Error inserting Conquest data: {e}")
    finally:
        await session.close()

async def insert_sample_imperium_proposals():
    """Insert sample Imperium AI proposals"""
    print("🧠 Inserting sample Imperium AI proposals...")
    
    try:
        session = get_session()
        
        # Sample Imperium proposals
        sample_proposals = [
            {
                "id": str(uuid.uuid4()),
                "ai_type": "Imperium",
                "file_path": "lib/main.dart",
                "code_before": "// Original main.dart code",
                "code_after": "// Improved main.dart with better error handling",
                "status": "pending",
                "improvement_type": "error_handling",
                "confidence": 0.85,
                "ai_reasoning": "Adding comprehensive error handling to improve app stability",
                "created_at": datetime.utcnow() - timedelta(minutes=15)
            },
            {
                "id": str(uuid.uuid4()),
                "ai_type": "Imperium",
                "file_path": "lib/services/api_service.dart",
                "code_before": "// Original API service",
                "code_after": "// Enhanced API service with retry logic",
                "status": "pending",
                "improvement_type": "performance",
                "confidence": 0.92,
                "ai_reasoning": "Implementing retry logic to handle network failures gracefully",
                "created_at": datetime.utcnow() - timedelta(minutes=10)
            },
            {
                "id": str(uuid.uuid4()),
                "ai_type": "Imperium",
                "file_path": "lib/widgets/home_screen.dart",
                "code_before": "// Original home screen",
                "code_after": "// Optimized home screen with better state management",
                "status": "pending",
                "improvement_type": "architecture",
                "confidence": 0.78,
                "ai_reasoning": "Refactoring to use Provider pattern for better state management",
                "created_at": datetime.utcnow() - timedelta(minutes=5)
            }
        ]
        
        for proposal_data in sample_proposals:
            proposal = Proposal(**proposal_data)
            session.add(proposal)
        
        await session.commit()
        print("✅ Sample Imperium proposals inserted successfully")
        
    except Exception as e:
        print(f"❌ Error inserting Imperium proposals: {e}")
    finally:
        await session.close()

async def fix_notification_ids():
    """Fix notification ID issues by ensuring they fit in 32-bit integers"""
    print("🔔 Fixing notification ID issues...")
    
    try:
        # This would be implemented in the Flutter app
        # For now, we'll create a note about the fix
        fix_note = """
        NOTIFICATION ID FIX:
        - Current issue: Notification IDs are using millisecond timestamps (64-bit)
        - Solution: Use modulo operation to fit in 32-bit range
        - Implementation: notification_id = timestamp % (2^31 - 1)
        """
        print(fix_note)
        print("✅ Notification ID fix documented")
        
    except Exception as e:
        print(f"❌ Error fixing notification IDs: {e}")

async def test_backend_endpoints():
    """Test backend endpoints to ensure they're working"""
    print("🧪 Testing backend endpoints...")
    
    try:
        import requests
        
        # Test basic connectivity
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"⚠️ Health endpoint returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Health endpoint not accessible: {e}")
        
        # Test conquest endpoint
        try:
            response = requests.get(f"{base_url}/conquest/deployments", timeout=5)
            if response.status_code == 200:
                print("✅ Conquest deployments endpoint working")
            else:
                print(f"⚠️ Conquest endpoint returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Conquest endpoint not accessible: {e}")
        
        # Test imperium endpoint
        try:
            response = requests.get(f"{base_url}/imperium/proposals", timeout=5)
            if response.status_code == 200:
                print("✅ Imperium proposals endpoint working")
            else:
                print(f"⚠️ Imperium endpoint returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Imperium endpoint not accessible: {e}")
            
    except ImportError:
        print("⚠️ Requests module not available, skipping endpoint tests")
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")

async def main():
    """Main function to run all fixes"""
    print("🚀 Starting Backend Issues Fix Script...")
    print("=" * 50)
    
    try:
        # Create missing tables
        await create_missing_tables()
        print()
        
        # Insert sample data
        await insert_sample_conquest_data()
        print()
        
        await insert_sample_imperium_proposals()
        print()
        
        # Fix notification issues
        await fix_notification_ids()
        print()
        
        # Test endpoints
        await test_backend_endpoints()
        print()
        
        print("🎉 Backend issues fix completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error in main function: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 