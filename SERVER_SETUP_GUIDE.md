# Toll Management System SSL Server Setup Guide

এই গাইড আপনাকে নতুন **Bash Script** ব্যবহার করে SSL server চালাতে সাহায্য করবে। Python script এর সমস্যার সমাধান হিসেবে এই robust bash script তৈরি করা হয়েছে।

## 🚀 Quick Start

### ১. Basic Server চালু করা

```bash
# SSL server শুরু করুন (default)
./start_toll_server.sh

# অথবা explicit start command
./start_toll_server.sh start
```

### ২. Server বন্ধ করা

```bash
# চলমান servers বন্ধ করুন
./start_toll_server.sh stop
```

### ৩. Server restart করা

```bash
# Server restart করুন
./start_toll_server.sh restart
```

## 🔧 Available Commands

| Command | Description |
|---------|-------------|
| `./start_toll_server.sh start` | SSL server চালু করুন |
| `./start_toll_server.sh stop` | চলমান servers বন্ধ করুন |
| `./start_toll_server.sh restart` | Server restart করুন |
| `./start_toll_server.sh status` | Server status চেক করুন |
| `./start_toll_server.sh check` | Requirements verify করুন |
| `./start_toll_server.sh help` | Help message দেখুন |

## 🧪 Testing & Troubleshooting

### সম্পূর্ণ System Test

```bash
# সমস্ত tests চালান
./test_server.sh

# অথবা specific tests:
./test_server.sh django     # Django setup test
./test_server.sh ssl        # SSL certificates test  
./test_server.sh db         # Database connection test
./test_server.sh auth       # User authentication test
./test_server.sh ports      # Server ports check
```

### Development Server (SSL ছাড়া)

```bash
# Development server চালান (debugging এর জন্য)
./test_server.sh dev
```

### Logs দেখা

```bash
# Recent logs দেখুন
./test_server.sh logs
```

## 🛠️ Common Issues & Solutions

### Issue 1: `/login.html not found` (404 Error)

**Solution:**
```bash
# Template issues ঠিক করুন
./test_server.sh fix

# Django static files collect করুন
./test_server.sh django
```

### Issue 2: Server Stacking/Hanging

**Causes:**
- Port 443 already in use
- SSL certificate issues  
- Virtual environment problems

**Solutions:**
```bash
# 1. Port check করুন
./test_server.sh ports

# 2. Existing servers বন্ধ করুন
./start_toll_server.sh stop

# 3. SSL certificates verify করুন
./test_server.sh ssl

# 4. Fresh restart করুন
./start_toll_server.sh restart
```

### Issue 3: SSL Certificate Problems

```bash
# Certificate validity check করুন
./test_server.sh ssl

# Certificate files ensure করুন:
# - cert/private.key
# - cert/certificate.crt  
# - cert/combined_cert.crt
```

### Issue 4: Permission Denied (Port 443)

Script automatically `sudo` দিয়ে চালায় port 443 এর জন্য। Manual করতে চাইলে:

```bash
sudo ./start_toll_server.sh start
```

## 📋 Prerequisites Check

Script চালানোর আগে ensure করুন:

### Required Files:
```
cert/
├── private.key          # Private key file
├── certificate.crt      # Certificate file  
└── combined_cert.crt    # Chain certificate file
```

### Required Directories:
```
toll_report/
├── venv/               # Virtual environment
├── templates/auth/     # Login template directory
├── logs/              # Log files directory
└── manage.py          # Django management script
```

## 🔄 Service Management (Optional)

System service হিসেবে চালানোর জন্য:

```bash
# Service file install করুন
sudo cp toll-ssl.service /etc/systemd/system/

# Service enable করুন
sudo systemctl enable toll-ssl

# Service start করুন  
sudo systemctl start toll-ssl

# Service status check করুন
sudo systemctl status toll-ssl

# Logs দেখুন
sudo journalctl -u toll-ssl -f
```

## 🚨 Emergency Procedures

### Complete Reset

```bash
# 1. সমস্ত Django processes kill করুন
sudo pkill -f "manage.py"

# 2. Port clear করুন (যদি stuck হয়)
sudo fuser -k 443/tcp

# 3. Virtual environment recreate করুন (যদি corrupted)
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Fresh start
./start_toll_server.sh start
```

### Debug Mode

```bash
# Development server দিয়ে debug করুন
./test_server.sh dev

# Database connection verify করুন
./test_server.sh db

# Authentication test করুন  
./test_server.sh auth
```

## 📊 Monitoring

### Real-time Logs

```bash
# Server startup logs
tail -f logs/server_startup.log

# Django application logs  
tail -f logs/toll_system.log

# Error logs
tail -f logs/server_errors.log
```

### Process Monitoring

```bash
# Django processes check করুন
ps aux | grep "manage.py"

# Port usage check করুন
netstat -tulnp | grep ":443"
```

## 🎯 Key Advantages of Bash Script

1. **Better Error Handling**: Comprehensive error checking এবং meaningful messages
2. **Process Management**: Automatic cleanup এবং process killing
3. **Port Management**: Port availability checking এবং conflict resolution
4. **Certificate Management**: SSL certificate validation এবং auto-creation
5. **Logging**: Detailed logging সব operations এর জন্য
6. **Recovery**: Automatic restart এবং cleanup mechanisms

## 🔍 Comparison: Python vs Bash Script

| Feature | Python Script | Bash Script |
|---------|---------------|-------------|
| **Reliability** | ❌ Certificate cleanup issues | ✅ Proper cleanup & management |
| **Error Handling** | ❌ Basic error messages | ✅ Detailed status messages |
| **Process Management** | ❌ No automatic cleanup | ✅ Complete process lifecycle |
| **Port Checking** | ❌ No port validation | ✅ Port availability check |
| **Debugging** | ❌ Limited debugging info | ✅ Comprehensive testing tools |
| **Service Integration** | ❌ Manual management | ✅ Systemd service support |

## 📞 Getting Help

- **Quick Test**: `./test_server.sh all`
- **Status Check**: `./start_toll_server.sh status`  
- **Help Command**: `./start_toll_server.sh help`
- **Development Mode**: `./test_server.sh dev`

Bash script ব্যবহার করে আপনার SSL server আরো stable এবং manageable হবে। Python script এর সমস্যাগুলো এড়িয়ে robust server management পাবেন। 