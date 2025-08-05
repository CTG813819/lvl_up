# Operations Guide - Daily Backend Management
## Lvl_UP AI Backend - Practical Operations Manual

### 🚀 **Daily Operations Checklist**

#### **Morning Routine (00:00-06:00)**
```bash
# 1. Check system status
sudo systemctl status ai-backend-python.service

# 2. Check database health
curl -s http://localhost:8000/api/database/health | jq .

# 3. Check all AI agents status
curl -s http://localhost:8000/api/agents/status | jq .

# 4. Monitor system resources
htop
free -h
df -h

# 5. Check recent logs
sudo journalctl -u ai-backend-python.service -n 50 --no-pager
```

#### **Daytime Monitoring (06:00-18:00)**
```bash
# 1. Monitor real-time performance
./monitor_service.sh

# 2. Check AI learning progress
curl -s http://localhost:8000/api/enhanced-learning/status | jq .

# 3. Monitor custody protocol tests
curl -s http://localhost:8000/api/custody/analytics | jq .

# 4. Check proposal generation
curl -s http://localhost:8000/api/proposals | jq . | head -20

# 5. Monitor security status
curl -s http://localhost:8000/api/guardian/health-status | jq .
```

#### **Evening Review (18:00-24:00)**
```bash
# 1. Generate daily report
python3 generate_daily_report.py

# 2. Check performance metrics
curl -s http://localhost:8000/api/analytics/performance | jq .

# 3. Review error logs
sudo journalctl -u ai-backend-python.service --since "6 hours ago" | grep ERROR

# 4. Check cache performance
curl -s http://localhost:8000/optimized/cache/stats | jq .

# 5. Backup critical data
./backup_critical_data.sh
```

### 🔧 **Common Operations**

#### **Service Management**
```bash
# Start the service
sudo systemctl start ai-backend-python.service

# Stop the service
sudo systemctl stop ai-backend-python.service

# Restart the service
sudo systemctl restart ai-backend-python.service

# Check service status
sudo systemctl status ai-backend-python.service

# Enable auto-start on boot
sudo systemctl enable ai-backend-python.service

# Disable auto-start on boot
sudo systemctl disable ai-backend-python.service
```

#### **Log Management**
```bash
# View real-time logs
sudo journalctl -u ai-backend-python.service -f

# View recent logs
sudo journalctl -u ai-backend-python.service -n 100 --no-pager

# View logs from specific time
sudo journalctl -u ai-backend-python.service --since "2 hours ago"

# View error logs only
sudo journalctl -u ai-backend-python.service -p err --no-pager

# Clear old logs
sudo journalctl --vacuum-time=7d
```

#### **Database Operations**
```bash
# Check database connection
curl -s http://localhost:8000/api/database/health | jq .

# Backup database
pg_dump -h localhost -U username -d lvl_up_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
psql -h localhost -U username -d lvl_up_db < backup_file.sql

# Check database size
psql -h localhost -U username -d lvl_up_db -c "SELECT pg_size_pretty(pg_database_size('lvl_up_db'));"

# Check table sizes
psql -h localhost -U username -d lvl_up_db -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

### 🤖 **AI Agent Management**

#### **Imperium AI (Learning Coordinator)**
```bash
# Check Imperium status
curl -s http://localhost:8000/api/imperium/status | jq .

# Check learning progress
curl -s http://localhost:8000/api/imperium/learning | jq .

# Monitor WebSocket connections
netstat -an | grep :8000 | grep ESTABLISHED

# Check learning analytics
curl -s http://localhost:8000/api/analytics/learning | jq .
```

#### **Guardian AI (Security Monitor)**
```bash
# Check Guardian health
curl -s http://localhost:8000/api/guardian/health-status | jq .

# View security suggestions
curl -s http://localhost:8000/api/guardian/suggestions | jq .

# Run security scan
curl -X POST http://localhost:8000/api/guardian/health-check | jq .

