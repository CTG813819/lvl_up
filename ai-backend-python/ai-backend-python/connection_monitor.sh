#!/bin/bash
# Connection monitoring script
LOG_FILE="/home/ubuntu/connection_monitor.log"

while true; do
    echo "$(date): Checking backend connectivity..." >> $LOG_FILE
    
    # Check if backend is responding
    if curl -s http://localhost:8000/api/imperium/persistence/learning-analytics > /dev/null; then
        echo "$(date): Backend is responding" >> $LOG_FILE
    else
        echo "$(date): Backend not responding, restarting service" >> $LOG_FILE
        sudo systemctl restart ai-backend-python.service
    fi
    
    # Check system resources
    echo "$(date): Memory usage: $(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')" >> $LOG_FILE
    echo "$(date): CPU usage: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1)%" >> $LOG_FILE
    
    sleep 300  # Check every 5 minutes
done
