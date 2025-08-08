#!/bin/bash
cd /home/ubuntu/ai-backend-python

# Create experiments directory
mkdir -p experiments
cd experiments

# Initialize git repository for experiments
git init
git config user.name "AI Backend"
git config user.email "ai-backend@lvl-up.com"

# Create initial experiment structure
mkdir -p ml_experiments
mkdir -p app_experiments
mkdir -p extension_experiments

# Create README
cat > README.md << 'EOF'
# AI Backend Experiments

This repository contains experiments for:
- Machine Learning experiments
- App creation experiments  
- Extension development experiments

## Structure
- ml_experiments/: Machine learning experiments
- app_experiments/: App creation experiments
- extension_experiments/: Extension development experiments

## Usage
Experiments are automatically created and managed by the AI backend.
EOF

# Add and commit
git add .
git commit -m "Initial experiment repository setup"

echo "Experiment repository created successfully"