# Check security metrics
curl -s http://localhost:8000/api/analytics/security | jq .
```

#### **Sandbox AI (Testing Environment)**
```bash
# Check Sandbox experiments
curl -s http://localhost:8000/api/sandbox/experiments | jq .

# View test results
curl -s http://localhost:8000/api/sandbox/results | jq .

# Check experiment status
curl -s http://localhost:8000/api/sandbox/status | jq .
```

#### **Conquest AI (Performance Optimizer)**
```bash
# Check Conquest analytics
curl -s http://localhost:8000/api/conquest/analytics | jq .

# View performance metrics
curl -s http://localhost:8000/api/conquest/performance | jq .

# Check build status
curl -s http://localhost:8000/api/conquest/build-status | jq .
```

### 🔒 **Custody Protocol Management**

#### **Test Administration**
```bash
# Run test for specific AI
curl -X POST http://localhost:8000/api/custody/test/imperium | jq .

# Run tests for all AIs
curl -X POST http://localhost:8000/api/custody/batch-test | jq .

# Check test results
curl -s http://localhost:8000/api/custody/analytics | jq .

# View test recommendations
curl -s http://localhost:8000/api/custody/recommendations | jq .

# Check AI eligibility
curl -s http://localhost:8000/api/custody/eligibility/imperium | jq .
```

#### **Level Management**
```bash
# Check AI levels
curl -s http://localhost:8000/api/custody/difficulty/imperium | jq .

# Force level up (admin only)
curl -X POST http://localhost:8000/api/custody/test/imperium/force | jq .

# Reset AI metrics (admin only)
curl -X POST http://localhost:8000/api/custody/test/imperium/reset | jq .
```

### 📊 **Performance Monitoring**

#### **System Performance**
```bash
# Monitor CPU usage
top -p $(pgrep -f uvicorn)

# Monitor memory usage
ps aux | grep uvicorn | grep -v grep

# Check disk usage
df -h /home/ubuntu/ai-backend-python

# Monitor network connections
netstat -tulpn | grep :8000

# Check process limits
cat /proc/$(pgrep -f uvicorn)/limits
```

#### **Application Performance**
```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health

# Monitor database connections
psql -h localhost -U username -d lvl_up_db -c "
SELECT 
    state,
    count(*) as connections
FROM pg_stat_activity 
WHERE datname = 'lvl_up_db'
GROUP BY state;
"

# Check cache performance
curl -s http://localhost:8000/optimized/cache/stats | jq .

# Monitor background tasks
ps aux | grep python | grep -v grep
```

### 🚨 **Troubleshooting Guide**

#### **Service Won't Start**
```bash
# 1. Check service configuration
sudo systemctl cat ai-backend-python.service

# 2. Check for port conflicts
sudo netstat -tulpn | grep :8000

# 3. Check logs for errors
sudo journalctl -u ai-backend-python.service -n 50 --no-pager

# 4. Check file permissions
ls -la /home/ubuntu/ai-backend-python/

# 5. Check Python environment
/home/ubuntu/ai-backend-python/venv/bin/python --version
```

#### **High CPU Usage**
```bash
# 1. Identify high CPU processes
top -p $(pgrep -f uvicorn)

# 2. Check for infinite loops
sudo journalctl -u ai-backend-python.service -f | grep -i loop

# 3. Check background task frequency
grep -r "asyncio.create_task" /home/ubuntu/ai-backend-python/app/

# 4. Monitor database queries
sudo journalctl -u ai-backend-python.service | grep "slow query"

# 5. Check for memory leaks
ps aux | grep uvicorn | awk '{print $6}' | sort -n
```

#### **Database Issues**
```bash
# 1. Check database connection
curl -s http://localhost:8000/api/database/health | jq .

# 2. Check PostgreSQL status
sudo systemctl status postgresql

# 3. Check database logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# 4. Check connection pool
psql -h localhost -U username -d lvl_up_db -c "
SELECT 
    count(*) as active_connections,
    max_conn as max_connections
