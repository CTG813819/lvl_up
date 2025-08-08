#!/usr/bin/env python3
"""
Test script to demonstrate the new real-world test system
that focuses on practical learning and improvement.
"""

import asyncio
import sys
import os

# Add the ai-backend-python directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

from app.services.custody_protocol_service import CustodyProtocolService, TestDifficulty, TestCategory
from app.services.agent_metrics_service import AgentMetricsService
from app.services.real_world_test_service import real_world_test_service, RealWorldTestCategory

async def test_real_world_system():
    """Test the new real-world test system"""
    
    print("🌍 Testing Real-World Test System")
    print("=" * 60)
    
    # Initialize services
    custody_service = CustodyProtocolService()
    agent_metrics_service = AgentMetricsService()
    
    # Set up guardian AI with poor performance (87 consecutive failures)
    test_metrics = {
        "total_tests_given": 87,
        "total_tests_passed": 0,
        "total_tests_failed": 87,
        "consecutive_failures": 87,
        "consecutive_successes": 0,
        "pass_rate": 0.0,
        "current_difficulty": "basic",
        "test_history": []
    }
    
    # Create test history with 87 failed tests
    for i in range(87):
        test_metrics["test_history"].append({
            "timestamp": f"2025-08-01T{i:02d}:00:00.000000",
            "passed": False,
            "score": 40.0,  # Low scores
            "duration": 0
        })
    
    # Update the metrics in the database
    await agent_metrics_service.create_or_update_agent_metrics("guardian", test_metrics)
    
    print(f"📊 Set up guardian AI with:")
    print(f"   - Total tests: {test_metrics['total_tests_given']}")
    print(f"   - Consecutive failures: {test_metrics['consecutive_failures']}")
    print(f"   - Pass rate: {test_metrics['pass_rate']:.2%}")
    print(f"   - Current difficulty: {test_metrics['current_difficulty']}")
    
    # Test 1: Generate a real-world test
    print(f"\n🧪 Test 1: Generating Real-World Test")
    print("-" * 40)
    
    # Get learning history
    learning_history = await custody_service._get_ai_learning_history("guardian")
    
    # Generate a real-world test
    real_world_test = await real_world_test_service.generate_real_world_test(
        "guardian", 
        RealWorldTestCategory.DOCKER_DEPLOYMENT, 
        "basic", 
        learning_history
    )
    
    print(f"✅ Generated real-world test:")
    print(f"   - Test ID: {real_world_test['test_id']}")
    print(f"   - Title: {real_world_test['title']}")
    print(f"   - Category: {real_world_test['category']}")
    print(f"   - Difficulty: {real_world_test['difficulty']}")
    print(f"   - Requirements: {len(real_world_test['requirements'])} items")
    print(f"   - Evaluation criteria: {len(real_world_test['evaluation_criteria'])} items")
    print(f"   - Learning objectives: {len(real_world_test['learning_objectives'])} items")
    
    print(f"\n📋 Test Scenario:")
    print(real_world_test['scenario'])
    
    print(f"\n📝 Requirements:")
    for i, req in enumerate(real_world_test['requirements'], 1):
        print(f"   {i}. {req}")
    
    print(f"\n🎯 Learning Objectives:")
    for i, obj in enumerate(real_world_test['learning_objectives'], 1):
        print(f"   {i}. {obj}")
    
    # Test 2: Simulate AI response and evaluation
    print(f"\n🧪 Test 2: Simulating AI Response and Evaluation")
    print("-" * 40)
    
    # Simulate an AI response
    ai_response = """
    I'll help you deploy a microservices application using Docker. Here's my comprehensive solution:

    ## Dockerfile for API Service
    ```dockerfile
    FROM node:18-alpine
    WORKDIR /app
    COPY package*.json ./
    RUN npm ci --only=production
    COPY . .
    EXPOSE 3000
    CMD ["npm", "start"]
    ```

    ## Dockerfile for Auth Service
    ```dockerfile
    FROM node:18-alpine
    WORKDIR /app
    COPY package*.json ./
    RUN npm ci --only=production
    COPY . .
    EXPOSE 3001
    CMD ["npm", "start"]
    ```

    ## Docker Compose Configuration
    ```yaml
    version: '3.8'
    services:
      api:
        build: ./api
        ports:
          - "3000:3000"
        environment:
          - NODE_ENV=development
          - DATABASE_URL=postgresql://user:pass@db:5432/app
        depends_on:
          - db
          - cache
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
          interval: 30s
          timeout: 10s
          retries: 3

      auth:
        build: ./auth
        ports:
          - "3001:3001"
        environment:
          - NODE_ENV=development
          - JWT_SECRET=your-secret-key
        depends_on:
          - db
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
          interval: 30s
          timeout: 10s
          retries: 3

      db:
        image: postgres:15-alpine
        environment:
          - POSTGRES_DB=app
          - POSTGRES_USER=user
          - POSTGRES_PASSWORD=pass
        volumes:
          - postgres_data:/var/lib/postgresql/data
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U user -d app"]
          interval: 30s
          timeout: 10s
          retries: 3

      cache:
        image: redis:7-alpine
        ports:
          - "6379:6379"
        healthcheck:
          test: ["CMD", "redis-cli", "ping"]
          interval: 30s
          timeout: 10s
          retries: 3

      frontend:
        build: ./frontend
        ports:
          - "80:80"
        depends_on:
          - api
          - auth

    volumes:
      postgres_data:
    ```

    ## Production Deployment Script
    ```bash
    #!/bin/bash
    # Production deployment script
    
    # Build and tag images
    docker build -t myapp/api:latest ./api
    docker build -t myapp/auth:latest ./auth
    docker build -t myapp/frontend:latest ./frontend
    
    # Push to registry
    docker push myapp/api:latest
    docker push myapp/auth:latest
    docker push myapp/frontend:latest
    
    # Deploy to production
    docker-compose -f docker-compose.prod.yml up -d
    ```

    ## Security Considerations
    - Use multi-stage builds to reduce image size
    - Implement proper health checks
    - Use environment variables for configuration
    - Set up proper networking between services
    - Implement logging and monitoring
    - Use secrets management for sensitive data
    """
    
    # Evaluate the response
    evaluation_result = await real_world_test_service.evaluate_real_world_test(
        "guardian", real_world_test, ai_response, learning_history
    )
    
    print(f"✅ Evaluation completed:")
    print(f"   - Overall score: {evaluation_result['overall_score']}")
    print(f"   - Passed: {evaluation_result['passed']}")
    print(f"   - Learning score: {evaluation_result['learning_progress']['learning_score']}")
    
    print(f"\n📊 Individual Criteria Scores:")
    for criterion, score in evaluation_result['scores'].items():
        print(f"   - {criterion}: {score}")
    
    print(f"\n📝 Detailed Feedback:")
    for criterion, feedback in evaluation_result['feedback'].items():
        print(f"   - {criterion}: {feedback}")
    
    print(f"\n🎯 Learning Progress:")
    progress = evaluation_result['learning_progress']
    print(f"   - Addressed previous failures: {len(progress['addressed_previous_failures'])}")
    print(f"   - Demonstrated learning: {len(progress['demonstrated_learning'])}")
    print(f"   - Learning score: {progress['learning_score']:.1f}%")
    
    print(f"\n🔧 Improvement Areas:")
    for area in evaluation_result['improvement_areas']:
        print(f"   - {area}")
    
    print(f"\n💡 Recommendations:")
    for rec in evaluation_result['recommendations']:
        print(f"   - {rec}")
    
    # Test 3: Test the integrated custody protocol system
    print(f"\n🧪 Test 3: Testing Integrated Custody Protocol System")
    print("-" * 40)
    
    # Administer a custody test (should trigger real-world test due to 87 failures)
    test_result = await custody_service.administer_custody_test("guardian", TestCategory.CODE_QUALITY)
    
    print(f"✅ Custody test completed:")
    print(f"   - Test type: {test_result.get('test_type', 'unknown')}")
    print(f"   - Score: {test_result.get('score', 0)}")
    print(f"   - Passed: {test_result.get('passed', False)}")
    print(f"   - Duration: {test_result.get('duration', 0):.2f}s")
    
    if 'learning_progress' in test_result:
        print(f"   - Learning progress tracked: Yes")
    
    if 'improvement_areas' in test_result:
        print(f"   - Improvement areas identified: {len(test_result['improvement_areas'])}")
    
    # Test 4: Get learning analytics
    print(f"\n🧪 Test 4: Learning Analytics")
    print("-" * 40)
    
    analytics = await real_world_test_service.get_learning_analytics("guardian")
    
    if "error" not in analytics:
        print(f"✅ Learning analytics:")
        print(f"   - Total tests: {analytics['total_tests']}")
        print(f"   - Passed tests: {analytics['passed_tests']}")
        print(f"   - Pass rate: {analytics['pass_rate']:.1f}%")
        print(f"   - Recent pass rate: {analytics['recent_pass_rate']:.1f}%")
        print(f"   - Improvement trend: {analytics['improvement_trend']}")
        
        if analytics['common_improvement_areas']:
            print(f"   - Common improvement areas: {', '.join(analytics['common_improvement_areas'][:3])}")
    else:
        print(f"❌ No learning data available yet")
    
    print(f"\n" + "=" * 60)
    print("🏁 Real-world test system demonstration completed!")
    print("\nKey improvements:")
    print("✅ Practical, real-world scenarios (Docker, architecture, etc.)")
    print("✅ Learning-focused evaluation with progress tracking")
    print("✅ Adaptive difficulty based on performance")
    print("✅ Detailed feedback and improvement recommendations")
    print("✅ Integration with existing custody protocol system")

if __name__ == "__main__":
    asyncio.run(test_real_world_system()) 