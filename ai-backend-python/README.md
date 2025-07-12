# AI Backend with scikit-learn Integration

This is a Python-based AI backend that replaces the original JavaScript backend, featuring advanced machine learning capabilities using scikit-learn.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **scikit-learn Integration**: Advanced machine learning for proposal analysis
- **MongoDB Integration**: Async database operations with motor
- **Natural Language Processing**: Text analysis using NLTK and TextBlob
- **AI Learning System**: Continuous learning from user feedback
- **Proposal Quality Analysis**: ML-powered proposal evaluation
- **Structured Logging**: Comprehensive logging with structlog

## Key ML Capabilities

### Proposal Analysis
- **Quality Scoring**: ML models predict proposal quality
- **Approval Probability**: Predict likelihood of user approval
- **Feature Extraction**: Analyze code complexity, text sentiment, and patterns
- **Recommendations**: Generate improvement suggestions

### Learning System
- **Pattern Recognition**: Identify common mistakes and success patterns
- **Model Training**: Continuous retraining based on feedback
- **Insights Generation**: Provide actionable recommendations
- **Performance Tracking**: Monitor learning effectiveness

## Installation

1. **Clone the repository**
   ```bash
   cd ai-backend-python
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# Database
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=ai_backend

# Server
PORT=4000
HOST=0.0.0.0
DEBUG=false

# AI Services
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# GitHub
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your_repo

# ML Settings
ML_MODEL_PATH=./models
ENABLE_ML_LEARNING=true
ML_CONFIDENCE_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Running the Application

### Development Mode
```bash
python start.py
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 4000
```

### Using Docker
```bash
docker build -t ai-backend-python .
docker run -p 4000:4000 ai-backend-python
```

## API Endpoints

### Health Checks
- `GET /health` - Basic health check
- `GET /api/health` - API health check
- `GET /debug` - Debug information

### Proposals
- `POST /api/proposals/` - Create new proposal with ML analysis
- `GET /api/proposals/` - Get proposals with filtering
- `GET /api/proposals/{id}` - Get specific proposal
- `PUT /api/proposals/{id}` - Update proposal and trigger learning
- `DELETE /api/proposals/{id}` - Delete proposal
- `GET /api/proposals/stats/summary` - Get proposal statistics
- `POST /api/proposals/{id}/analyze` - Analyze proposal using ML

### Learning
- `GET /api/learning/stats/{ai_type}` - Get learning statistics
- `GET /api/learning/insights/{ai_type}` - Get learning insights
- `POST /api/learning/train` - Train ML models
- `GET /api/learning/ml-insights` - Get ML insights

### AI Types
- `GET /api/imperium/` - Imperium AI endpoints
- `GET /api/guardian/` - Guardian AI endpoints
- `GET /api/sandbox/` - Sandbox AI endpoints
- `GET /api/conquest/` - Conquest AI endpoints

## ML Models

The system uses several scikit-learn models:

1. **Quality Predictor**: GradientBoostingClassifier for proposal quality scoring
2. **Approval Predictor**: RandomForestClassifier for approval probability
3. **Text Vectorizer**: TF-IDF for text feature extraction
4. **Feature Extractors**: Custom feature engineering for code analysis

### Model Training

Models are automatically trained when:
- Sufficient data is available (>50 proposals with feedback)
- Manual training is triggered via API
- System detects performance degradation

### Feature Engineering

The system extracts features from:
- **Code Analysis**: Length, complexity, similarity metrics
- **Text Analysis**: Sentiment, token count, lexical diversity
- **File Analysis**: File type, AI type, improvement type
- **Historical Data**: Previous success/failure patterns

## Database Schema

### Proposals Collection
```json
{
  "_id": "ObjectId",
  "ai_type": "string",
  "file_path": "string",
  "code_before": "string",
  "code_after": "string",
  "status": "string",
  "confidence": "float",
  "improvement_type": "string",
  "ai_reasoning": "string",
  "user_feedback": "string",
  "user_feedback_reason": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Learning Collection
```json
{
  "_id": "ObjectId",
  "proposal_id": "ObjectId",
  "ai_type": "string",
  "status": "string",
  "feedback_reason": "string",
  "ml_analysis": "object",
  "created_at": "datetime"
}
```

## Development

### Project Structure
```
ai-backend-python/
├── app/
│   ├── core/           # Core configuration and utilities
│   ├── models/         # Pydantic models
│   ├── routers/        # API route handlers
│   └── services/       # Business logic and ML services
├── models/             # Trained ML models
├── main.py            # FastAPI application
├── start.py           # Startup script
└── requirements.txt   # Dependencies
```

### Adding New ML Features

1. **Extend MLService**: Add new methods to `app/services/ml_service.py`
2. **Update Models**: Modify feature extraction in `extract_features()`
3. **Add Endpoints**: Create new routes in appropriate router
4. **Update Documentation**: Document new capabilities

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_ml_service.py
```

## Monitoring

### Logging
- Structured JSON logging with structlog
- Configurable log levels
- Request/response logging
- Error tracking with context

### Metrics
- Proposal processing times
- ML model accuracy
- Learning effectiveness
- API response times

### Health Checks
- Database connectivity
- ML model availability
- External service status
- System resource usage

## Migration from JavaScript

### Key Differences
1. **Async/Await**: Native Python async support
2. **Type Safety**: Pydantic models for validation
3. **ML Integration**: Direct scikit-learn integration
4. **Performance**: FastAPI's high performance
5. **Documentation**: Automatic API documentation

### Migration Steps
1. **Data Migration**: Export MongoDB data from JS backend
2. **Model Training**: Train ML models with historical data
3. **API Testing**: Verify all endpoints work correctly
4. **Performance Testing**: Ensure performance meets requirements
5. **Deployment**: Deploy Python backend alongside JS backend
6. **Switchover**: Gradually migrate traffic to Python backend

## Troubleshooting

### Common Issues

1. **NLTK Data Missing**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

2. **MongoDB Connection**
   - Check MONGODB_URI in .env
   - Ensure MongoDB is running
   - Verify network connectivity

3. **ML Model Loading**
   - Check ML_MODEL_PATH exists
   - Ensure sufficient disk space
   - Verify model file permissions

4. **Memory Issues**
   - Increase Python memory limit
   - Optimize batch processing
   - Monitor memory usage

### Performance Optimization

1. **Database Indexing**: Ensure proper MongoDB indexes
2. **Model Caching**: Cache trained models in memory
3. **Async Processing**: Use background tasks for heavy operations
4. **Connection Pooling**: Optimize database connections

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 