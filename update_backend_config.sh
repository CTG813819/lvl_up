
# Update backend configuration for local experiments
cd /home/ubuntu/ai-backend-python

# Create .env file with experiment settings
cat >> .env << 'EOF'

# Experiment Configuration
EXPERIMENT_REPO_PATH=/home/ubuntu/ai-backend-python/experiments
LOCAL_EXPERIMENTS_ENABLED=true
GITHUB_INTEGRATION_ENABLED=false
AUTO_COMMIT_EXPERIMENTS=true

# Git Configuration
GIT_USER_NAME=AI Backend
GIT_USER_EMAIL=ai-backend@lvl-up.com
GIT_DEFAULT_BRANCH=main

# Repository Settings
REPO_PATH=/home/ubuntu/ai-backend-python
EXPERIMENT_BASE_PATH=/home/ubuntu/ai-backend-python/experiments
EOF

echo "Backend configuration updated"