FROM pg_stat_activity, pg_settings 
WHERE name = 'max_connections';
"

# 5. Check for locks
psql -h localhost -U username -d lvl_up_db -c "
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query
FROM pg_stat_activity 
WHERE state = 'active';
"
```

#### **AI Agent Issues**
```bash
# 1. Check agent status
curl -s http://localhost:8000/api/agents/status | jq .

# 2. Check agent logs
sudo journalctl -u ai-backend-python.service | grep -i "agent"

# 3. Test agent endpoints
curl -s http://localhost:8000/api/imperium/status | jq .
curl -s http://localhost:8000/api/guardian/health-status | jq .
curl -s http://localhost:8000/api/sandbox/experiments | jq .
curl -s http://localhost:8000/api/conquest/analytics | jq .

# 4. Check API keys
grep -r "API_KEY" /home/ubuntu/ai-backend-python/.env

# 5. Test external API connections
curl -s http://localhost:8000/api/health | jq .
```

### 🔄 **Maintenance Procedures**

#### **Weekly Maintenance**
```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Clean up old logs
sudo journalctl --vacuum-time=7d

# 3. Clean up old backups
find /home/ubuntu/backups -name "*.sql" -mtime +7 -delete

# 4. Optimize database
psql -h localhost -U username -d lvl_up_db -c "VACUUM ANALYZE;"

# 5. Check disk space
df -h

# 6. Review performance metrics
curl -s http://localhost:8000/api/analytics/performance | jq .
```

#### **Monthly Maintenance**
```bash
# 1. Full system backup
./full_system_backup.sh

# 2. Database optimization
psql -h localhost -U username -d lvl_up_db -c "REINDEX DATABASE lvl_up_db;"

# 3. Security audit
./security_audit.sh

# 4. Performance review
./performance_review.sh

# 5. Update dependencies
pip3 install -r requirements.txt --upgrade

# 6. Review and rotate logs
sudo logrotate -f /etc/logrotate.conf
```

### 📈 **Performance Optimization**

#### **Database Optimization**
```sql
-- Check slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check table statistics
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY tablename, attname;

-- Analyze table usage
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
FROM pg_stat_user_tables 
ORDER BY seq_scan DESC;
```

#### **Application Optimization**
```bash
# Check memory usage patterns
ps aux | grep uvicorn | awk '{print $6}' | sort -n

# Monitor cache hit rates
curl -s http://localhost:8000/optimized/cache/stats | jq .

# Check background task performance
grep -r "background_task" /home/ubuntu/ai-backend-python/logs/

# Monitor API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health
```

### 🚀 **Deployment Procedures**

#### **Code Deployment**
```bash
# 1. Backup current version
cp -r /home/ubuntu/ai-backend-python /home/ubuntu/ai-backend-python.backup.$(date +%Y%m%d_%H%M%S)

# 2. Pull latest code
cd /home/ubuntu/ai-backend-python
git pull origin main

# 3. Update dependencies
source venv/bin/activate
pip3 install -r requirements.txt

# 4. Run database migrations
python3 -m alembic upgrade head

# 5. Restart service
sudo systemctl restart ai-backend-python.service

# 6. Verify deployment
curl -s http://localhost:8000/api/health | jq .
```

#### **Configuration Updates**
```bash
# 1. Backup configuration
cp /home/ubuntu/ai-backend-python/.env /home/ubuntu/ai-backend-python/.env.backup.$(date +%Y%m%d_%H%M%S)

# 2. Update configuration
nano /home/ubuntu/ai-backend-python/.env

# 3. Validate configuration
python3 -c "from app.core.config import settings; print('Config valid')"

# 4. Restart service
sudo systemctl restart ai-backend-python.service

# 5. Verify configuration
curl -s http://localhost:8000/api/config | jq .
```

This operations guide provides comprehensive procedures for daily management, troubleshooting, and maintenance of the Lvl_UP AI backend system. 