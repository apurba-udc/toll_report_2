# 📊 Comprehensive Logging Guide for Toll System

এই গাইড আপনাকে **সমস্ত possible logs** enable করতে এবং monitor করতে সাহায্য করবে। Debugging এবং troubleshooting এর জন্য সম্পূর্ণ logging solution।

## 🚀 Quick Setup

### **একবার Setup করুন:**
```bash
# সমস্ত logging enable করুন
./enable_all_logging.sh setup
```

এর পর আপনার কাছে থাকবে:
- ✅ **7 ধরনের log directories**
- ✅ **Real-time monitoring scripts**  
- ✅ **Debug server modes**
- ✅ **SSL connection testing**
- ✅ **Systemd service debugging**
- ✅ **Automatic log rotation**

## 📁 Log Directory Structure

```
logs/
├── system/           # System and process logs
│   ├── server_startup.log
│   └── server_errors.log
├── django/           # Django application logs  
│   └── django.log
├── ssl/              # SSL certificate and connection logs
│   ├── ssl_connections.log
│   └── ssl_test_*.log
├── database/         # Database connection and query logs
│   └── database.log
├── auth/             # Authentication and security logs
│   └── authentication.log
├── debug/            # Debug and troubleshooting logs
│   ├── debug.log
│   └── server_debug_*.log
└── service/          # Systemd service logs
```

## 🔍 Real-time Log Monitoring

### **সমস্ত Logs একসাথে দেখুন:**
```bash
# সব logs monitor করুন
./monitor_logs.sh all
```

### **Specific Log Categories:**
```bash
./monitor_logs.sh django     # Django application logs
./monitor_logs.sh ssl        # SSL connection logs  
./monitor_logs.sh db         # Database logs
./monitor_logs.sh auth       # Authentication logs
./monitor_logs.sh service    # Systemd service logs
./monitor_logs.sh errors     # শুধু error logs
```

## 🐛 Debug Modes

### **1. Debug Server Mode:**
```bash
# Maximum debugging সহ server চালান
./start_debug_server.sh
```
- সমস্ত bash commands log হবে
- Django debug mode enable
- Real-time log file save

### **2. SSL Connection Testing:**
```bash
# SSL connection test করুন
./test_ssl_connection.sh
```
- Certificate validation
- Cipher information  
- Connection diagnostics

### **3. Manual Debug Mode:**
```bash
# Manual debug start
DJANGO_DEBUG=1 PYTHONUNBUFFERED=1 ./start_toll_server.sh start
```

## 📋 Systemd Service Logging

### **Service Logs (Real-time):**
```bash
# Service logs follow করুন
sudo journalctl -u toll-ssl-debug -f

# Last hour logs
sudo journalctl -u toll-ssl-debug --since '1 hour ago'

# Today's logs  
sudo journalctl -u toll-ssl-debug --since today

# Boot থেকে সব logs
sudo journalctl -u toll-ssl-debug --since boot
```

### **Debug Service চালান:**
```bash
# Debug service enable করুন
sudo systemctl enable toll-ssl-debug
sudo systemctl start toll-ssl-debug

# Status check
sudo systemctl status toll-ssl-debug
```

## 🔧 Manual Log Commands

### **Specific Log Files:**
```bash
# Django application logs
tail -f logs/django/django.log

# SSL connections
tail -f logs/ssl/ssl_connections.log

# Database queries (সব SQL queries দেখুন)
tail -f logs/database/database.log

# Authentication activities
tail -f logs/auth/authentication.log

# Debug information
tail -f logs/debug/debug.log

# System startup logs
tail -f logs/system/server_startup.log
```

### **Multiple Files একসাথে:**
```bash
# সমস্ত logs একসাথে
tail -f logs/*/*.log

# শুধু error files
tail -f logs/*/error*.log
```

## 🔍 Log Analysis & Searching

### **Error Hunting:**
```bash
# সমস্ত errors খুঁজুন
grep -r "ERROR" logs/

# Critical issues
grep -r "CRITICAL\|FATAL" logs/

# Exceptions
grep -r "Exception\|Traceback" logs/

# SSL errors
grep -r "SSL\|TLS\|Certificate" logs/ssl/
```

### **Authentication Analysis:**
```bash
# Login activities
grep -r "login\|Login" logs/auth/

# Failed authentication
grep -r "failed\|Failed\|invalid" logs/auth/

# User activities
grep -r "User.*accessed" logs/
```

### **Database Analysis:**
```bash
# Database connections
grep -r "connection\|connect" logs/database/

# SQL queries
grep -r "SELECT\|INSERT\|UPDATE" logs/database/

# Database errors
grep -r "database.*error\|SQL.*error" logs/
```

### **Performance Analysis:**
```bash
# Slow requests (Django)
grep -r "slow\|timeout" logs/django/

# Server startup time
grep -r "Starting\|Started" logs/system/

# Memory usage
grep -r "memory\|Memory" logs/
```

## 📊 Advanced Monitoring

### **Real-time Error Monitoring:**
```bash
# শুধু errors দেখুন (live)
./monitor_logs.sh errors

# অথবা manual
tail -f logs/*/*.log | grep -i "error\|exception\|failed"
```

