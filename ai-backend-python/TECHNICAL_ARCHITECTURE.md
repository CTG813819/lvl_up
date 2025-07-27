# Technical Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Backend System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   FastAPI App   │    │   Background    │    │   Database   │ │
│  │   (main.py)     │    │   Services      │    │  PostgreSQL  │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                       │     │
│           ▼                       ▼                       ▼     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    AI Services Layer                        │ │
│  │                                                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │ │
│  │  │   Imperium  │ │   Guardian  │ │   Sandbox   │ │ Conquest│ │ │
│  │  │     AI      │ │     AI      │ │     AI      │ │    AI   │ │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │ │
│  │                                                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │ │
│  │  │    AI       │ │   SCKIPIT   │ │   ML        │            │ │
│  │  │  Learning   │ │  Service    │ │  Service    │            │ │
│  │  │  Service    │ │             │ │             │            │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘            │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    API Layer                                │ │
│  │                                                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │ │
│  │  │  Proposals  │ │   Learning  │ │  Analytics  │ │ Agents  │ │ │
│  │  │   Router    │ │   Router    │ │   Router    │ │ Router  │ │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │ │
│  │                                                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │ │
│  │  │   Guardian  │ │   Conquest  │ │  Imperium   │            │ │
│  │  │   Router    │ │   Router    │ │   Router    │            │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘            │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  External Integrations                      │ │
│  │                                                             │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │ │
│  │  │   GitHub    │ │  Anthropic  │ │   OpenAI    │ │ Flutter │ │ │
│  │  │             │ │   Claude    │ │             │ │         │ │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   GitHub    │───▶│  AI Agent   │───▶│  Proposal   │
│ Repository  │    │   Service   │    │ Generation  │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   ML        │◀───│  AI         │◀───│  Testing    │
│  Models     │    │  Learning   │    │  Service    │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Database   │◀───│  Proposal   │◀───│  Approval   │
│ PostgreSQL  │    │  Storage    │    │  Process    │
└─────────────┘    └─────────────┘    └─────────────┘
```

## API Reference

### Base URL
```
http://localhost:8000
```

### Authentication
Most endpoints require API key authentication via header:
```
Authorization: Bearer <api_key>
```

### Core Endpoints

#### 1. Health & Status

**GET /health**
- Returns system health status
- Response: `{"status": "ok", "timestamp": "...", "version": "2.0.0"}`

**GET /api/health**
- API health check
- Response: `{"status": "ok", "message": "AI Learning Backend is running"}`

**GET /debug**
- System debug information
- Returns proposal statistics and recent activity

#### 2. Proposals Management

**POST /proposals/**
- Create a new proposal
- Body: `ProposalCreate` model
- Response: `ProposalResponse`

**GET /proposals/**
- List proposals with filtering
- Query params: `ai_type`, `status`, `limit`, `skip`
- Response: `List[ProposalResponse]`

**GET /proposals/{proposal_id}**
- Get specific proposal
- Response: `ProposalResponse`

**POST /proposals/{proposal_id}/accept**
- Accept a proposal
- Response: Success/error message

**POST /proposals/{proposal_id}/reject**
- Reject a proposal
- Response: Success/error message

**POST /proposals/{proposal_id}/apply**
- Apply a proposal to codebase
- Response: Application results

**POST /proposals/{proposal_id}/auto-apply**
- Automatically apply proposal
- Response: Auto-application results

#### 3. AI Agents

**GET /agents/status**
- Get status of all AI agents
- Response: Agent status information

**POST /agents/{agent_type}/run**
- Manually trigger agent execution
- Response: Agent execution results

**GET /agents/{agent_type}/metrics**
- Get agent performance metrics
- Response: Agent metrics data

#### 4. Learning Analytics

**GET /learning/insights**
- Get learning insights
- Query params: `ai_type`
- Response: Learning insights data

**GET /learning/stats**
- Get learning statistics
- Response: Learning statistics

**POST /learning/trigger**
- Trigger learning process
- Body: Learning parameters
- Response: Learning results

#### 5. Analytics

**GET /analytics/overview**
- System overview analytics
- Response: System analytics data

**GET /analytics/proposals**
- Proposal analytics
- Response: Proposal analytics

**GET /analytics/agents**
- Agent performance analytics
- Response: Agent analytics

#### 6. Guardian AI

**POST /guardian/analyze**
- Security analysis
- Body: Code content and file path
- Response: Security analysis results

**GET /guardian/suggestions**
- Get security suggestions
- Response: Security suggestions list

**POST /guardian/suggestions/{suggestion_id}/approve**
- Approve security suggestion
- Response: Approval results

#### 7. Conquest AI

**POST /conquest/create-app**
- Create new Flutter application
- Body: App creation parameters
- Response: App creation results

**GET /conquest/deployments**
- List app deployments
- Response: Deployment list

**GET /conquest/deployments/{deployment_id}**
- Get deployment status
- Response: Deployment status

#### 8. Imperium AI

**POST /imperium/optimize**
- Optimize code
- Body: Code content and optimization parameters
- Response: Optimization results

**POST /imperium/create-extension**
- Create code extension
- Body: Extension parameters
- Response: Extension creation results

## Data Models

### Proposal Model
```python
class ProposalCreate(BaseModel):
    ai_type: str
    file_path: str
    code_before: str
    code_after: str
    description: Optional[str] = None

