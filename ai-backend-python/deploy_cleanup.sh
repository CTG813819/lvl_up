#!/bin/bash

# Proposal Cleanup Deployment Script
# ==================================
# This script provides easy access to the comprehensive proposal cleanup system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Proposal Cleanup Deployment Script"
    echo "=================================="
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --aggressive     Remove ALL proposals (use with caution!)"
    echo "  --conservative   Remove only pending, test-failed, and expired proposals (default)"
    echo "  --selective      Remove proposals older than specified hours"
    echo "  --hours N        For selective strategy: remove proposals older than N hours (default: 24)"
    echo "  --backup-only    Only create backup, don't delete anything"
    echo "  --verify-only    Only check current state, don't delete anything"
    echo "  --no-backup      Skip backup creation"
    echo "  --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --conservative                    # Safe cleanup (default)"
    echo "  $0 --aggressive                      # Remove everything"
    echo "  $0 --selective --hours 6             # Remove proposals older than 6 hours"
    echo "  $0 --backup-only                     # Just create backup"
    echo "  $0 --verify-only                     # Just check current state"
    echo ""
}

# Function to check if Python is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    print_success "Python 3 found: $(python3 --version)"
}

# Function to check if we're in the right directory
check_directory() {
    if [ ! -f "cleanup_all_pending_proposals.py" ]; then
        print_error "cleanup_all_pending_proposals.py not found in current directory"
        print_error "Please run this script from the ai-backend-python directory"
        exit 1
    fi
    
    print_success "Found cleanup script in current directory"
}

# Function to run the cleanup
run_cleanup() {
    local args="$1"
    
    print_status "Starting proposal cleanup..."
    print_status "Command: python3 cleanup_all_pending_proposals.py $args"
    echo ""
    
    python3 cleanup_all_pending_proposals.py $args
    
    if [ $? -eq 0 ]; then
        print_success "Cleanup completed successfully!"
    else
        print_error "Cleanup failed!"
        exit 1
    fi
}

# Main script logic
main() {
    # Parse command line arguments
    STRATEGY="conservative"
    HOURS=24
    BACKUP_ONLY=false
    VERIFY_ONLY=false
    NO_BACKUP=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --aggressive)
                STRATEGY="aggressive"
                shift
                ;;
            --conservative)
                STRATEGY="conservative"
                shift
                ;;
            --selective)
                STRATEGY="selective"
                shift
                ;;
            --hours)
                HOURS="$2"
                shift 2
                ;;
            --backup-only)
                BACKUP_ONLY=true
                shift
                ;;
            --verify-only)
                VERIFY_ONLY=true
                shift
                ;;
            --no-backup)
                NO_BACKUP=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Show banner
    echo "=========================================="
    echo "  PROPOSAL CLEANUP DEPLOYMENT SCRIPT"
    echo "=========================================="
    echo ""
    
    # Pre-flight checks
    print_status "Performing pre-flight checks..."
    check_python
    check_directory
    
    # Build command arguments
    CMD_ARGS=""
    
    if [ "$BACKUP_ONLY" = true ]; then
        CMD_ARGS="--backup-only"
        print_warning "BACKUP-ONLY MODE: No proposals will be deleted"
    elif [ "$VERIFY_ONLY" = true ]; then
        CMD_ARGS="--verify-only"
        print_warning "VERIFY-ONLY MODE: No proposals will be deleted"
    else
        CMD_ARGS="--strategy $STRATEGY"
        
        if [ "$STRATEGY" = "selective" ]; then
            CMD_ARGS="$CMD_ARGS --hours-old $HOURS"
        fi
        
        if [ "$NO_BACKUP" = true ]; then
            CMD_ARGS="$CMD_ARGS --no-backup"
            print_warning "BACKUP DISABLED: No backup will be created"
        fi
        
        # Show strategy confirmation
        case $STRATEGY in
            aggressive)
                print_warning "AGGRESSIVE STRATEGY: This will remove ALL proposals!"
                echo -n "Are you sure you want to continue? (yes/no): "
                read -r confirm
                if [ "$confirm" != "yes" ]; then
                    print_error "Operation cancelled by user"
                    exit 1
                fi
                ;;
            conservative)
                print_status "CONSERVATIVE STRATEGY: Will remove pending, test-failed, and expired proposals"
                ;;
            selective)
                print_status "SELECTIVE STRATEGY: Will remove proposals older than $HOURS hours"
                ;;
        esac
    fi
    
    echo ""
    print_status "Ready to execute cleanup..."
    echo ""
    
    # Run the cleanup
    run_cleanup "$CMD_ARGS"
    
    echo ""
    print_success "Deployment script completed successfully!"
}

# Run main function with all arguments
main "$@" 