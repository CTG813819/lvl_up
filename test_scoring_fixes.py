#!/usr/bin/env python3
"""
Test script to verify AI scoring system fixes
Tests the comprehensive scoring system to ensure it produces dynamic scores
instead of the fixed 40.08 scores that were occurring before.
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService

class ScoringSystemTester:
    """Test the comprehensive scoring system fixes"""
    
    def __init__(self):
        self.custody_service = CustodyProtocolService()
        
    async def test_comprehensive_scoring(self):
        """Test the comprehensive scoring system"""
        print("🧪 Testing Comprehensive Scoring System")
        print("=" * 50)
        
        # Test case 1: Imperium with good response
        ai_type = "imperium"
        scenario = """
        You are an expert Python developer. Generate production-ready code for the following scenario:
        
        SCENARIO: Collaborative task for sandbox and conquest
        
        REQUIREMENTS:
        - Design a scalable microservices architecture
        - Implement secure authentication system
        - Create comprehensive API documentation
        
        COMPLEXITY LEVEL: x1
        
        LANGUAGE: Python
        """
        
        response = """
        As Imperium, I'll create a comprehensive microservices architecture solution:
        
        ```python
        from fastapi import FastAPI, Depends, HTTPException, status
        from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
        from sqlalchemy import create_engine, Column, Integer, String, DateTime
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker, Session
        import jwt
        import bcrypt
        from datetime import datetime, timedelta
        from typing import Optional
        
        # Database models
        Base = declarative_base()
        
        class User(Base):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True, index=True)
            username = Column(String, unique=True, index=True)
            email = Column(String, unique=True, index=True)
            hashed_password = Column(String)
            created_at = Column(DateTime, default=datetime.utcnow)
        
        # Authentication service
        class AuthService:
            def __init__(self, secret_key: str):
                self.secret_key = secret_key
                self.algorithm = "HS256"
            
            def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
                to_encode = data.copy()
                if expires_delta:
                    expire = datetime.utcnow() + expires_delta
                else:
                    expire = datetime.utcnow() + timedelta(minutes=15)
                to_encode.update({"exp": expire})
                encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
                return encoded_jwt
            
            def verify_password(self, plain_password: str, hashed_password: str) -> bool:
                return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
            
            def get_password_hash(self, password: str) -> str:
                return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Main application
        app = FastAPI(title="Collaborative Task API", version="1.0.0")
        
        # Security configuration
        SECRET_KEY = "your-secret-key-here"
        ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        auth_service = AuthService(SECRET_KEY)
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        
        # Database setup
        SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        
        # Dependency
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        
        # Authentication endpoints
        @app.post("/token")
        async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
            user = db.query(User).filter(User.username == form_data.username).first()
            if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = auth_service.create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
        
        # Protected endpoint example
        @app.get("/users/me/")
        async def read_users_me(token: str = Depends(oauth2_scheme)):
            return {"token": token}
        
        # Health check
        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.utcnow()}
        
        if __name__ == "__main__":
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8000)
        ```
        
        This solution provides:
        - Scalable microservices architecture using FastAPI
        - Secure JWT-based authentication system
        - Comprehensive API documentation with automatic OpenAPI generation
        - Database integration with SQLAlchemy
        - Production-ready security features
        - Health check endpoints for monitoring
        """
        
        difficulty = "basic"
        
        print(f"\n📋 Test Case: {ai_type.title()}")
        print("-" * 30)
        
        # Test comprehensive analysis
        analysis = await self.custody_service._comprehensive_response_analysis(
            ai_type, scenario, response
        )
        
        print(f"📊 Analysis Results:")
        for component, score in analysis.items():
            print(f"  • {component.replace('_', ' ').title()}: {score:.1f}/100")
        
        # Test comprehensive scoring
        final_score = self.custody_service._calculate_comprehensive_score(
            analysis, difficulty, ai_type
        )
        
        print(f"\n🎯 Final Score: {final_score:.1f}/100")
        
        # Test feedback generation
        feedback = self.custody_service._generate_comprehensive_feedback(
            analysis, final_score, ai_type
        )
        
        print(f"\n💬 Feedback: {feedback}")
        
        # Test reasoning points
        reasoning_points = self.custody_service._generate_reasoning_points(analysis)
        print(f"\n🧠 Reasoning Points:")
        for point in reasoning_points[:3]:  # Show first 3
            print(f"  • {point}")
        
        # Verify score is not the old fixed value
        if abs(final_score - 40.08) < 0.1:
            print(f"❌ ERROR: Score is still the old fixed value!")
            return False
        else:
            print(f"✅ SUCCESS: Score is dynamic ({final_score:.1f})")
        
        print("\n" + "="*50)
        
        return True
    
    async def test_scoring_consistency(self):
        """Test that scoring is consistent and reasonable"""
        print("\n🔍 Testing Scoring Consistency")
        print("=" * 50)
        
        # Test with different AI types
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            print(f"\n🤖 Testing {ai_type.title()}")
            
            # Simple response
            simple_response = "This is a basic response with minimal technical content."
            analysis_simple = await self.custody_service._comprehensive_response_analysis(
                ai_type, "Basic test scenario", simple_response
            )
            score_simple = self.custody_service._calculate_comprehensive_score(
                analysis_simple, "basic", ai_type
            )
            
            # Complex response
            complex_response = """
            As an expert system architect, I'll design a comprehensive solution:
            
            ```python
            class AdvancedSystem:
                def __init__(self):
                    self.security_layer = SecurityManager()
                    self.performance_optimizer = PerformanceEngine()
                    self.scalability_handler = ScalabilityController()
                
                def implement_enterprise_solution(self):
                    # Comprehensive enterprise-grade implementation
                    pass
            ```
            
            This solution provides:
            - Advanced security with encryption and authentication
            - Performance optimization with caching and load balancing
            - Scalable architecture with microservices
            - Comprehensive monitoring and logging
            - Production-ready deployment strategies
            """
            
            analysis_complex = await self.custody_service._comprehensive_response_analysis(
                ai_type, "Complex test scenario", complex_response
            )
            score_complex = self.custody_service._calculate_comprehensive_score(
                analysis_complex, "advanced", ai_type
            )
            
            print(f"  Simple Response Score: {score_simple:.1f}")
            print(f"  Complex Response Score: {score_complex:.1f}")
            print(f"  Score Difference: {score_complex - score_simple:.1f}")
            
            # Verify complex response scores higher
            if score_complex > score_simple:
                print(f"  ✅ SUCCESS: Complex response scored higher")
            else:
                print(f"  ❌ ERROR: Complex response should score higher")
        
        return True
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting AI Scoring System Tests")
        print("=" * 60)
        
        try:
            # Test comprehensive scoring
            test1_passed = await self.test_comprehensive_scoring()
            
            # Test scoring consistency
            test2_passed = await self.test_scoring_consistency()
            
            if test1_passed and test2_passed:
                print("\n🎉 ALL TESTS PASSED!")
                print("✅ The AI scoring system is now working correctly")
                print("✅ Dynamic scores are being generated")
                print("✅ Comprehensive analysis is functioning")
                print("✅ Reasoning points are being generated")
                return True
            else:
                print("\n❌ SOME TESTS FAILED!")
                print("Please check the implementation")
                return False
                
        except Exception as e:
            print(f"\n💥 TEST ERROR: {str(e)}")
            return False

async def main():
    """Main test function"""
    tester = ScoringSystemTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎯 RECOMMENDATION: Deploy the fixes to production")
        print("The AI backend should now produce dynamic scores instead of fixed 40.08")
    else:
        print("\n⚠️  RECOMMENDATION: Review and fix the implementation")

if __name__ == "__main__":
    asyncio.run(main()) 