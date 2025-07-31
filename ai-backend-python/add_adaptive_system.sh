#!/bin/bash

# Add AdaptiveTestSystem initialization to custody_protocol_service.py
cd /home/ubuntu/ai-backend-python

# Find the line number where EnhancedTestGenerator initialization ends
line_num=$(grep -n "EnhancedTestGenerator initialized successfully" app/services/custody_protocol_service.py | cut -d: -f1)

# Add AdaptiveTestSystem initialization after EnhancedTestGenerator
sed -i "${line_num}a\\
        # Initialize AdaptiveTestSystem\\
        try:\\
            instance.adaptive_test_system = AdaptiveTestSystem()\\
            await instance.adaptive_test_system.initialize(instance.agent_metrics_service, instance.learning_service)\\
            logger.info(\"AdaptiveTestSystem initialized successfully\")\\
        except Exception as e:\\
            logger.warning(f\"Failed to initialize AdaptiveTestSystem: {e}\")\\
            instance.adaptive_test_system = None" app/services/custody_protocol_service.py

echo "AdaptiveTestSystem initialization added to custody_protocol_service.py"