#!/bin/bash

# Deploy and Run Comprehensive System Audit Script
# This script helps you SCP the audit script to your EC2 instance and run it

set -e

# Configuration - UPDATE THESE VALUES
EC2_HOST="your-ec2-instance.com"  # Replace with your EC2 public IP or domain
EC2_USER="ubuntu"                  # Replace with your EC2 username
EC2_KEY_PATH="~/.ssh/your-key.pem" # Replace with path to your EC2 key file
REMOTE_DIR="/home/ubuntu/audit"    # Directory on EC2 where audit will run

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== LVL_UP AI Backend System Audit Deployment ===${NC}"
echo

# Check if required tools are available
check_requirements() {
    echo -e "${YELLOW}Checking requirements...${NC}"
    
    if ! command -v scp &> /dev/null; then
        echo -e "${RED}Error: scp is not installed${NC}"
        exit 1
    fi
    
    if ! command -v ssh &> /dev/null; then
        echo -e "${RED}Error: ssh is not installed${NC}"
        exit 1
    fi
    
    if [ ! -f "comprehensive_system_audit.py" ]; then
        echo -e "${RED}Error: comprehensive_system_audit.py not found in current directory${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Requirements check passed${NC}"
}

# Validate configuration
validate_config() {
    echo -e "${YELLOW}Validating configuration...${NC}"
    
    if [ "$EC2_HOST" = "your-ec2-instance.com" ]; then
        echo -e "${RED}Error: Please update EC2_HOST in this script${NC}"
        exit 1
    fi
    
    if [ "$EC2_KEY_PATH" = "~/.ssh/your-key.pem" ]; then
        echo -e "${RED}Error: Please update EC2_KEY_PATH in this script${NC}"
        exit 1
    fi
    
    # Expand tilde in key path
    EC2_KEY_PATH=$(eval echo $EC2_KEY_PATH)
    
    if [ ! -f "$EC2_KEY_PATH" ]; then
        echo -e "${RED}Error: SSH key file not found at $EC2_KEY_PATH${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Configuration validation passed${NC}"
}

# Create remote directory and copy files
deploy_audit_script() {
    echo -e "${YELLOW}Deploying audit script to EC2...${NC}"
    
    # Create remote directory
    ssh -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "mkdir -p $REMOTE_DIR"
    
    # Copy audit script
    scp -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no comprehensive_system_audit.py "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"
    
    echo -e "${GREEN}✓ Audit script deployed successfully${NC}"
}

# Install dependencies on EC2
install_dependencies() {
    echo -e "${YELLOW}Installing dependencies on EC2...${NC}"
    
    ssh -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" << 'EOF'
        cd /home/ubuntu/audit
        
        # Update package list
        sudo apt-get update
        
        # Install Python dependencies
        sudo apt-get install -y python3-pip python3-psycopg2-binary
        
        # Install Python packages
        pip3 install requests psycopg2-binary websocket-client
        
        echo "✓ Dependencies installed"
EOF
    
    echo -e "${GREEN}✓ Dependencies installation completed${NC}"
}

# Run the audit
run_audit() {
    echo -e "${YELLOW}Running comprehensive system audit...${NC}"
    echo -e "${BLUE}This may take several minutes to complete...${NC}"
    echo
    
    ssh -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" << 'EOF'
        cd /home/ubuntu/audit
        
        # Set proper permissions
        chmod +x comprehensive_system_audit.py
        
        # Run the audit
        python3 comprehensive_system_audit.py
        
        echo ""
        echo "=== AUDIT COMPLETED ==="
        echo "Check the following files for results:"
        echo "- comprehensive_audit_report.json (detailed JSON report)"
        echo "- system_audit.log (audit execution log)"
EOF
    
    echo -e "${GREEN}✓ Audit completed${NC}"
}

# Download results
download_results() {
    echo -e "${YELLOW}Downloading audit results...${NC}"
    
    # Create local results directory
    mkdir -p audit_results
    
    # Download audit files
    scp -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST:$REMOTE_DIR/comprehensive_audit_report.json" ./audit_results/
    scp -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST:$REMOTE_DIR/system_audit.log" ./audit_results/
    
    echo -e "${GREEN}✓ Results downloaded to ./audit_results/${NC}"
}

# Display results summary
show_results() {
    echo -e "${BLUE}=== AUDIT RESULTS SUMMARY ===${NC}"
    
    if [ -f "./audit_results/comprehensive_audit_report.json" ]; then
        echo -e "${YELLOW}Detailed report: ./audit_results/comprehensive_audit_report.json${NC}"
        echo -e "${YELLOW}Execution log: ./audit_results/system_audit.log${NC}"
        
        # Extract and display overall status
        OVERALL_STATUS=$(python3 -c "
import json
try:
    with open('./audit_results/comprehensive_audit_report.json', 'r') as f:
        data = json.load(f)
    print(data.get('overall_status', 'UNKNOWN'))
except:
    print('ERROR_READING_REPORT')
")
        
        case $OVERALL_STATUS in
            "PASSED")
                echo -e "${GREEN}✓ Overall Status: PASSED - System is healthy${NC}"
                ;;
            "WARNING")
                echo -e "${YELLOW}⚠ Overall Status: WARNING - Some issues detected${NC}"
                ;;
            "FAILED")
                echo -e "${RED}✗ Overall Status: FAILED - Critical issues found${NC}"
                ;;
            *)
                echo -e "${RED}? Overall Status: $OVERALL_STATUS${NC}"
                ;;
        esac
    else
        echo -e "${RED}Error: Could not find audit results${NC}"
    fi
}

# Cleanup remote files (optional)
cleanup_remote() {
    read -p "Do you want to clean up audit files on EC2? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Cleaning up remote files...${NC}"
        ssh -i "$EC2_KEY_PATH" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "rm -rf $REMOTE_DIR"
        echo -e "${GREEN}✓ Remote cleanup completed${NC}"
    else
        echo -e "${BLUE}Remote files preserved at $REMOTE_DIR${NC}"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}Starting deployment process...${NC}"
    echo
    
    check_requirements
    validate_config
    deploy_audit_script
    install_dependencies
    run_audit
    download_results
    show_results
    cleanup_remote
    
    echo
    echo -e "${GREEN}=== DEPLOYMENT COMPLETED ===${NC}"
    echo -e "${BLUE}Check ./audit_results/ for detailed audit information${NC}"
}

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --deploy-only  Only deploy the script (don't run audit)"
    echo "  --run-only     Only run the audit (assumes script is already deployed)"
    echo
    echo "Before running, update the configuration variables at the top of this script:"
    echo "  - EC2_HOST: Your EC2 instance public IP or domain"
    echo "  - EC2_USER: Your EC2 username (usually 'ubuntu' or 'ec2-user')"
    echo "  - EC2_KEY_PATH: Path to your EC2 private key file"
    echo
    echo "Example:"
    echo "  $0"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    --deploy-only)
        check_requirements
        validate_config
        deploy_audit_script
        install_dependencies
        echo -e "${GREEN}Deployment completed. Run audit manually on EC2.${NC}"
        exit 0
        ;;
    --run-only)
        validate_config
        run_audit
        download_results
        show_results
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        show_help
        exit 1
        ;;
esac 