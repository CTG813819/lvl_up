# Quick Deployment (No GitHub Required)

## 🚀 **Option 1: Render (Easiest)**

1. **Go to [render.com](https://render.com)**
2. **Sign up with email**
3. **Click "New +" → "Web Service"**
4. **Upload your `ai-backend-python` folder**
5. **Configure:**
   - **Name**: `ai-backend-python`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. **Add Environment Variables:**
   ```
   DATABASE_URL=your_neon_postgresql_url
   ANTHROPIC_API_KEY=your_anthropic_key
   OPENAI_API_KEY=your_openai_key
   GITHUB_TOKEN=your_github_token
   PORT=8000
   HOST=0.0.0.0
   RUN_BACKGROUND_JOBS=1
   ```
7. **Deploy!**

## 🚀 **Option 2: Railway Web Interface**

1. **Go to [railway.app](https://railway.app)**
2. **Sign up with email**
3. **Click "New Project" → "Deploy from GitHub"**
4. **Create GitHub repo** (takes 2 minutes):
   - Go to [github.com](https://github.com)
   - Click "New repository"
   - Name it `ai-backend-python`
   - Upload your code
5. **Connect Railway to your new repo**
6. **Add environment variables**
7. **Deploy!**

## 🚀 **Option 3: Heroku CLI**

1. **Download Heroku CLI** from [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)
2. **Open PowerShell and run:**
   ```powershell
   # Login to Heroku
   heroku login
   
   # Navigate to your project
   cd ai-backend-python
   
   # Create Heroku app
   heroku create your-ai-backend-name
   
   # Add PostgreSQL
   heroku addons:create heroku-postgresql:hobby-dev
   
   # Set environment variables
   heroku config:set ANTHROPIC_API_KEY=your_anthropic_key
   heroku config:set OPENAI_API_KEY=your_openai_key
   heroku config:set GITHUB_TOKEN=your_github_token
   heroku config:set RUN_BACKGROUND_JOBS=1
   
   # Initialize git and deploy
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

## 🎯 **Recommended: Render**

**Use Render** because:
- ✅ No GitHub required
- ✅ Direct file upload
- ✅ Free tier available
- ✅ Fast deployment
- ✅ Perfect for FastAPI

## 📱 **After Deployment**

Update your Flutter app with the new URL:

```dart
// In lib/services/network_config.dart
static const String baseUrl = 'https://your-new-deployment-url.com';
```

## 🔍 **Test Your Deployment**

```bash
# Health check
curl https://your-deployment-url.com/health

# AI endpoints
curl https://your-deployment-url.com/api/imperium/health
```

**Your AI backend will be online in 10 minutes!** 🚀 