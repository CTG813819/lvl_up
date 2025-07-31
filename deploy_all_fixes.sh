#!/bin/bash

echo "Deploying all three fixes to EC2 instance..."

# Stop the service
echo "Stopping ai-backend-python service..."
sudo systemctl stop ai-backend-python

# Apply the cleanup fix to the proposals.py file
echo "Applying cleanup fix..."
sudo sed -i 's/proposal.user_feedback = "Automatically expired due to age"/proposal.user_feedback = "expired"/g' /home/ubuntu/ai-backend-python/app/routers/proposals.py

# Apply the duplicate check fix
echo "Applying duplicate check fix..."
sudo sed -i 's/duplicate = duplicate_result.scalar_one_or_none()/duplicates = duplicate_result.scalars().all()\n        if duplicates:\n            # If there are multiple duplicates, just use the first one\n            duplicate = duplicates[0]/g' /home/ubuntu/ai-backend-python/app/routers/proposals.py

# Apply the hash value check fix
echo "Applying hash value check fix..."
sudo sed -i '/# Deduplication: check for existing proposal with same code_hash or semantic_hash/a\        # Only check for duplicates if we have actual hash values\n        if proposal.code_hash is not None or proposal.semantic_hash is not None:' /home/ubuntu/ai-backend-python/app/routers/proposals.py
sudo sed -i '/raise HTTPException(status_code=409, detail="Duplicate proposal already exists.")/a\        else:\n            logger.info("Skipping duplicate check - no hash values provided")' /home/ubuntu/ai-backend-python/app/routers/proposals.py

# Also fix the guardian deployment version
echo "Applying fixes to guardian deployment version..."
sudo sed -i 's/proposal.user_feedback = "Automatically expired due to age"/proposal.user_feedback = "expired"/g' /home/ubuntu/ai-backend-python/guardian_deployment_20250607_175440/app/routers/proposals.py
sudo sed -i 's/duplicate = duplicate_result.scalar_one_or_none()/duplicates = duplicate_result.scalars().all()\n        if duplicates:\n            # If there are multiple duplicates, just use the first one\n            duplicate = duplicates[0]/g' /home/ubuntu/ai-backend-python/guardian_deployment_20250607_175440/app/routers/proposals.py
sudo sed -i '/# Deduplication: check for existing proposal with same code_hash or semantic_hash/a\        # Only check for duplicates if we have actual hash values\n        if proposal.code_hash is not None or proposal.semantic_hash is not None:' /home/ubuntu/ai-backend-python/guardian_deployment_20250607_175440/app/routers/proposals.py
sudo sed -i '/raise HTTPException(status_code=409, detail="Duplicate proposal already exists.")/a\        else:\n            logger.info("Skipping duplicate check - no hash values provided")' /home/ubuntu/ai-backend-python/guardian_deployment_20250607_175440/app/routers/proposals.py

# Verify the fixes were applied
echo "Verifying fixes..."
if grep -q 'proposal.user_feedback = "expired"' /home/ubuntu/ai-backend-python/app/routers/proposals.py; then
    echo "✅ Cleanup fix applied successfully"
else
    echo "❌ Cleanup fix not found - manual intervention required"
    exit 1
fi

if grep -q 'duplicates = duplicate_result.scalars().all()' /home/ubuntu/ai-backend-python/app/routers/proposals.py; then
    echo "✅ Duplicate check fix applied successfully"
else
    echo "❌ Duplicate check fix not found - manual intervention required"
    exit 1
fi

if grep -q 'Skipping duplicate check - no hash values provided' /home/ubuntu/ai-backend-python/app/routers/proposals.py; then
    echo "✅ Hash value check fix applied successfully"
else
    echo "❌ Hash value check fix not found - manual intervention required"
    exit 1
fi

# Start the service
echo "Starting ai-backend-python service..."
sudo systemctl start ai-backend-python

# Check service status
echo "Checking service status..."
sudo systemctl status ai-backend-python --no-pager

echo "Deployment complete! The service should now handle all three issues without errors." 