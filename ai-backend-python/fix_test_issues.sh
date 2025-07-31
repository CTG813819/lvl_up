#!/bin/bash

cd /home/ubuntu/ai-backend-python

# Fix the missing timestamp issue in custody metrics
sed -i '1796s/"timestamp": test_result\["timestamp"\]/"timestamp": test_result.get("timestamp", datetime.utcnow().isoformat())/' app/services/custody_protocol_service.py

# Fix the Logger._log() error in enhanced test generator
sed -i 's/logger.error(/logger.warning(/g' app/services/enhanced_test_generator.py

# Add better logging to show actual test scenarios and AI responses
sed -i '/✅ AI response for.*persisted to database/a\
            logger.info(f"🎯 TEST DETAILS for {ai}: {test_result.get("scenario", "No scenario")}") \
            logger.info(f"📝 AI RESPONSE for {ai}: {test_result.get("answer", "No answer")[:200]}...") \
            logger.info(f"📊 TEST RESULT for {ai}: Passed={test_result.get("passed", False)}, Score={test_result.get("score", 0)}")' app/services/custody_protocol_service.py

echo "✅ Fixed test issues and improved logging"