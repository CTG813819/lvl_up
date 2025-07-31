#!/bin/bash
# AI Services Monitoring Script
echo "AI Services Monitoring Dashboard"
echo "================================"
echo ""

# Function to check service status
check_service() {
    local service_name=$1
    local display_name=$2
    
    echo "$display_name Status:"
    if sudo systemctl is-active --quiet $service_name; then
        echo "OK: $display_name is running"
        echo "   PID: $(sudo systemctl show -p MainPID --value $service_name)"
        echo "   Uptime: $(sudo systemctl show -p ActiveEnterTimestamp --value $service_name)"
    else
        echo "ERROR: $display_name is not running"
        echo "   Last error: $(sudo journalctl -u $service_name --no-pager -n 5 --no-full)"
    fi
    echo ""
}

# Check each service
check_service "imperium-ai.service" "Imperium AI"
check_service "sandbox-ai.service" "Sandbox AI"
check_service "custodes-ai.service" "Custodes AI"
check_service "guardian-ai.service" "Guardian AI"

# System resources
echo "System Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df / | tail -1 | awk '{print $5}')"
echo ""

# Recent logs
echo "Recent Activity (last 10 entries):"
echo "=================================="
for service in imperium-ai sandbox-ai custodes-ai guardian-ai; do
    echo ""
    echo "$service:"
    sudo journalctl -u $service.service --no-pager -n 10 --no-full | grep -E "(error|warning|info)" || echo "   No recent activity"
done
