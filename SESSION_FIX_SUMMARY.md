# Session Logout সমস্যার সমাধান

## মূল সমস্যাগুলো যা ঠিক করা হয়েছে:

### 1. ✅ Domain Mismatch সমস্যা
**সমস্যা:** nginx config এ HTTPS server `toll.sdlbdcloud.com` কিন্তু HTTP redirect `cda.sdlbdcloud.com`
**সমাধান:** nginx config file দেখুন: `nginx_config_fixed.conf`

### 2. ✅ Session Engine সমস্যা  
**সমস্যা:** Local Memory Cache ব্যবহার করছিল যা Gunicorn এর multiple workers এর সাথে কাজ করে না
**সমাধান:** File-based sessions ব্যবহার করা হয়েছে

### 3. ✅ SSL Cookie Settings
**সমস্যা:** DEBUG=True থাকার কারণে secure cookies disable ছিল
**সমাধান:** Force secure cookies for HTTPS

### 4. ✅ Session Timeout
**সমস্যা:** 1 ঘন্টা timeout খুব কম ছিল
**সমাধান:** 2 ঘন্টা করা হয়েছে

## প্রয়োজনীয় পদক্ষেপ:

### 1. nginx config আপডেট করুন:
```bash
# আপনার nginx config file edit করুন
sudo nano /etc/nginx/sites-available/your-site

# নিচের config ব্যবহার করুন (nginx_config_fixed.conf থেকে)
```

### 2. Django restart করুন:
```bash
# Gunicorn service restart করুন
sudo systemctl restart your-gunicorn-service

# অথবা manually restart করুন
sudo pkill -f gunicorn
cd /home/atonu/toll_report
/usr/local/bin/gunicorn toll_system.wsgi:application --workers 3 --bind 127.0.0.1:8887
```

### 3. nginx restart করুন:
```bash
sudo systemctl restart nginx
```

## পরিবর্তনের বিস্তারিত:

### Django settings.py এ যা পরিবর্তন হয়েছে:
- `ALLOWED_HOSTS` এ `cda.sdlbdcloud.com` যোগ করা হয়েছে
- `CSRF_TRUSTED_ORIGINS` এ দুটি domain যোগ করা হয়েছে
- `SESSION_ENGINE` file-based করা হয়েছে
- `SESSION_COOKIE_AGE` 2 ঘন্টা করা হয়েছে  
- SSL cookie settings force enable করা হয়েছে

### nginx config এ যা করতে হবে:
- দুটি server block এ same domain ব্যবহার করুন
- `X-Forwarded-Proto` header যোগ করুন

## Test করার জন্য:
1. Browser এ গিয়ে clear cookies করুন
2. নতুন করে login করুন
3. 15-20 মিনিট ব্যবহার করুন দেখতে logout হয় কিনা
4. Different tabs এ check করুন

## আরো debugging এর জন্য:
```bash
# Session files check করুন
ls -la /tmp/django_sessions/

# logs check করুন  
tail -f /home/atonu/toll_report/logs/toll_system.log
```

যদি এখনো সমস্যা থাকে তাহলে আমাকে জানান।

