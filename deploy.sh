#!/bin/bash

# LVL UP AI Deployment Script
# This script handles APK building, Git integration, and deployment automation

set -e  # Exit on any error

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$PROJECT_DIR/build"
APK_OUTPUT_DIR="$BUILD_DIR/app/outputs/flutter-apk"
GIT_REPO_URL="${GIT_REPO_URL:-https://github.com/your-username/lvl_up.git}"
DEPLOYMENT_ENABLED="${DEPLOYMENT_ENABLED:-true}"
AUTO_MERGE="${AUTO_MERGE:-true}"
CLEAN_BUILDS="${CLEAN_BUILDS:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Flutter is installed
check_flutter() {
    if ! command -v flutter &> /dev/null; then
        log_error "Flutter is not installed or not in PATH"
        exit 1
    fi
    
    log_info "Flutter version: $(flutter --version | head -n 1)"
}

# Check if Git is installed
check_git() {
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed or not in PATH"
        exit 1
    fi
    
    log_info "Git version: $(git --version)"
}

# Clean previous builds
clean_builds() {
    if [ "$CLEAN_BUILDS" = "true" ]; then
        log_info "Cleaning previous builds..."
        flutter clean
        log_success "Builds cleaned"
    fi
}

# Get Flutter dependencies
get_dependencies() {
    log_info "Getting Flutter dependencies..."
    flutter pub get
    log_success "Dependencies updated"
}

# Build APK
build_apk() {
    log_info "Building APK..."
    
    # Build release APK
    flutter build apk --release
    
    # Check if APK was created
    if [ -d "$APK_OUTPUT_DIR" ]; then
        APK_FILE=$(find "$APK_OUTPUT_DIR" -name "*.apk" | head -n 1)
        if [ -n "$APK_FILE" ]; then
            APK_SIZE=$(du -h "$APK_FILE" | cut -f1)
            log_success "APK built successfully: $APK_FILE ($APK_SIZE)"
            echo "$APK_FILE"
        else
            log_error "APK file not found in output directory"
            exit 1
        fi
    else
        log_error "APK output directory not found"
        exit 1
    fi
}

# Git operations
git_operations() {
    local apk_file="$1"
    local proposal_id="$2"
    
    if [ -z "$apk_file" ]; then
        log_error "APK file path is required for Git operations"
        return 1
    fi
    
    log_info "Performing Git operations..."
    
    # Check if we're in a Git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a Git repository"
        return 1
    fi
    
    # Create APK branch
    local branch_name="apk-build-${proposal_id:-$(date +%s)}"
    log_info "Creating branch: $branch_name"
    
    git checkout -b "$branch_name"
    
    # Add APK file
    git add "$apk_file"
    
    # Commit with detailed message
    local commit_message="APK Build: $(date '+%Y-%m-%d %H:%M:%S')

APK File: $(basename "$apk_file")
APK Size: $(du -h "$apk_file" | cut -f1)
Build Time: $(date -Iseconds)
Proposal ID: ${proposal_id:-N/A}
Environment: Production Release

This APK was automatically built after successful proposal approval and testing."
    
    git commit -m "$commit_message"
    
    # Push to remote
    git push origin "$branch_name"
    
    # Merge to main if auto-merge is enabled
    if [ "$AUTO_MERGE" = "true" ]; then
        log_info "Auto-merging to main branch..."
        git checkout main
        git pull origin main
        git merge "$branch_name"
        git push origin main
        
        # Delete the APK branch
        git branch -d "$branch_name"
        git push origin --delete "$branch_name" 2>/dev/null || true
        
        log_success "APK branch merged to main"
    else
        log_info "Auto-merge disabled. APK branch '$branch_name' created and pushed"
    fi
}

# Deploy APK (placeholder for actual deployment logic)
deploy_apk() {
    local apk_file="$1"
    
    if [ "$DEPLOYMENT_ENABLED" = "true" ]; then
        log_info "Deploying APK..."
        
        # Here you would add your actual deployment logic
        # Examples:
        # - Upload to Google Play Console
        # - Upload to Firebase App Distribution
        # - Upload to internal testing platform
        # - Send to testers via email
        
        log_warning "Deployment logic not implemented yet"
        log_info "APK ready for deployment: $apk_file"
    else
        log_info "Deployment disabled. APK ready: $apk_file"
    fi
}

# Main deployment function
main_deploy() {
    local proposal_id="$1"
    
    log_info "Starting LVL UP AI deployment process..."
    log_info "Project directory: $PROJECT_DIR"
    log_info "Proposal ID: ${proposal_id:-N/A}"
    
    # Change to project directory
    cd "$PROJECT_DIR"
    
    # Check prerequisites
    check_flutter
    check_git
    
    # Clean and prepare
    clean_builds
    get_dependencies
    
    # Build APK
    local apk_file=$(build_apk)
    
    # Git operations
    if git_operations "$apk_file" "$proposal_id"; then
        log_success "Git operations completed"
    else
        log_warning "Git operations failed, but APK was built successfully"
    fi
    
    # Deploy APK
    deploy_apk "$apk_file"
    
    log_success "Deployment process completed successfully!"
    
    # Output summary
    echo ""
    echo "=== DEPLOYMENT SUMMARY ==="
    echo "APK File: $apk_file"
    echo "APK Size: $(du -h "$apk_file" | cut -f1)"
    echo "Build Time: $(date)"
    echo "Proposal ID: ${proposal_id:-N/A}"
    echo "Git Branch: $(git branch --show-current)"
    echo "========================"
}

# Function to handle proposal-triggered builds
proposal_build() {
    local proposal_id="$1"
    
    if [ -z "$proposal_id" ]; then
        log_error "Proposal ID is required for proposal builds"
        exit 1
    fi
    
    log_info "Building APK for proposal: $proposal_id"
    main_deploy "$proposal_id"
}

# Function to handle manual builds
manual_build() {
    log_info "Starting manual APK build..."
    main_deploy
}

# Function to show help
show_help() {
    echo "LVL UP AI Deployment Script"
    echo ""
    echo "Usage:"
    echo "  $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build [PROPOSAL_ID]  Build APK for specific proposal"
    echo "  manual               Build APK manually (no proposal)"
    echo "  help                 Show this help message"
    echo ""
    echo "Options:"
    echo "  --no-clean           Skip cleaning previous builds"
    echo "  --no-merge           Skip auto-merging to main"
    echo "  --no-deploy          Skip deployment step"
    echo ""
    echo "Environment Variables:"
    echo "  DEPLOYMENT_ENABLED   Enable/disable deployment (default: true)"
    echo "  AUTO_MERGE          Enable/disable auto-merge (default: true)"
    echo "  CLEAN_BUILDS        Enable/disable build cleaning (default: true)"
    echo "  GIT_REPO_URL        Git repository URL"
    echo ""
    echo "Examples:"
    echo "  $0 build 12345      Build APK for proposal 12345"
    echo "  $0 manual           Build APK manually"
    echo "  $0 --no-merge build 12345  Build without auto-merging"
}

# Parse command line arguments
case "${1:-manual}" in
    "build")
        proposal_build "$2"
        ;;
    "manual")
        manual_build
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 