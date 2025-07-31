#!/bin/bash

cd /home/ubuntu/ai-backend-python

# Fix the random.sample error on line 5198
sed -i '5198s/ai_pair = random.sample(ai_types, 2)/# Ensure we have at least 2 AIs for adversarial test\n            if len(ai_types) >= 2:\n                ai_pair = random.sample(ai_types, 2)\n            else:\n                # Fallback to standard test if not enough AIs\n                test_type = "standard"\n                ai_pair = [ai_types[0]] if ai_types else []/' app/services/custody_protocol_service.py

echo "✅ Fixed random.sample error in adversarial testing"