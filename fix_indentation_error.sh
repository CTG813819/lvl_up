#!/bin/bash

echo "Fixing indentation error in proposals.py..."

# Stop the service
echo "Stopping ai-backend-python service..."
sudo systemctl stop ai-backend-python

# Check the current state of the file
echo "Checking current file state..."
sudo grep -n "Checking for duplicates" /home/ubuntu/ai-backend-python/app/routers/proposals.py

# Fix the indentation by replacing the problematic section
echo "Fixing indentation..."
sudo sed -i '/# Deduplication: check for existing proposal with same code_hash or semantic_hash/,/logger.info("Converting proposal to dict for ML analysis")/c\
        # Deduplication: check for existing proposal with same code_hash or semantic_hash\
        logger.info("Checking for duplicates")\
        \
        # Only check for duplicates if we have actual hash values\
        if proposal.code_hash is not None or proposal.semantic_hash is not None:\
            duplicate_query = select(Proposal).where(\
                (Proposal.code_hash == proposal.code_hash) | (Proposal.semantic_hash == proposal.semantic_hash),\
                Proposal.status != "rejected"\
            )\
            duplicate_result = await db.execute(duplicate_query)\
            duplicates = duplicate_result.scalars().all()\
            if duplicates:\
                # If there are multiple duplicates, just use the first one\
                duplicate = duplicates[0]\
                raise HTTPException(status_code=409, detail="Duplicate proposal already exists.")\
        else:\
            logger.info("Skipping duplicate check - no hash values provided")\
        \
        # Convert to dict for ML analysis' /home/ubuntu/ai-backend-python/app/routers/proposals.py

# Also fix the guardian deployment version
echo "Fixing guardian deployment version..."
sudo sed -i '/# Deduplication: check for existing proposal with same code_hash or semantic_hash/,/proposal_dict = proposal.dict()/c\
        # Deduplication: check for existing proposal with same code_hash or semantic_hash\
        # Only check for duplicates if we have actual hash values\
        if proposal.code_hash is not None or proposal.semantic_hash is not None:\
            duplicate_query = select(Proposal).where(\
                (Proposal.code_hash == proposal.code_hash) | (Proposal.semantic_hash == proposal.semantic_hash),\
                Proposal.status != "rejected"\
            )\
            duplicate_result = await db.execute(duplicate_query)\
            duplicates = duplicate_result.scalars().all()\
            if duplicates:\
                # If there are multiple duplicates, just use the first one\
                duplicate = duplicates[0]\
                raise HTTPException(status_code=409, detail="Duplicate proposal already exists.")\
        else:\
            logger.info("Skipping duplicate check - no hash values provided")\
        \
        # Convert to dict for ML analysis\
        proposal_dict = proposal.dict()' /home/ubuntu/ai-backend-python/guardian_deployment_20250607_175440/app/routers/proposals.py

# Verify the fix
echo "Verifying fix..."
if python3 -m py_compile /home/ubuntu/ai-backend-python/app/routers/proposals.py; then
    echo "✅ Syntax check passed"
else
    echo "❌ Syntax error still exists"
    exit 1
fi

# Start the service
echo "Starting ai-backend-python service..."
sudo systemctl start ai-backend-python

# Check service status
echo "Checking service status..."
sudo systemctl status ai-backend-python --no-pager

echo "Indentation fix complete!" 