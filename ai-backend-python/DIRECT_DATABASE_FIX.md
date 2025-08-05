# 🔧 Direct Database Fix

## ❌ **Current Issue**
The DATABASE_URL is still using the old format: `postgresql://username:password@localhost/dbname`

## 🚀 **Run the Direct Fix**

### Step 1: Run the direct fix script
```bash
chmod +x ~/direct_database_fix.sh
~/direct_database_fix.sh
```

## 🔍 **What This Will Do**

The script will:
- ✅ Show current DATABASE_URL
- ✅ Replace it with: `postgresql://ai_user:ai_password@localhost:5432/ai_backend`
- ✅ Test database connection
- ✅ Restart backend service
- ✅ Show backend logs

## 📊 **Expected Results**

After running the script, you should see:
- ✅ DATABASE_URL updated correctly
- ✅ Database connection test successful
- ✅ Backend service restarted
- ✅ No more authentication errors

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

## 🚨 **If Still Failing**

If you still see authentication errors, manually check:

1. **Check .env file:**
```bash
cat ~/ai-backend-python/.env | grep DATABASE_URL
```

2. **Manually edit if needed:**
```bash
nano ~/ai-backend-python/.env
```
Make sure the line reads:
```
DATABASE_URL="postgresql://ai_user:ai_password@localhost:5432/ai_backend"
```

3. **Restart backend:**
```bash
sudo systemctl restart ai-backend-python
```

This direct fix should resolve the database authentication issue completely! 