#!/bin/bash

cd /home/ubuntu/ai-backend-python

# Add the missing except block for EnhancedTestGenerator
sed -i '197a\
        except Exception as e:\
            logger.warning(f"Failed to initialize EnhancedTestGenerator: {e}")\
            instance.enhanced_test_generator = None' app/services/custody_protocol_service.py

echo "✅ Fixed syntax error"