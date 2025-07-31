# 🗄️ Neon Database Setup

## ✅ **Great Choice!**
Using Neon database is much better than local PostgreSQL for production. Neon provides:
- ✅ Managed PostgreSQL service
- ✅ Automatic backups
- ✅ High availability
- ✅ No server maintenance needed

## 🚀 **Setup Neon Database Connection**

### Step 1: Run the Neon database setup script
```bash
chmod +x ~/update_neon_database.sh
~/update_neon_database.sh
```

## 🔍 **What This Will Do**

The script will:
- ✅ Backup your current .env file
- ✅ Update DATABASE_URL with your Neon database credentials
- ✅ Test the Neon database connection
- ✅ Restart the backend service
- ✅ Show backend logs after restart

## 📊 **Expected Results**

After running the script, you should see:
- ✅ Neon database connection successful
- ✅ Backend service restarted
- ✅ No more authentication errors
- ✅ All API endpoints working

## 🔍 **Verify the Fix**

After the script completes, test these endpoints:
```bash
# Test proposals endpoint
curl http://localhost:4001/api/proposals/?status=pending

# Test guardian suggestions
curl http://localhost:4001/api/guardian/suggestions

# Test sandbox experiments
curl http://localhost:4001/api/sandbox/experiments
```

## 🎯 **What Should Work**

- ✅ All database-dependent endpoints
- ✅ Proposal creation and retrieval
- ✅ Guardian suggestions
- ✅ Sandbox experiments
- ✅ AI learning and growth services
- ✅ All CRUD operations

## 🚨 **If Issues Persist**

If you still see errors:

1. **Check the .env file:**
```bash
cat ~/ai-backend-python/.env | grep DATABASE_URL
```

2. **Manually update if needed:**
```bash
nano ~/ai-backend-python/.env
```
Make sure the line reads:
```
DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-1b.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
```

3. **Restart backend:**
```bash
sudo systemctl restart ai-backend-python
```

## 📝 **Neon Database Benefits**

- ✅ **Managed Service**: No server maintenance
- ✅ **Automatic Backups**: Data is safe
- ✅ **High Availability**: 99.9% uptime
- ✅ **SSL Security**: Encrypted connections
- ✅ **Scalable**: Grows with your needs

This should completely resolve your database issues and give you a production-ready backend! 