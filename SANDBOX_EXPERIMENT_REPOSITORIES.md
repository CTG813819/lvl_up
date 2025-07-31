# Sandbox Agent Experiment Repositories

## Overview

The Sandbox agent can now create its own repositories for experiments, providing a dedicated space for AI experimentation and testing without affecting the main codebase.

## Features

### 🏗️ Automatic Repository Creation
- **Self-Contained**: Sandbox agent creates dedicated repositories for experiments
- **GitHub Integration**: Automatically creates private GitHub repositories when token is available
- **Local Fallback**: Creates local repositories when GitHub is not configured
- **Unique Naming**: Uses timestamps to ensure unique repository names

### 📁 Repository Structure
```
ai-sandbox-experiments-YYYYMMDD_HHMMSS/
├── README.md                    # Repository documentation
├── experiments/                 # Individual experiment directories
├── tests/                      # Test files and results
├── results/                    # Experiment results and metrics
└── logs/                       # Experiment logs
```

### 🔬 Experiment Tracking
- **Metadata Storage**: Each experiment includes detailed metadata
- **Test Results**: Comprehensive test execution tracking
- **Code Analysis**: AST-based code complexity analysis
- **Success Metrics**: Detailed success/failure tracking

## API Endpoints

### Create Experiment Repository
```http
POST /api/sandbox/create-experiment-repository
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "repository_id": "uuid",
    "repository_url": "https://github.com/user/ai-sandbox-experiments-20250107_175440",
    "name": "ai-sandbox-experiments-20250107_175440",
    "message": "Experiment repository created successfully",
    "created_at": "2025-01-07T17:54:40Z"
  }
}
```

### List Experiment Repositories
```http
GET /api/sandbox/experiment-repositories
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "repositories": [
      {
        "id": "uuid",
        "name": "ai-sandbox-experiments-20250107_175440",
        "url": "https://github.com/user/ai-sandbox-experiments-20250107_175440",
        "description": "AI Sandbox Experiments Repository",
        "agent_type": "Sandbox",
        "status": "active",
        "repository_type": "github",
        "is_private": true,
        "experiments_count": 15,
        "total_commits": 25,
        "last_activity": "2025-01-07T18:30:00Z",
        "created_at": "2025-01-07T17:54:40Z",
        "created_by": "Sandbox Agent"
      }
    ],
    "total_repositories": 1
  }
}
```

### Get Experiment Results
```http
GET /api/sandbox/experiment-results/{experiment_id}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "experiment_id": "uuid",
    "commit_sha": "abc12345",
    "commit_message": "Add new feature",
    "status": "completed",
    "success": true,
    "timestamp": "2025-01-07T17:54:40Z",
    "test_results": [
      {
        "type": "pytest",
        "success": true,
        "output": "3 passed, 0 failed"
      }
    ],
    "analysis_results": {
      "files_analyzed": 5,
      "total_lines": 250,
      "functions_found": 12,
      "classes_found": 3,
      "complexity_score": 2.5,
      "potential_issues": []
    }
  }
}
```

### Run Sandbox Experiment
```http
POST /api/sandbox/run-sandbox-experiment
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "success",
    "experiments_run": 3,
    "successful_experiments": 2,
    "tests_run": 5,
    "proposals_created": 1,
    "agent": "Sandbox"
  },
  "timestamp": "2025-01-07T17:54:40Z"
}
```

## Database Schema

### ExperimentRepository Model
```sql
CREATE TABLE experiment_repositories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    url VARCHAR(500) NOT NULL,
    description TEXT,
    agent_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    repository_type VARCHAR(50) DEFAULT 'github',
    is_private BOOLEAN DEFAULT TRUE,
    experiments_count INTEGER DEFAULT 0,
    total_commits INTEGER DEFAULT 0,
    last_activity TIMESTAMP,
    auto_push_enabled BOOLEAN DEFAULT TRUE,
    branch_name VARCHAR(100) DEFAULT 'main',
    gitignore_template VARCHAR(100),
    license_template VARCHAR(100),
    created_by VARCHAR(100),
    config JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Configuration

### Environment Variables
```bash
# GitHub Configuration (optional)
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_github_username

# Experiment Repository Configuration
EXPERIMENT_REPOSITORY_URL=https://github.com/user/experiments
EXPERIMENT_BRANCH=main
EXPERIMENT_AUTO_PUSH=true
```

## Safety Features

### 🔒 Isolation
- **Private Repositories**: All experiment repositories are created as private by default
- **Temporary Directories**: Experiments run in isolated temporary directories
- **No Main Codebase Impact**: Experiments never affect the main application code

### 🛡️ Error Handling
- **Graceful Degradation**: Falls back to local repositories if GitHub is unavailable
- **Comprehensive Logging**: All operations are logged for debugging
- **Timeout Protection**: All operations have reasonable timeouts

### 📊 Monitoring
- **Experiment Tracking**: All experiments are tracked with metadata
- **Success Metrics**: Detailed success/failure statistics
- **Performance Monitoring**: Execution time and resource usage tracking

## Usage Examples

### Automatic Creation
The Sandbox agent automatically creates experiment repositories when:
1. No main repository is configured
2. Running experiments that need isolation
3. Testing new features or improvements

### Manual Creation
```python
from app.services.ai_agent_service import AIAgentService

ai_agent_service = AIAgentService()
experiment_repo = await ai_agent_service._create_experiment_repository()
```

### Running Experiments
```python
# Run Sandbox agent with experiment repository
result = await ai_agent_service.run_sandbox_agent()
```

## Benefits

1. **🔬 Dedicated Experimentation**: Isolated environment for AI experiments
2. **📈 Scalability**: Multiple experiment repositories for different purposes
3. **🔄 Version Control**: Full Git history for all experiments
4. **📊 Analytics**: Comprehensive tracking and metrics
5. **🛡️ Safety**: No risk to main codebase
6. **🔍 Transparency**: Full visibility into AI experimentation process

## Future Enhancements

- **Multi-Repository Support**: Support for multiple experiment repositories
- **Experiment Templates**: Predefined experiment templates
- **Collaborative Experiments**: Shared experiment repositories
- **Advanced Analytics**: Machine learning on experiment results
- **Integration Testing**: Automated integration with main codebase 