### **Multi-window Monitoring:**
```bash
# Terminal 1: Django logs
./monitor_logs.sh django

# Terminal 2: SSL logs  
./monitor_logs.sh ssl

# Terminal 3: Service logs
./monitor_logs.sh service

# Terminal 4: Errors only
./monitor_logs.sh errors
```

### **Log Stats:**
```bash
# Log file sizes
du -h logs/*/*.log

# Line counts
wc -l logs/*/*.log

# Latest entries
ls -lt logs/*/*.log
```

## 🛠️ Troubleshooting Common Issues

### **Issue 1: Service Start Failure**
```bash
# 1. Service status check
sudo systemctl status toll-ssl-debug -l

# 2. Recent service logs
sudo journalctl -u toll-ssl-debug --since '5 minutes ago'

# 3. Debug mode
./start_debug_server.sh

# 4. Manual test
./start_toll_server.sh check
```

### **Issue 2: SSL Connection Problems**
```bash
# 1. SSL test
./test_ssl_connection.sh

# 2. SSL logs
tail -f logs/ssl/ssl_connections.log

# 3. Certificate check
openssl x509 -in cert/certificate.crt -text -noout
```

### **Issue 3: Database Issues**
```bash
# 1. Database logs
tail -f logs/database/database.log

# 2. Connection test
./test_server.sh db

# 3. Django check
source venv/bin/activate
python manage.py check --database default
```

### **Issue 4: Authentication Problems**
```bash
# 1. Auth logs
tail -f logs/auth/authentication.log

# 2. User test
./test_server.sh auth

# 3. Login attempts
grep -r "login" logs/auth/
```

## 📈 Performance Monitoring

### **Server Performance:**
```bash
# CPU/Memory usage during server operation
top -p $(pgrep -f "manage.py")

# Server response time
curl -w "@curl-format.txt" -o /dev/null -s "https://115.127.158.186/"

# Connection count
netstat -an | grep :443 | wc -l
```

### **Log Growth Monitoring:**
```bash
# Log size growth
watch -n 60 'du -h logs/*/*.log'

# Active log writing
lsof +D logs/
```

## 🔄 Log Rotation & Cleanup

### **Automatic Rotation:**
Log rotation ইতিমধ্যে configured (30 days retention)

### **Manual Cleanup:**
```bash
# Old logs clean (7 দিনের বেশি পুরানো)
find logs/ -name "*.log" -mtime +7 -delete

# Compress old logs
find logs/ -name "*.log" -mtime +1 -exec gzip {} \;

# Archive logs by date
mkdir -p archive/$(date +%Y%m%d)
cp logs/*/*.log archive/$(date +%Y%m%d)/
```

## 🚨 Emergency Debugging

### **Complete Debug Mode:**
```bash
# 1. Stop normal service
sudo systemctl stop toll-ssl

# 2. Start debug mode
./start_debug_server.sh

# 3. Monitor all logs (in another terminal)
./monitor_logs.sh all

# 4. Test functionality
curl -k https://115.127.158.186/login/
```

### **Live Process Monitoring:**
```bash
# Monitor server processes
watch -n 2 'ps aux | grep manage.py'

# Monitor open files
watch -n 5 'lsof -p $(pgrep -f manage.py)'

# Monitor network connections
watch -n 10 'netstat -tulnp | grep :443'
```

## 📋 Quick Reference Commands

### **Setup & Enable:**
```bash
./enable_all_logging.sh setup     # Setup all logging
sudo systemctl start toll-ssl-debug  # Start debug service
```

### **Monitor (Choose One):**
```bash
./monitor_logs.sh all              # All logs
./monitor_logs.sh service          # Service logs
sudo journalctl -u toll-ssl-debug -f  # Systemd logs
```

### **Debug:**
```bash
./start_debug_server.sh            # Debug server
./test_ssl_connection.sh           # SSL test
./test_server.sh all               # System test
```

### **Analysis:**
```bash
grep -r "ERROR" logs/              # Find errors
grep -r "login" logs/auth/         # Login activities
tail -f logs/debug/debug.log       # Debug info
```

## 🎯 Best Practices

1. **🔄 Regular Monitoring**: Daily `./monitor_logs.sh errors` check করুন
2. **📊 Weekly Analysis**: সপ্তাহে একবার full log analysis করুন
3. **🧹 Cleanup**: Monthly log cleanup এবং archiving
4. **🚨 Alert Setup**: Critical errors এর জন্য email alerts setup করুন
5. **📈 Performance Tracking**: Regular performance monitoring করুন

## 💡 Pro Tips

- **Multiple Terminals**: Different log categories জন্য আলাদা terminals ব্যবহার করুন
- **Log Filtering**: `grep`, `awk`, `sed` দিয়ে specific patterns খুঁজুন  
- **Time-based Analysis**: `--since` এবং `--until` দিয়ে time range specify করুন
- **Real-time Alerts**: `tail -f logs/*/*.log | grep -i critical` দিয়ে instant alerts পান

---

**Summary**: এই comprehensive logging system দিয়ে আপনি toll system এর সমস্ত activities track করতে পারবেন এবং যেকোনো সমস্যা দ্রুত identify ও solve করতে পারবেন। 