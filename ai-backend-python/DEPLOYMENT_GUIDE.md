# 🚀 AI Backend - Deployment Guide

## System Overview

The AI Backend is a comprehensive system with multiple components running on different ports:

- **Main Server**: Port 8000 - Core API and services
- **Enhanced Adversarial Testing**: Port 8001 - Security and robustness testing  
- **Training Ground**: Port 8002 - AI training scenarios and simulations

## 🔧 Fixed Issues

### ✅ **Major Fixes Completed:**

1. **Unified Application Structure**
   - Consolidated conflicting main.py files into `main_unified.py`
   - Fixed import errors and service initialization
   - Removed app conflicts and duplicate configurations

2. **Learning Cycles Active**
   - Learning cycles running every 30 minutes
   - Custody testing every 20 minutes  
   - Olympic events every 45 minutes
   - Collaborative testing every 90 minutes
   - ML training with scikit-learn integration

3. **Testing Systems Fixed**
   - Custodial testing with fallback mechanisms
   - Olympic AI competitions
   - Collaborative multi-AI testing
   - Enhanced adversarial testing on dedicated port

4. **AI Services Active**
   - Imperium, Guardian, Conquest, Sandbox AIs
   - Project Horus, Olympic AI, Collaborative AI, Custodes AI
   - Auto-apply service and proposal generation
   - GitHub integration and code analysis

## 📋 System Components

### Core AI Services
- **Imperium AI**: Strategic leadership and decision-making
- **Guardian AI**: Security and system protection  
- **Conquest AI**: Competitive optimization and expansion
- **Sandbox AI**: Experimental testing and development

### Specialized Services  
- **Project Horus**: Advanced project management
- **Olympic AI**: Competition and benchmarking
- **Collaborative AI**: Multi-AI coordination
- **Custodes AI**: Quality assurance and testing

### Background Systems
- **Learning Cycles**: Continuous AI improvement
- **Custody Protocol**: Quality gating for AI actions
- **ML Training**: Scikit-learn model updates
- **Proposal Generation**: Automated code improvements

## 🚀 Deployment Steps

### Local Development

1. **Start the system:**
   ```bash
   cd ai-backend-python
   python start_server.py
   ```

2. **Test the system:**
   ```bash
   python test_unified_system.py
   ```

3. **Access endpoints:**
   - Main API: http://localhost:8000
   - Adversarial Testing: http://localhost:8001  
   - Training Ground: http://localhost:8002

### Railway Deployment

1. **Environment Variables:**
   ```env
   RUN_BACKGROUND_JOBS=1
   DATABASE_URL=your_neon_postgres_url
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   ```

2. **Deploy Command:**
   ```bash
   uvicorn main_unified:app --host 0.0.0.0 --port $PORT
   ```

3. **Health Checks:**
   - Main: `/health`
   - API: `/api/health`  
   - Debug: `/debug`

## 🔬 Testing & Monitoring

### Automated Testing
- All AI services have status endpoints
- Background services log activity
- ML models track performance metrics
- Custody protocol validates AI actions

### Key Metrics
- Learning cycle frequency and success
- AI test pass rates
- Proposal generation quality
- System performance and uptime

## 🛡️ Security & Quality

### Custody Protocol
- AIs must pass tests before generating proposals
- Multi-layer fallback testing
- Quality gates for all AI actions

### Enhanced Security
- Adversarial testing on dedicated port
- Security headers and CORS protection  
- Input validation and error handling

## 📊 API Endpoints

### Core Endpoints
- `GET /health` - System health
- `GET /api/health` - API health  
- `GET /debug` - Debug information

### AI Services
- `/api/imperium/*` - Imperium AI
- `/api/guardian/*` - Guardian AI  
- `/api/conquest/*` - Conquest AI
- `/api/sandbox/*` - Sandbox AI

### Specialized Services
- `/api/project-horus/*` - Project Horus
- `/api/olympic-ai/*` - Olympic AI
- `/api/collaborative-ai/*` - Collaborative AI
- `/api/custodes-ai/*` - Custodes AI

### Management
- `/api/proposals/*` - Proposal management
- `/api/learning/*` - Learning insights
- `/api/agents/*` - Agent management
- `/api/custody/*` - Custody protocol

## 🎯 Performance Optimization

### ML Integration
- Scikit-learn models for proposal quality prediction
- Continuous model retraining
- Performance metrics tracking
- Automated feature engineering

### Background Services
- Async processing for all cycles
- Lock mechanisms to prevent conflicts
- Error handling and recovery
- Resource optimization

## 🔄 Maintenance

### Regular Tasks
- Monitor learning cycle logs
- Check ML model performance  
- Review custody test results
- Update AI knowledge bases

### Troubleshooting
- Check `/debug` endpoint for system status
- Review service logs for errors
- Verify database connectivity
- Test AI service endpoints

## 📈 Future Enhancements

### Planned Features
- Enhanced ML model architectures
- Real-time learning adaptation
- Advanced adversarial scenarios
- Multi-environment deployment

### Scalability
- Kubernetes deployment support
- Distributed AI processing
- Advanced caching strategies
- Performance monitoring

---

**System Status**: ✅ Ready for deployment
**Last Updated**: {datetime.now().isoformat()}
**Version**: 2.0.0