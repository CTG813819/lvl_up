#!/bin/bash

echo "=== LVL UP Backend Status and Logs Check ==="
echo "Timestamp: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "running" ]; then
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" = "failed" ]; then
        echo -e "${RED}✗${NC} $message"
    else
        echo -e "${YELLOW}?${NC} $message"
    fi
}

echo -e "${BLUE}=== 1. System Overview ===${NC}"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime)"
echo "Memory Usage:"
free -h
echo ""
echo "Disk Usage:"
df -h /
echo ""

echo -e "${BLUE}=== 2. Service Status ===${NC}"

# Check all AI services
services=("guardian-ai" "conquest-ai" "imperium-ai" "sandbox-ai" "lvl-up-backend")

for service in "${services[@]}"; do
    echo -n "Checking $service: "
    if systemctl is-active --quiet $service; then
        print_status "running" "$service is running"
        echo "  Status: $(systemctl is-active $service)"
        echo "  Enabled: $(systemctl is-enabled $service)"
    else
        print_status "failed" "$service is not running"
        echo "  Status: $(systemctl is-active $service)"
        echo "  Enabled: $(systemctl is-enabled $service)"
    fi
    echo ""
done

echo -e "${BLUE}=== 3. Port Usage ===${NC}"
echo "Checking which ports are in use:"
netstat -tlnp | grep -E ':(8000|8001|8002|8003|8004)' || echo "No AI service ports found"
echo ""

echo -e "${BLUE}=== 4. Process Status ===${NC}"
echo "Python processes:"
ps aux | grep python | grep -v grep || echo "No Python processes found"
echo ""

echo -e "${BLUE}=== 5. Service Logs (Last 20 lines each) ===${NC}"

# Function to show logs for a service
show_service_logs() {
    local service=$1
    echo -e "${YELLOW}--- $service Logs ---${NC}"
    if systemctl is-active --quiet $service; then
        journalctl -u $service -n 20 --no-pager
    else
        echo "Service not running - showing last available logs:"
        journalctl -u $service -n 20 --no-pager 2>/dev/null || echo "No logs available"
    fi
    echo ""
}

# Show logs for each service
for service in "${services[@]}"; do
    show_service_logs $service
done

echo -e "${BLUE}=== 6. Application Logs ===${NC}"

# Check for application log files
log_dirs=(
    "/home/ubuntu/lvl_up/ai-backend-python/logs"
    "/home/ubuntu/lvl_up/logs"
    "/var/log/lvl-up"
)

for log_dir in "${log_dirs[@]}"; do
    if [ -d "$log_dir" ]; then
        echo -e "${YELLOW}--- Logs in $log_dir ---${NC}"
        ls -la "$log_dir" 2>/dev/null || echo "Cannot access $log_dir"
        echo ""
        
        # Show recent log files
        find "$log_dir" -name "*.log" -type f -exec ls -lt {} + 2>/dev/null | head -5 || echo "No log files found"
        echo ""
    fi
done

echo -e "${BLUE}=== 7. Error Logs (Last 50 lines) ===${NC}"
echo "Recent system errors:"
journalctl -p err -n 50 --no-pager | grep -E "(guardian|conquest|imperium|sandbox|lvl-up)" || echo "No recent errors found"
echo ""

echo -e "${BLUE}=== 8. Network Connectivity ===${NC}"
echo "Testing local connectivity:"
for port in 8000 8001 8002 8003 8004; do
    if curl -s --connect-timeout 2 http://localhost:$port/health >/dev/null 2>&1; then
        print_status "running" "Port $port is responding"
    else
        print_status "failed" "Port $port is not responding"
    fi
done
echo ""

echo -e "${BLUE}=== 9. Environment Variables ===${NC}"
echo "Checking environment for AI services:"
for service in "${services[@]}"; do
    echo -e "${YELLOW}--- $service Environment ---${NC}"
    systemctl show $service --property=Environment 2>/dev/null | grep -v "^$" || echo "No environment variables found"
    echo ""
done

echo -e "${BLUE}=== 10. Resource Usage ===${NC}"
echo "CPU and Memory usage by AI processes:"
ps aux | grep -E "(guardian|conquest|imperium|sandbox)" | grep -v grep | awk '{print $1, $2, $3, $4, $11}' | head -10 || echo "No AI processes found"
echo ""

echo "=== Check Complete ==="
echo "For real-time monitoring, use: journalctl -u [service-name] -f"
echo "To restart a service: sudo systemctl restart [service-name]" 