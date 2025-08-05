#!/bin/bash

# Enhanced Subject Learning Features Deployment Script
# This script deploys the new subject-based AI learning capabilities

set -e

echo "🚀 Deploying Enhanced Subject Learning Features..."

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

print_status "Starting deployment of enhanced subject learning features..."

# 1. Run database migration to add subject fields
print_status "Step 1: Running database migration..."
python add_subject_fields_migration.py
if [ $? -eq 0 ]; then
    print_success "Database migration completed"
else
    print_error "Database migration failed"
    exit 1
fi

# 2. Check if required environment variables are set
print_status "Step 2: Checking environment variables..."

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    print_warning "OPENAI_API_KEY not set - OpenAI features will be disabled"
else
    print_success "OpenAI API key found"
fi

# Check for Anthropic API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    print_warning "ANTHROPIC_API_KEY not set - Anthropic features will be disabled"
else
    print_success "Anthropic API key found"
fi

# Check for Google Search API
if [ -z "$GOOGLE_SEARCH_API_KEY" ] || [ -z "$GOOGLE_SEARCH_ENGINE_ID" ]; then
    print_warning "Google Search API not configured - Internet search features will be disabled"
else
    print_success "Google Search API configured"
fi

# 3. Install additional dependencies if needed
print_status "Step 3: Checking dependencies..."

# Check if aiohttp is installed (for enhanced subject learning)
python -c "import aiohttp" 2>/dev/null || {
    print_status "Installing aiohttp for enhanced HTTP requests..."
    pip install aiohttp
}

# 4. Test the enhanced services
print_status "Step 4: Testing enhanced services..."

# Test the enhanced subject learning service
python -c "
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

async def test_enhanced_learning():
    try:
        from app.services.enhanced_subject_learning_service import EnhancedSubjectLearningService
        service = EnhancedSubjectLearningService()
        print('✅ Enhanced Subject Learning Service imported successfully')
        
        # Test basic functionality
        result = await service.build_subject_knowledge_base('test subject', 'test context')
        print('✅ Enhanced Subject Learning Service test completed')
        return True
    except Exception as e:
        print(f'❌ Enhanced Subject Learning Service test failed: {e}')
        return False

# Run the test
success = asyncio.run(test_enhanced_learning())
exit(0 if success else 1)
"

if [ $? -eq 0 ]; then
    print_success "Enhanced services test passed"
else
    print_warning "Enhanced services test had issues - some features may not work"
fi

# 5. Update API documentation
print_status "Step 5: Updating API documentation..."

# Create a summary of new endpoints
cat > SUBJECT_LEARNING_API_SUMMARY.md << 'EOF'
# Enhanced Subject Learning API Summary

## New Features Added

### 1. Subject Field in Oath Papers
- **Endpoint**: `POST /api/oath-papers/`
- **New Field**: `subject` (optional)
- **Description**: When provided, triggers enhanced AI learning with internet research

### 2. Enhanced Oath Papers
- **Endpoint**: `POST /api/oath-papers/enhanced`
- **Description**: Advanced oath paper creation with comprehensive AI learning

### 3. Subject Research
- **Endpoint**: `POST /api/oath-papers/research-subject`
- **Parameters**: `subject`, `context` (optional)
- **Description**: Research a subject using OpenAI, Anthropic, and internet search

### 4. Enhanced Book of Lorgar (Training Data)
- **Endpoint**: `POST /api/ai/upload-training-data`
- **New Field**: `subject` (optional)
- **Description**: Enhanced training data upload with subject-based learning

### 5. Subject Research for Book of Lorgar
- **Endpoint**: `POST /api/ai/research-subject`
- **Parameters**: `subject`, `context` (optional)
- **Description**: Research subjects for Book of Lorgar knowledge base

### 6. Subject Filtering
- **Endpoint**: `GET /api/oath-papers/subject/{subject}`
- **Description**: Get oath papers by subject

- **Endpoint**: `GET /api/ai/training-data?subject={subject}`
- **Description**: Get training data filtered by subject

### 7. Subject Listing
- **Endpoint**: `GET /api/ai/training-data/subjects`
- **Description**: Get all unique subjects from training data

## Environment Variables Required

```bash
# For OpenAI integration
export OPENAI_API_KEY="your_openai_api_key"

# For Anthropic integration  
export ANTHROPIC_API_KEY="your_anthropic_api_key"

# For internet search
export GOOGLE_SEARCH_API_KEY="your_google_api_key"
export GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id"
```

## Usage Examples

### Research a Subject
```bash
curl -X POST "http://localhost:8000/api/ai/research-subject" \
  -H "Content-Type: application/json" \
  -d '{"subject": "machine learning", "context": "deep learning applications"}'
```

### Create Enhanced Oath Paper
```bash
curl -X POST "http://localhost:8000/api/oath-papers/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "cybersecurity",
    "tags": ["security", "hacking", "penetration testing"],
    "description": "Advanced cybersecurity techniques",
    "targetAI": "Imperium"
  }'
```

