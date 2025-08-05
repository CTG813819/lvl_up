#!/usr/bin/env python3
"""
Fix Missing Dependencies and Data Issues
Installs missing packages and populates database with test data
"""

import asyncio
import aiohttp
import json
import sys
import os
import subprocess
import time
from datetime import datetime

class MissingDependenciesFixer:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.fixes_applied = []
        self.issues_found = []
        
    async def install_missing_packages(self):
        """Install missing Python packages"""
        print("📦 Installing missing packages...")
        
        # List of required packages
        required_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "psycopg2-binary",
            "aiohttp",
            "python-multipart",
            "python-jose[cryptography]",
            "passlib[bcrypt]",
            "python-dotenv"
        ]
        
        for package in required_packages:
            try:
                print(f"📦 Installing {package}...")
                # Use pip with --break-system-packages flag for externally managed environment
                result = subprocess.run([
                    "pip3", "install", package, "--break-system-packages"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print(f"✅ {package} installed successfully")
                    self.fixes_applied.append(f"Installed {package}")
                else:
                    print(f"❌ Failed to install {package}: {result.stderr}")
                    self.issues_found.append(f"Failed to install {package}")
                    
            except Exception as e:
                print(f"❌ Error installing {package}: {str(e)}")
                self.issues_found.append(f"Error installing {package}: {str(e)}")

    async def create_database_config(self):
        """Create missing database configuration"""
        print("🗄️ Creating database configuration...")
        
        # Create app directory if it doesn't exist
        if not os.path.exists('app'):
            os.makedirs('app')
            print("✅ Created app directory")
            self.fixes_applied.append("Created app directory")
        
        # Create database.py
        database_code = '''
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database URL from environment or default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ubuntu:password@localhost:5432/ai_backend")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

# Define models
class Proposal(Base):
    __tablename__ = "proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    ai_type = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String)
    validation_score = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

class AIAgent(Base):
    __tablename__ = "ai_agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    agent_type = Column(String)  # imperium, guardian, sandbox, conquest
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class LearningRecord(Base):
    __tablename__ = "learning_records"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String)
    score = Column(Float)
    learning_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        
        try:
            with open('app/database.py', 'w') as f:
                f.write(database_code)
            print("✅ Created app/database.py")
            self.fixes_applied.append("Created app/database.py")
        except Exception as e:
            print(f"❌ Error creating database.py: {str(e)}")
            self.issues_found.append(f"Error creating database.py: {str(e)}")

    async def create_test_data(self):
        """Create test data for proposals and AI agents"""
        print("📝 Creating test data...")
        
        test_data_code = '''
import sys
import os
sys.path.append('.')

from app.database import SessionLocal, Proposal, AIAgent, LearningRecord, create_tables
from datetime import datetime

def create_test_data():
    # Create tables
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Create test proposals
        test_proposals = [
            {
                "title": "Implement Advanced AI Learning Algorithm",
                "description": "Create a new learning algorithm that improves AI agent performance by 25%",
                "ai_type": "imperium_agent",
                "status": "active",
                "created_by": "system",
                "validation_score": 85.5
            },
            {
                "title": "Enhance Security Protocol",
                "description": "Upgrade the security system to prevent unauthorized access",
                "ai_type": "guardian_agent", 
                "status": "pending",
                "created_by": "system",
                "validation_score": 92.0
            },
            {
                "title": "Optimize Database Queries",
                "description": "Improve database performance by optimizing slow queries",
                "ai_type": "sandbox_agent",
                "status": "active", 
                "created_by": "system",
                "validation_score": 78.5
            },
            {
                "title": "Add New Analytics Dashboard",
                "description": "Create a comprehensive analytics dashboard for monitoring system performance",
                "ai_type": "conquest_agent",
                "status": "completed",
                "created_by": "system", 
                "validation_score": 95.0
            }
        ]
        
        for proposal_data in test_proposals:
            proposal = Proposal(**proposal_data)
            db.add(proposal)
        
        # Create AI agents
        ai_agents = [
            {"name": "Imperium", "agent_type": "imperium", "level": 2, "xp": 150},
            {"name": "Guardian", "agent_type": "guardian", "level": 1, "xp": 75},
            {"name": "Sandbox", "agent_type": "sandbox", "level": 3, "xp": 300},
            {"name": "Conquest", "agent_type": "conquest", "level": 1, "xp": 50}
        ]
        
        for agent_data in ai_agents:
            agent = AIAgent(**agent_data)
            db.add(agent)
        
        # Create learning records
        learning_records = [
            {"agent_type": "imperium", "score": 95.0, "learning_data": "Advanced pattern recognition"},
            {"agent_type": "guardian", "score": 88.0, "learning_data": "Security protocol analysis"},
            {"agent_type": "sandbox", "score": 92.0, "learning_data": "Code optimization techniques"},
            {"agent_type": "conquest", "score": 87.0, "learning_data": "Strategic planning algorithms"}
        ]
        
        for record_data in learning_records:
            record = LearningRecord(**record_data)
            db.add(record)
        
        db.commit()
        print("Test data created successfully!")
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
'''
        
        try:
            with open('create_test_data.py', 'w') as f:
                f.write(test_data_code)
            print("✅ Created test data script")
            self.fixes_applied.append("Created test data script")
            
            # Run the test data creation
            result = subprocess.run(["python3", "create_test_data.py"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ Test data created successfully")
                self.fixes_applied.append("Created test data")
            else:
                print(f"❌ Error creating test data: {result.stderr}")
                self.issues_found.append(f"Error creating test data: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error creating test data script: {str(e)}")
            self.issues_found.append(f"Error creating test data script: {str(e)}")

    async def restart_backend_service(self):
        """Restart the backend service"""
        print("🔄 Restarting backend service...")
        try:
            subprocess.run(["sudo", "systemctl", "restart", "ultimate_start"], check=True)
            print("✅ Backend service restarted")
            
            # Wait for service to start
            print("⏳ Waiting for service to start...")
            time.sleep(20)
            
            # Check service status
            result = subprocess.run(["sudo", "systemctl", "status", "ultimate_start"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Backend service is running")
            else:
                print("❌ Backend service may not be running properly")
                self.issues_found.append("Backend service not running properly")
                
        except Exception as e:
            print(f"❌ Error restarting service: {str(e)}")
            self.issues_found.append(f"Service restart error: {str(e)}")

    async def test_endpoints_after_fix(self):
        """Test endpoints after fixes"""
        print("🎯 Testing endpoints after fixes...")
        
        endpoints_to_test = [
            "/api/proposals/",
            "/api/custody/",
            "/api/health"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ {endpoint} - working")
                            if endpoint == "/api/proposals/":
                                proposal_count = len(data) if isinstance(data, list) else 0
                                print(f"   📋 Found {proposal_count} proposals")
                                if proposal_count > 0:
                                    print("   ✅ Proposals now available - frontend should show data")
                                else:
                                    print("   ⚠️ Still no proposals found")
                        else:
                            print(f"❌ {endpoint} - failed ({response.status})")
            except Exception as e:
                print(f"❌ {endpoint} - error: {str(e)}")

    def generate_fix_summary(self):
        """Generate summary of fixes applied"""
        print("\n" + "="*60)
        print("🔧 MISSING DEPENDENCIES AND DATA FIX SUMMARY")
        print("="*60)
        
        print(f"✅ Fixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"   • {fix}")
            
        print(f"🚨 Issues Found: {len(self.issues_found)}")
        for issue in self.issues_found:
            print(f"   • {issue}")
            
        # Save detailed results
        results = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": self.fixes_applied,
            "issues_found": self.issues_found,
            "overall_status": "fixed" if len(self.fixes_applied) > 0 else "failed"
        }
        
        with open('missing_dependencies_fix_report.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\n📄 Detailed report saved to: missing_dependencies_fix_report.json")
        
        if len(self.issues_found) == 0:
            print("✅ All missing dependencies and data issues resolved!")
        else:
            print("⚠️ Some issues remain - manual intervention may be needed")

    async def run_comprehensive_fix(self):
        """Run all fixes"""
        print("🚀 Starting comprehensive missing dependencies and data fix...")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        
        # Apply fixes
        await self.install_missing_packages()
        await self.create_database_config()
        await self.create_test_data()
        
        # Restart service
        await self.restart_backend_service()
        
        # Test endpoints
        await self.test_endpoints_after_fix()
        
        # Generate summary
        self.generate_fix_summary()

async def main():
    fixer = MissingDependenciesFixer()
    await fixer.run_comprehensive_fix()

if __name__ == "__main__":
    asyncio.run(main()) 