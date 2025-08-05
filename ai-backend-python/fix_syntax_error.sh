#!/bin/bash

cd /home/ubuntu/ai-backend-python

# Fix the syntax error by removing the malformed code block
sed -i '4424,4434d' app/services/custody_protocol_service.py

# Fix the incomplete line at 4423
sed -i '4423s/scenario = await self\.sckipit_service\.generate_olympus_treaty_scenario/scenario = await self.sckipit_service.generate_olympus_treaty_scenario(ai_types[0], difficulty)/' app/services/custody_protocol_service.py

# Add proper diverse scenario generation in the right place
sed -i '/scenario = await self\.sckipit_service\.generate_olympus_treaty_scenario/a\
                # Generate diverse test scenarios if needed\
                if not scenario or scenario == "Basic test scenario":\
                    scenarios = [\
                        "Design a high-performance microservices architecture for a real-time analytics platform",\
                        "Implement a secure authentication system with OAuth2, JWT, and role-based access control",\
                        "Create a scalable data pipeline for processing 1M+ events per second",\
                        "Build a fault-tolerant distributed system with circuit breakers and retry mechanisms",\
                        "Develop a machine learning pipeline with automated model training and deployment",\
                        "Architect a multi-region deployment with global load balancing and disaster recovery",\
                        "Design a real-time collaboration platform with WebSocket connections and conflict resolution",\
                        "Implement a blockchain-based supply chain tracking system with smart contracts",\
                        "Create an AI-powered recommendation engine with A/B testing and personalization",\
                        "Build a serverless architecture for IoT device management and data processing"\
                    ]\
                    scenario = random.choice(scenarios)\
                    logger.info(f"🎯 Generated diverse test scenario: {scenario}")' app/services/custody_protocol_service.py

echo "✅ Fixed syntax error in custody_protocol_service.py"