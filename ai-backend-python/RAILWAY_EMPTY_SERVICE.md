# Railway Empty Service Deployment

Since Railway only shows "Deploy to GitHub repo, Template, Database, Docker image, Functions, and Empty service" - use the **Empty Service** option!

## 🚀 **Step-by-Step Railway Empty Service Deployment**

### 1. Create Empty Service
1. **Click "Empty Service"** in Railway dashboard
2. **Name it**: `ai-backend-python`
3. **Click "Deploy"**

### 2. Connect Your Code
After creating the empty service, you have two options:

#### **Option A: Railway CLI (Recommended)**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Navigate to your project
cd ai-backend-python

# Link to your Railway project
railway link

# Deploy your code
railway up
```

#### **Option B: Manual Upload**
1. **In Railway dashboard**, go to your empty service
2. **Click "Settings"** → **"Source"**
3. **Upload your `ai-backend-python` folder** as a ZIP file
4. **Railway will auto-detect FastAPI and deploy**

### 3. Configure Environment Variables
In Railway dashboard:
1. **Go to your service**
2. **Click "Variables"**
3. **Add these environment variables:**
   ```
   DATABASE_URL=your_neon_postgresql_url
   ANTHROPIC_API_KEY=your_anthropic_key
   OPENAI_API_KEY=your_openai_key
   GITHUB_TOKEN=your_github_token
   PORT=8000
   HOST=0.0.0.0
   RUN_BACKGROUND_JOBS=1
   ```

### 4. Set Build Commands
In Railway dashboard:
1. **Go to "Settings"** → **"General"**
2. **Set Build Command**: `pip install -r requirements.txt`
3. **Set Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 5. Get Your Domain
1. **Go to "Settings"** → **"Domains"**
2. **Copy your Railway domain** (e.g., `https://your-app.railway.app`)

## 🚀 **Alternative: Quick GitHub Setup**

If you want the easiest deployment:

### 1. Create GitHub Repo
1. **Go to [github.com](https://github.com)**
2. **Click "New repository"**
3. **Name it**: `ai-backend-python`
4. **Make it Public** (easier for deployment)

### 2. Upload Your Code
```bash
# In your ai-backend-python directory
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-backend-python.git
git push -u origin main
```

### 3. Deploy on Railway
1. **Go back to Railway**
2. **Click "Deploy from GitHub repo"**
3. **Select your new repository**
4. **Railway will auto-deploy!**

## 🎯 **Recommended: Empty Service + Railway CLI**

**Use this method:**
1. **Create Empty Service** in Railway
2. **Install Railway CLI**: `npm install -g @railway/cli`
3. **Login**: `railway login`
4. **Link project**: `railway link`
5. **Deploy**: `railway up`
6. **Set environment variables** in dashboard
7. **Get your domain**

This will get your AI backend online in minutes! 🚀 