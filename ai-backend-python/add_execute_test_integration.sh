#!/bin/bash

cd /home/ubuntu/ai-backend-python

# Add adaptive test system integration to execute_test method
# Find the line after test result is created and add adaptive system update
sed -i '/Store test result in database/a\
                    # Update adaptive test system with test results\
                    if hasattr(self, "adaptive_test_system") and self.adaptive_test_system:\
                        await self.adaptive_test_system.update_ai_growth_analytics(ai, test_result)\
                        logger.info(f"✅ Updated adaptive difficulty for {ai} based on test performance")\
' app/services/custody_protocol_service.py

echo "✅ Added AdaptiveTestSystem integration to execute_test method"