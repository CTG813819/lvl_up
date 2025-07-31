#!/bin/bash

# Update the generate_test method to use AdaptiveTestSystem
cd /home/ubuntu/ai-backend-python

# Create a temporary file with the new generate_test method
cat > temp_generate_test.py << 'EOF'
    async def generate_test(self, ai_types: list, test_type: str, difficulty: str) -> dict:
        """Generate a live test with adaptive difficulty based on AI performance"""
        try:
            # Use AdaptiveTestSystem if available
            if hasattr(self, 'adaptive_test_system') and self.adaptive_test_system:
                logger.info(f"🎯 Using AdaptiveTestSystem for {', '.join(ai_types)}")
                return await self.adaptive_test_system.generate_adaptive_test_scenario(ai_types, test_type)
            
            # Fallback to existing SCKIPIT/LLM method
            logger.info(f"🔄 Using SCKIPIT/LLM fallback for {', '.join(ai_types)}")
            
            # Gather learning logs and analytics for all AIs
            learning_histories = {ai: await self.learning_service.get_learning_insights(ai) for ai in ai_types}
            knowledge_gaps = {ai: await self._identify_knowledge_gaps(ai, [], []) for ai in ai_types}
            analytics = {ai: await self.learning_service.get_learning_insights(ai) for ai in ai_types}

            # Check if sckipit_service is available
            if self.sckipit_service:
                # Use SCKIPIT/LLM to generate a test
                if len(ai_types) == 1:
                    # Single-AI test (standard)
                    scenario = await self.sckipit_service.generate_olympus_treaty_scenario(
                        ai_type=ai_types[0],
                        learning_history=learning_histories[ai_types[0]],
                        knowledge_gaps=knowledge_gaps[ai_types[0]],
                        analytics=analytics[ai_types[0]],
                        difficulty=difficulty
                    )
                    return {"type": "single", "ai_types": ai_types, "scenario": scenario, "difficulty": difficulty}
                else:
                    # Collaborative test: generate a multi-AI, high-difficulty, mixed-type challenge
                    scenario = await self.sckipit_service.generate_collaborative_challenge(
                        ai_types=ai_types,
                        learning_histories=learning_histories,
                        knowledge_gaps=knowledge_gaps,
                        analytics=analytics,
                        difficulty=difficulty,
                        test_type=test_type
                    )
                    return {"type": "collaborative", "ai_types": ai_types, "scenario": scenario, "difficulty": difficulty}
            else:
                # Fallback to basic test generation
                if len(ai_types) == 1:
                    scenario = f"Basic test scenario for {ai_types[0]} with difficulty {difficulty}. Demonstrate your knowledge and capabilities."
                    return {"type": "single", "ai_types": ai_types, "scenario": scenario, "difficulty": difficulty}
                else:
                    scenario = f"Collaborative test scenario for {', '.join(ai_types)} with difficulty {difficulty}. Work together to solve this challenge."
                    return {"type": "collaborative", "ai_types": ai_types, "scenario": scenario, "difficulty": difficulty}
        except Exception as e:
            logger.error(f"Error generating test: {str(e)}")
            # Fallback to basic test
            if len(ai_types) == 1:
                scenario = f"Fallback test scenario for {ai_types[0]} with difficulty {difficulty}."
                return {"type": "single", "ai_types": ai_types, "scenario": scenario, "difficulty": difficulty}
            else:
                scenario = f"Fallback collaborative test for {', '.join(ai_types)} with difficulty {difficulty}."
                return {"type": "collaborative", "ai_types": ai_types, "scenario": scenario, "difficulty": difficulty}
EOF

# Find the start and end of the current generate_test method
start_line=$(grep -n "async def generate_test" app/services/custody_protocol_service.py | cut -d: -f1)
end_line=$(sed -n "${start_line},$p" app/services/custody_protocol_service.py | grep -n "^    async def" | head -1 | cut -d: -f1)
if [ -z "$end_line" ]; then
    end_line=$(wc -l < app/services/custody_protocol_service.py)
else
    end_line=$((start_line + end_line - 2))
fi

# Replace the generate_test method
sed -i "${start_line},${end_line}d" app/services/custody_protocol_service.py
sed -i "${start_line}i\\$(cat temp_generate_test.py)" app/services/custody_protocol_service.py

# Clean up
rm temp_generate_test.py

echo "✅ Updated generate_test method to use AdaptiveTestSystem"