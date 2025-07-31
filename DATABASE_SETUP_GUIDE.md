# 🗄️ Database Setup Guide

## ✅ **Current Status**
- ✅ Backend starts successfully
- ✅ Pydantic validation errors fixed
- ✅ Database URL format updated
- ❌ Need to setup actual database connection

## 🚀 **Setup Local Database**

### Step 1: Run the database setup script
```bash
chmod +x ~/setup_local_database.sh
~/setup_local_database.sh
```

This script will:
- Install PostgreSQL on the EC2 instance
- Create a local database called `ai_backend`
- Create a user `ai_user` with password `ai_password`
- Update the `.env` file with the local database URL
- Restart the backend service

## 🔍 **What to Expect**

### During Setup:
- 📦 Installing PostgreSQL packages
- 🗄️ Creating database and user
- 📝 Updating .env file
- 🔄 Restarting backend service

### After Setup:
- ✅ PostgreSQL service running
- ✅ Database connection working
- ✅ Backend service restarted
- ✅ No more authentication errors

## 📊 **Verify the Setup**

### Check PostgreSQL status:
```bash
sudo systemctl status postgresql
```

### Check backend logs:
```bash
journalctl -u ai-backend-python -n 30 --no-pager
```

### Test database connection:
```bash
psql -h localhost -U ai_user -d ai_backend -c "SELECT version();"
```

## 🎯 **Expected Results**

After running the setup script, you should see:
- ✅ No database authentication errors
- ✅ Backend service running successfully
- ✅ All API endpoints working
- ✅ AI agents functioning properly

## 🔍 **Test the Backend**

Once the database is setup, test these endpoints:
```bash
# Test basic connectivity
curl http://localhost:4001/api/imperium/agents

# Test proposals endpoint
curl http://localhost:4001/api/proposals/?status=pending

# Test guardian suggestions
curl http://localhost:4001/api/guardian/suggestions
```

## 🚨 **If Issues Persist**

If you still see errors after the database setup:

1. **Check PostgreSQL logs:**
```bash
sudo tail -f /var/log/postgresql/postgresql-*.log
```

2. **Check backend logs:**
```bash
journalctl -u ai-backend-python -f
```

3. **Test database connection manually:**
```bash
sudo -u postgres psql -c "SELECT * FROM pg_user;"
```

## 📝 **Alternative: External Database**

If you prefer to use an external database:

1. **Update .env file:**
```bash
nano ~/ai-backend-python/.env
```

2. **Replace DATABASE_URL with your external database:**
```
DATABASE_URL="postgresql://username:password@your-db-host:5432/database_name"
```

3. **Restart the backend:**
```bash
sudo systemctl restart ai-backend-python
``` 