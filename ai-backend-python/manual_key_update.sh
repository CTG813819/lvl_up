#!/bin/bash

echo "🔑 Manual OpenAI API Key Update"
echo "================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    exit 1
fi

echo "📝 Current .env file contents:"
echo "-------------------------------"
grep "OPENAI_API_KEY" .env || echo "OPENAI_API_KEY not found in .env"

echo ""
echo "📋 Instructions:"
echo "1. Open the .env file: nano .env"
echo "2. Find the line: OPENAI_API_KEY=sk-proj-..."
echo "3. Replace the entire line with: OPENAI_API_KEY=your_new_key_here"
echo "4. Save the file (Ctrl+X, Y, Enter)"
echo "5. Run: python test_simple_openai.py"
echo ""
echo "🔗 Get your API key from: https://platform.openai.com/account/api-keys"
echo ""
echo "Press Enter when you've updated the .env file..."
read

echo "🧪 Testing the updated API key..."
python test_simple_openai.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! OpenAI API key is working correctly."
    echo "The backend should now be able to use OpenAI as a fallback."
else
    echo ""
    echo "❌ API key test failed. Please check your key and try again."
fi 