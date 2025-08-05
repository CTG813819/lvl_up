#!/bin/bash

cd /home/ubuntu/ai-backend-python

# Add adaptive test system integration to generate_test method
sed -i '4401a\
        # Use AdaptiveTestSystem if available\
        if hasattr(self, "adaptive_test_system") and self.adaptive_test_system:\
            logger.info(f"🎯 Using AdaptiveTestSystem for {", ".join(ai_types)}")\
            return await self.adaptive_test_system.generate_adaptive_test_scenario(ai_types, test_type)\
        \
        # Fallback to existing SCKIPIT/LLM method\
        logger.info(f"🔄 Using SCKIPIT/LLM fallback for {", ".join(ai_types)}")\
' app/services/custody_protocol_service.py

echo "✅ Added AdaptiveTestSystem integration to generate_test method"