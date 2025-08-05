#!/bin/bash

echo "🚀 Starting comprehensive test suite..."

# Navigate to project root
cd /path/to/your/lvl_up_project

echo "📱 Running Flutter tests..."
flutter test

echo "🔧 Running Node.js backend tests..."

# Navigate to backend directory
cd ai-backend

# Run all test scripts
echo "Testing Chaos Warp functionality..."
node scripts/test-chaos-warp.js

echo "Testing Proposal Integration..."
node scripts/test-proposal-integration.js

echo "Validating App Functionality..."
node scripts/validate-app-functionality.js

echo "Testing Complete System Integration..."
node scripts/test-complete-system-integration.js

echo "Testing GitHub Workflow Integration..."
node scripts/test-github-workflow-integration.js

echo "✅ All tests completed!" 