#!/bin/bash

cd /home/ubuntu/ai-backend-python

# Add comprehensive test logging to show actual scenarios and responses
cat > enhance_logging.py << 'EOF'
import re

# Read the custody protocol service file
with open('app/services/custody_protocol_service.py', 'r') as f:
    content = f.read()

# Add logging after AI response persistence
logging_addition = '''
            # Enhanced logging for test details
            if test_result.get("scenario"):
                logger.info(f"🎯 TEST SCENARIO for {ai}: {test_result['scenario']}")
            if test_result.get("answer"):
                answer_preview = test_result["answer"][:300] + "..." if len(test_result["answer"]) > 300 else test_result["answer"]
                logger.info(f"📝 AI RESPONSE for {ai}: {answer_preview}")
            logger.info(f"📊 TEST RESULT for {ai}: Passed={test_result.get('passed', False)}, Score={test_result.get('score', 0)}, XP={test_result.get('xp_awarded', 0)}")
            if test_result.get("evaluation"):
                logger.info(f"🔍 EVALUATION for {ai}: {test_result['evaluation']}")
'''

# Find the line after AI response persistence and add logging
pattern = r'(✅ AI response for.*persisted to database)'
replacement = r'\1' + logging_addition

content = re.sub(pattern, replacement, content)

# Write back the modified content
with open('app/services/custody_protocol_service.py', 'w') as f:
    f.write(content)

print("✅ Enhanced test logging added")
EOF

python3 enhance_logging.py

echo "✅ Enhanced test logging to show actual scenarios and AI responses"