class ProposalResponse(BaseModel):
    id: str
    ai_type: str
    file_path: str
    status: str
    created_at: datetime
    # ... other fields
```

### Learning Model
```python
class LearningCreate(BaseModel):
    ai_type: str
    learning_type: str
    learning_data: Optional[Dict] = None

class LearningResponse(BaseModel):
    id: str
    ai_type: str
    learning_type: str
    status: str
    created_at: datetime
```

### Agent Metrics Model
```python
class AgentMetrics(BaseModel):
    agent_id: str
    agent_type: str
    learning_score: float
    success_rate: float
    level: int
    xp: int
    # ... other fields
```

## Database Schema

### Core Tables

#### proposals
- `id` (UUID, Primary Key)
- `ai_type` (String, Indexed)
- `file_path` (String, Indexed)
- `code_before` (Text)
- `code_after` (Text)
- `status` (String, Indexed)
- `created_at` (DateTime, Indexed)
- `updated_at` (DateTime)

#### learning
- `id` (UUID, Primary Key)
- `proposal_id` (UUID, Foreign Key)
- `ai_type` (String, Indexed)
- `learning_type` (String)
- `learning_data` (JSON)
- `created_at` (DateTime)

#### agent_metrics
- `id` (UUID, Primary Key)
- `agent_id` (String, Unique, Indexed)
- `agent_type` (String, Indexed)
- `learning_score` (Float)
- `level` (Integer)
- `xp` (Integer)
- `created_at` (DateTime)

#### guardian_suggestions
- `id` (UUID, Primary Key)
- `issue_type` (String, Indexed)
- `severity` (String, Indexed)
- `status` (String, Indexed)
- `created_at` (DateTime)

## Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# AI Services
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# GitHub
GITHUB_TOKEN=your_github_token

# Flutter
FLUTTER_PATH=/path/to/flutter

# ML Models
ML_MODEL_PATH=/path/to/models

# Security
SECRET_KEY=your_secret_key
```

### Service Configuration
```python
class Settings(BaseSettings):
    # Database
    database_url: str
    
    # AI Services
    anthropic_api_key: str
    openai_api_key: str
    
    # GitHub
    github_token: str
    
    # Flutter
    flutter_path: str = "/home/ubuntu/flutter/bin/flutter"
    
    # ML Models
    ml_model_path: str = "models"
    
    # Security
    secret_key: str
    
    class Config:
        env_file = ".env"
```

## Deployment Architecture

### Production Setup
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │───▶│  FastAPI App 1  │    │  FastAPI App 2  │
│   (Nginx)       │    │   (Port 8000)   │    │   (Port 8001)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────────────────────────┐
                       │         PostgreSQL Cluster          │
                       │         (Primary + Replicas)        │
                       └─────────────────────────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Redis Cache   │
                       │   (Optional)    │
                       └─────────────────┘
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-backend
  template:
    metadata:
      labels:
        app: ai-backend
    spec:
      containers:
      - name: ai-backend
        image: ai-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

This technical architecture provides a scalable, maintainable foundation for the AI Backend system with clear separation of concerns and robust API design. 