#!/bin/bash

cd /home/ubuntu/ai-backend-python

# Fix the missing duration key error
sed -i 's/"duration": test_result\["duration"\]/"duration": test_result.get("duration", 0)/' app/services/custody_protocol_service.py

# Add comprehensive test result logging to show actual scenarios and responses
cat > fix_test_logging.py << 'EOF'
import re

# Read the custody protocol service file
with open('app/services/custody_protocol_service.py', 'r') as f:
    content = f.read()

# Add comprehensive logging after test execution
logging_addition = '''
            # Enhanced test result logging
            logger.info(f"🎯 TEST SCENARIO: {test.get('scenario', 'No scenario provided')}")
            logger.info(f"📝 AI RESPONSE for {ai}: {test_result.get('answer', 'No answer generated')[:500]}...")
            logger.info(f"📊 TEST RESULT for {ai}: Passed={test_result.get('passed', False)}, Score={test_result.get('score', 0)}, XP={test_result.get('xp_awarded', 0)}")
            if test_result.get('evaluation'):
                logger.info(f"🔍 EVALUATION for {ai}: {test_result['evaluation']}")
            logger.info(f"⏱️ DURATION for {ai}: {test_result.get('duration', 0)} seconds")
'''

# Find the line after test result persistence and add logging
pattern = r'(✅ AI response for.*persisted to database)'
replacement = r'\1' + logging_addition

content = re.sub(pattern, replacement, content)

# Also add logging for collaborative test completion
collab_logging = '''
            # Enhanced collaborative test logging
            logger.info(f"🏆 COLLABORATIVE TEST COMPLETED:")
            logger.info(f"   Participants: {test.get('ai_types', [])}")
            logger.info(f"   Scenario: {test.get('scenario', 'No scenario')}")
            logger.info(f"   Final Score: {test_result.get('score', 0)}")
            logger.info(f"   XP Awarded: {test_result.get('xp_awarded', 0)}")
            logger.info(f"   Passed: {test_result.get('passed', False)}")
            if test_result.get('evaluation'):
                logger.info(f"   Evaluation: {test_result['evaluation']}")
'''

# Find collaborative test completion and add logging
collab_pattern = r'(✅ Collaborative test completed successfully)'
collab_replacement = r'\1' + collab_logging

content = re.sub(collab_pattern, collab_replacement, content)

# Write back the modified content
with open('app/services/custody_protocol_service.py', 'w') as f:
    f.write(content)

print("✅ Enhanced test logging with comprehensive details")
EOF

python3 fix_test_logging.py

# Fix the random.sample issue in Olympic events
sed -i 's/random.sample(ai_types, 2)/random.sample(ai_types, min(2, len(ai_types)))/' app/services/custody_protocol_service.py

# Add better test scenario generation
sed -i '/generate_test.*ai_types.*test_type.*difficulty/a\
        # Add timestamp to test result\
        test_result["timestamp"] = datetime.utcnow().isoformat()\
        test_result["duration"] = test_result.get("duration", 0)\
        test_result["scenario"] = test.get("scenario", "No scenario provided")\
        test_result["ai_types"] = test.get("ai_types", [])' app/services/custody_protocol_service.py

echo "✅ Fixed critical issues: duration key, enhanced logging, and test generation"