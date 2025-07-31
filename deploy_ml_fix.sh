#!/bin/bash

echo "Deploying ML service fix..."

# Stop the service
echo "Stopping ai-backend-python service..."
sudo systemctl stop ai-backend-python

# Create a backup
sudo cp /home/ubuntu/ai-backend-python/app/services/ml_service.py /home/ubuntu/ai-backend-python/app/services/ml_service.py.backup

# Apply the ML service fix by replacing the problematic methods
echo "Applying ML service fix..."

# Fix extract_features method
sudo sed -i '/async def extract_features(self, proposal_data) -> Dict\[str, Any\]:/,/return features/c\
    async def extract_features(self, proposal_data) -> Dict[str, Any]:\
        """Extract features from a proposal for ML analysis"""\
        features = {}\
        \
        # Handle both dictionary and object inputs\
        if isinstance(proposal_data, dict):\
            code_before = proposal_data.get("code_before", "") or ""\
            code_after = proposal_data.get("code_after", "") or ""\
            file_path = proposal_data.get("file_path", "") or ""\
            ai_type = proposal_data.get("ai_type", "Imperium") or "Imperium"\
            ai_reasoning = proposal_data.get("ai_reasoning", "") or ""\
            improvement_type = proposal_data.get("improvement_type", "") or ""\
        else:\
            # Handle Pydantic model object\
            code_before = proposal_data.code_before or ""\
            code_after = proposal_data.code_after or ""\
            file_path = proposal_data.file_path or ""\
            ai_type = proposal_data.ai_type or "Imperium"\
            ai_reasoning = proposal_data.ai_reasoning or ""\
            improvement_type = proposal_data.improvement_type or ""\
        \
        features["code_length_before"] = len(code_before)\
        features["code_length_after"] = len(code_after)\
        features["code_length_ratio"] = len(code_after) / max(len(code_before), 1)\
        \
        # File type features\
        file_ext = file_path.split(".")[-1] if "." in file_path else "unknown"\
        features["file_extension"] = file_ext\
        \
        # AI type encoding\
        ai_type_encoding = {"Imperium": 0, "Guardian": 1, "Sandbox": 2}\
        features["ai_type_encoded"] = ai_type_encoding.get(ai_type, 0)\
        \
        # Text analysis features\
        if ai_reasoning:\
            blob = TextBlob(ai_reasoning)\
            features["reasoning_sentiment"] = blob.sentiment.polarity\
            features["reasoning_subjectivity"] = blob.sentiment.subjectivity\
            features["reasoning_length"] = len(ai_reasoning)\
        \
        # Code complexity features\
        features["lines_added"] = code_after.count("\\n") - code_before.count("\\n")\
        features["characters_added"] = len(code_after) - len(code_before)\
        \
        # Improvement type encoding\
        improvement_types = ["performance", "readability", "security", "bug-fix", "refactor", "feature", "system"]\
        features["improvement_type_encoded"] = improvement_types.index(improvement_type) if improvement_type in improvement_types else -1\
        \
        return features' /home/ubuntu/ai-backend-python/app/services/ml_service.py

# Fix _extract_text_features method
sudo sed -i '/async def _extract_text_features(self, proposal_data) -> Dict\[str, Any\]:/,/return features/c\
    async def _extract_text_features(self, proposal_data) -> Dict[str, Any]:\
        """Extract text-based features"""\
        features = {}\
        \
        # Handle both dictionary and object inputs\
        if isinstance(proposal_data, dict):\
            ai_reasoning = proposal_data.get("ai_reasoning", "") or ""\
        else:\
            ai_reasoning = proposal_data.ai_reasoning or ""\
        \
        if ai_reasoning:\
            # Tokenize and analyze reasoning\
            tokens = word_tokenize(ai_reasoning.lower())\
            \
            # Remove stopwords\
            stop_words = set(stopwords.words("english"))\
            tokens = [token for token in tokens if token.isalnum() and token not in stop_words]\
            \
            features["reasoning_token_count"] = len(tokens)\
            features["reasoning_unique_tokens"] = len(set(tokens))\
            features["reasoning_lexical_diversity"] = len(set(tokens)) / max(len(tokens), 1)\
        \
        return features' /home/ubuntu/ai-backend-python/app/services/ml_service.py

# Fix _extract_code_features method
sudo sed -i '/async def _extract_code_features(self, proposal_data) -> Dict\[str, Any\]:/,/return features/c\
    async def _extract_code_features(self, proposal_data) -> Dict[str, Any]:\
        """Extract code-based features"""\
        features = {}\
        \
        # Handle both dictionary and object inputs\
        if isinstance(proposal_data, dict):\
            code_after = proposal_data.get("code_after", "") or ""\
            code_before = proposal_data.get("code_before", "") or ""\
            file_path = proposal_data.get("file_path", "") or ""\
        else:\
            code_after = proposal_data.code_after or ""\
            code_before = proposal_data.code_before or ""\
            file_path = proposal_data.file_path or ""\
        \
        # Code complexity metrics\
        features["code_complexity"] = await self._calculate_code_complexity(code_after)\
        features["code_similarity"] = await self._calculate_code_similarity(code_before, code_after)\
        \
        # Language-specific features\
        if file_path.endswith(".dart"):\
            features["dart_specific"] = await self._extract_dart_features(code_after)\
        \
        return features' /home/ubuntu/ai-backend-python/app/services/ml_service.py

# Test the syntax
echo "Testing syntax..."
if python3 -m py_compile /home/ubuntu/ai-backend-python/app/services/ml_service.py; then
    echo "✅ ML service syntax check passed"
else
    echo "❌ ML service syntax error - restoring backup"
    sudo cp /home/ubuntu/ai-backend-python/app/services/ml_service.py.backup /home/ubuntu/ai-backend-python/app/services/ml_service.py
    exit 1
fi

# Start the service
echo "Starting service..."
sudo systemctl start ai-backend-python

# Check status
echo "Service status:"
sudo systemctl status ai-backend-python --no-pager

echo "ML service fix complete!" 