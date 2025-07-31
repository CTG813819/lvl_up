#!/bin/bash

cd /home/ubuntu/ai-backend-python

# First, restore from backup
cp app/services/custody_protocol_service_backup.py app/services/custody_protocol_service.py

# Add the import
sed -i '55i from app.services.adaptive_test_system import AdaptiveTestSystem' app/services/custody_protocol_service.py

# Find the line after EnhancedTestGenerator initialization and add AdaptiveTestSystem properly
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

echo "✅ Fixed and added AdaptiveTestSystem properly"