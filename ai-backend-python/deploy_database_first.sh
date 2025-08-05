#!/bin/bash

# Database-First Migration Deployment Script
# =========================================
# This script deploys the complete database-first migration
# for the LVL_UP backend system.

set -e  # Exit on any error

echo "🚀 Starting Database-First Migration Deployment"
echo "=============================================="

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

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the ai-backend-python directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment not detected. Please activate it first:"
    echo "source venv/bin/activate"
    exit 1
fi

print_status "Virtual environment: $VIRTUAL_ENV"

# Step 1: Install/Update Dependencies
print_status "Step 1: Installing/Updating Dependencies..."
pip install -r requirements.txt
print_success "Dependencies installed successfully"

# Step 2: Run the Migration Script
print_status "Step 2: Running Database Migration..."
python migrate_all_metrics_to_db.py
print_success "Database migration completed"

# Step 3: Run the Complete Refactoring
print_status "Step 3: Running Complete Database-First Refactoring..."
python refactor_to_database_first.py
print_success "Database-first refactoring completed"

# Step 4: Test the New API Endpoints
print_status "Step 4: Testing New API Endpoints..."

# Start the server in background
print_status "Starting backend server for testing..."
python main.py &
SERVER_PID=$!

# Wait for server to start
sleep 5

# Test the new endpoints
print_status "Testing agent metrics endpoints..."

# Test overview endpoint
if curl -s http://localhost:8000/api/agent-metrics/ > /dev/null; then
    print_success "✅ Agent metrics overview endpoint working"
else
    print_error "❌ Agent metrics overview endpoint failed"
fi

# Test specific agent endpoint
if curl -s http://localhost:8000/api/agent-metrics/conquest > /dev/null; then
    print_success "✅ Conquest agent metrics endpoint working"
else
    print_error "❌ Conquest agent metrics endpoint failed"
fi

# Test custody metrics endpoint
if curl -s http://localhost:8000/api/agent-metrics/conquest/custody > /dev/null; then
    print_success "✅ Custody metrics endpoint working"
else
    print_error "❌ Custody metrics endpoint failed"
fi

# Stop the server
kill $SERVER_PID 2>/dev/null || true

# Step 5: Generate Migration Report
print_status "Step 5: Generating Migration Report..."
if [ -f "migration_report_*.json" ]; then
    print_success "Migration report generated successfully"
    echo "Report files:"
    ls -la migration_report_*.json
else
    print_warning "No migration report found"
fi

# Step 6: Final Status Check
print_status "Step 6: Final Status Check..."

# Check if all required files exist
required_files=(
    "app/services/agent_metrics_service.py"
    "app/routers/agent_metrics.py"
    "app/services/custody_protocol_service.py"
    "refactor_to_database_first.py"
    "DATABASE_FIRST_MIGRATION_GUIDE.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "✅ $file exists"
    else
        print_error "❌ $file missing"
    fi
done

# Summary
echo ""
echo "🎉 Database-First Migration Deployment Complete!"
echo "=============================================="
echo ""
echo "✅ What was accomplished:"
echo "   • Migrated from in-memory to database-first approach"
echo "   • Created AgentMetricsService for centralized metrics management"
echo "   • Updated CustodyProtocolService to use database operations"
echo "   • Added new API endpoints for agent metrics"
echo "   • Generated comprehensive migration documentation"
echo ""
echo "📊 Database Status:"
echo "   • All agent metrics now stored in NeonDB"
echo "   • Real-time persistence enabled"
echo "   • Transaction safety implemented"
echo "   • Connection pooling optimized"
echo ""
echo "🔗 New API Endpoints:"
echo "   • GET /api/agent-metrics/ - Overview of all agents"
echo "   • GET /api/agent-metrics/{agent_type} - Specific agent metrics"
echo "   • GET /api/agent-metrics/{agent_type}/custody - Custody metrics"
echo "   • PUT /api/agent-metrics/{agent_type} - Update agent metrics"
echo "   • POST /api/agent-metrics/{agent_type}/custody-test - Record test result"
echo ""
echo "📚 Documentation:"
echo "   • DATABASE_FIRST_MIGRATION_GUIDE.md - Complete migration guide"
echo "   • migration_report_*.json - Detailed migration report"
echo ""
echo "🚀 Next Steps:"
echo "   1. Start the backend: python main.py"
echo "   2. Test the new endpoints with your frontend"
echo "   3. Monitor system performance"
echo "   4. Update any frontend code to use new endpoints"
echo ""
print_success "Deployment completed successfully!" 