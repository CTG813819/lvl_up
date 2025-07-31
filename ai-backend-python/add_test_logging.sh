#!/bin/bash

cd /home/ubuntu/ai-backend-python

# Find the line where AI responses are persisted and add enhanced logging
sed -i '/✅ AI response for.*persisted to database/a\
            # Enhanced logging for test details\
            if test_result.get("scenario"):\
                logger.info(f"🎯 TEST SCENARIO for {ai}: {test_result[\"scenario\"]}")\
            if test_result.get("answer"):\
                answer_preview = test_result["answer"][:300] + "..." if len(test_result["answer"]) > 300 else test_result["answer"]\
                logger.info(f"📝 AI RESPONSE for {ai}: {answer_preview}")\
            logger.info(f"📊 TEST RESULT for {ai}: Passed={test_result.get(\"passed\", False)}, Score={test_result.get(\"score\", 0)}, XP={test_result.get(\"xp_awarded\", 0)}")\
            if test_result.get("evaluation"):\
                logger.info(f"🔍 EVALUATION for {ai}: {test_result[\"evaluation\"]}")' app/services/custody_protocol_service.py

echo "✅ Added enhanced test logging"