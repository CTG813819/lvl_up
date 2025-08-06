#!/bin/bash

echo "Applying simple fix for indentation error..."

# Stop the service
sudo systemctl stop ai-backend-python

# Create a backup
sudo cp /home/ubuntu/ai-backend-python/app/routers/proposals.py /home/ubuntu/ai-backend-python/app/routers/proposals.py.backup

# Apply a simpler fix - just remove the problematic lines and add them back correctly
echo "Fixing main proposals.py..."
sudo sed -i '/# Deduplication: check for existing proposal with same code_hash or semantic_hash/,/logger.info("Converting proposal to dict for ML analysis")/d' /home/ubuntu/ai-backend-python/app/routers/proposals.py

# Add the correct duplicate check section
sudo sed -i '/# Convert to dict for ML analysis/i\
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
        ' /home/ubuntu/ai-backend-python/app/routers/proposals.py

# Test the syntax
echo "Testing syntax..."
if python3 -m py_compile /home/ubuntu/ai-backend-python/app/routers/proposals.py; then
    echo "✅ Syntax check passed"
else
    echo "❌ Syntax error - restoring backup"
    sudo cp /home/ubuntu/ai-backend-python/app/routers/proposals.py.backup /home/ubuntu/ai-backend-python/app/routers/proposals.py
    exit 1
fi

# Start the service
echo "Starting service..."
sudo systemctl start ai-backend-python

# Check status
echo "Service status:"
sudo systemctl status ai-backend-python --no-pager

echo "Fix complete!" 