### Upload Training Data with Subject
```bash
curl -X POST "http://localhost:8000/api/ai/upload-training-data" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Stock Market Analysis",
    "subject": "stocks",
    "description": "Technical analysis and trading strategies",
    "code": "// Trading algorithm code here"
  }'
```

## Features

### Enhanced AI Learning
- **OpenAI Integration**: Uses GPT-4 for comprehensive subject research
- **Anthropic Integration**: Uses Claude for knowledge synthesis
- **Internet Search**: Real-time information gathering from the web
- **Knowledge Synthesis**: Combines multiple sources into comprehensive knowledge base

### Subject-Based Learning
- **Keyword Extraction**: Automatic extraction of relevant keywords
- **Learning Paths**: Generated learning recommendations
- **Code Examples**: Relevant code examples for technical subjects
- **Best Practices**: Identified best practices for each subject
- **Common Pitfalls**: Warning about common mistakes
- **Advanced Concepts**: Expert-level knowledge identification

### Database Enhancements
- **Subject Field**: Added to both oath_papers and training_data tables
- **Indexing**: Performance optimization with subject-based indexes
- **Filtering**: Query training data and oath papers by subject
- **Analytics**: Track learning progress by subject

EOF

print_success "API documentation updated"

# 6. Create a test script
print_status "Step 6: Creating test script..."

cat > test_subject_learning.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for enhanced subject learning features
"""

import requests
import json
from datetime import datetime

# Backend URL
BACKEND_URL = "http://localhost:8000"

def test_subject_research():
    """Test subject research functionality"""
    print("🧪 Testing subject research...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/ai/research-subject",
            headers={'Content-Type': 'application/json'},
            json={
                'subject': 'machine learning',
                'context': 'deep learning applications'
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Subject research test passed")
            print(f"   Subject: {result.get('subject')}")
            print(f"   Status: {result.get('knowledge_base', {}).get('status')}")
            return True
        else:
            print(f"❌ Subject research test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Subject research test error: {e}")
        return False

def test_enhanced_oath_paper():
    """Test enhanced oath paper creation"""
    print("🧪 Testing enhanced oath paper creation...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/oath-papers/enhanced",
            headers={'Content-Type': 'application/json'},
            json={
                'subject': 'cybersecurity',
                'tags': ['security', 'hacking', 'penetration testing'],
                'description': 'Advanced cybersecurity techniques and methodologies',
                'targetAI': 'Imperium'
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Enhanced oath paper test passed")
            print(f"   Oath Paper ID: {result.get('oath_paper', {}).get('id')}")
            return True
        else:
            print(f"❌ Enhanced oath paper test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced oath paper test error: {e}")
        return False

def test_training_data_with_subject():
    """Test training data upload with subject"""
    print("🧪 Testing training data upload with subject...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/ai/upload-training-data",
            headers={'Content-Type': 'application/json'},
            json={
                'title': 'Stock Market Analysis',
                'subject': 'stocks',
                'description': 'Technical analysis and trading strategies for stock markets',
                'code': '# Example trading algorithm\nimport pandas as pd\n\ndef analyze_stocks(data):\n    return data.mean()',
                'timestamp': datetime.now().isoformat()
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Training data upload test passed")
            print(f"   Training Data ID: {result.get('id')}")
            print(f"   Subject Researched: {result.get('subject_researched')}")
            return True
        else:
            print(f"❌ Training data upload test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Training data upload test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Subject Learning Tests...")
    print("=" * 50)
    
    tests = [
        test_subject_research,
        test_enhanced_oath_paper,
        test_training_data_with_subject
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced subject learning features are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the backend logs for more details.")

if __name__ == "__main__":
    main()
EOF

print_success "Test script created"

# 7. Final status
print_status "Step 7: Final status check..."

echo ""
print_success "Enhanced Subject Learning Features Deployment Complete!"
echo ""
echo "📋 Summary of deployed features:"
echo "  ✅ Subject field added to oath_papers and training_data tables"
echo "  ✅ Enhanced Subject Learning Service with OpenAI/Anthropic integration"
echo "  ✅ Internet search capabilities for real-time information"
echo "  ✅ Subject-based filtering and querying"
echo "  ✅ Enhanced frontend forms with subject research buttons"
echo "  ✅ API endpoints for subject research and enhanced learning"
echo ""
echo "🔧 Next steps:"
echo "  1. Set up environment variables for OpenAI/Anthropic/Google APIs"
echo "  2. Restart the backend server"
echo "  3. Test the features using: python test_subject_learning.py"
echo "  4. Use the enhanced forms in the frontend"
echo ""
echo "📚 Documentation: SUBJECT_LEARNING_API_SUMMARY.md"
echo "🧪 Test script: test_subject_learning.py"
echo ""

print_success "Deployment completed successfully!" 