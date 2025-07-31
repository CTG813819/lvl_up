#!/bin/bash

cd /home/ubuntu/ai-backend-python

# Comment out the problematic line that calls a non-existent method
sed -i 's/await scheduled_notification_service.start_notification_cycle()/# await scheduled_notification_service.start_notification_cycle()  # Method not implemented/' app/main.py

echo "✅ Fixed startup error by commenting out problematic method call"