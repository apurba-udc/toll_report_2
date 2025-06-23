#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'toll_report.settings')
django.setup()

from transactions.models import Transaction
from datetime import datetime
from django.utils import timezone
from django.db import models

print("=== CAPTUREDATE DEBUG ANALYSIS ===\n")

# Get sample transactions
sample_transactions = Transaction.objects.all()[:5]

print("1. Sample CAPTUREDATE values:")
for i, t in enumerate(sample_transactions, 1):
    print(f"   {i}. ID: {t.id}")
    print(f"      CAPTUREDATE: {t.capturedate}")
    print(f"      Type: {type(t.capturedate)}")
    print(f"      Timezone aware: {timezone.is_aware(t.capturedate) if t.capturedate else 'N/A'}")
    print()

print("\n2. Current System Time:")
now = datetime.now()
print(f"   Current datetime: {now}")
print(f"   Type: {type(now)}")
print(f"   Timezone aware: {timezone.is_aware(now)}")

print("\n3. Sample Date Range Test:")
# Test with a specific date range
test_start = "2025-06-24 00:00:00"
test_end = "2025-06-24 23:59:59"

print(f"   Test range: {test_start} to {test_end}")

# String comparison (old method)
string_results = Transaction.objects.filter(
    capturedate__gte=test_start,
    capturedate__lte=test_end
).count()
print(f"   String filtering results: {string_results} transactions")

# Datetime object comparison (new method)
try:
    start_dt = datetime.strptime(test_start, '%Y-%m-%d %H:%M:%S')
    end_dt = datetime.strptime(test_end, '%Y-%m-%d %H:%M:%S')
    
    # Check if we need timezone awareness
    first_transaction = Transaction.objects.first()
    if first_transaction and first_transaction.capturedate:
        if timezone.is_aware(first_transaction.capturedate):
            start_dt = timezone.make_aware(start_dt)
            end_dt = timezone.make_aware(end_dt)
            print(f"   Made datetime objects timezone aware")
    
    datetime_results = Transaction.objects.filter(
        capturedate__gte=start_dt,
        capturedate__lte=end_dt
    ).count()
    print(f"   Datetime object filtering results: {datetime_results} transactions")
    
except Exception as e:
    print(f"   Error with datetime filtering: {e}")

print("\n4. Date Range Analysis:")
# Get min and max dates to understand data range
try:
    date_range = Transaction.objects.aggregate(
        min_date=models.Min('capturedate'),
        max_date=models.Max('capturedate')
    )
    print(f"   Earliest transaction: {date_range['min_date']}")
    print(f"   Latest transaction: {date_range['max_date']}")
except Exception as e:
    print(f"   Error getting date range: {e}")

print("\n5. Today's Transactions Check:")
# Check what transactions exist for today
from datetime import date
today = date.today()
today_start = f"{today} 00:00:00"
today_end = f"{today} 23:59:59"

today_count = Transaction.objects.filter(
    capturedate__gte=today_start,
    capturedate__lte=today_end
).count()
print(f"   Today ({today}) transactions: {today_count}")

# Show some recent transactions
print("\n6. Recent Transactions:")
recent = Transaction.objects.order_by('-capturedate')[:5]
for i, t in enumerate(recent, 1):
    print(f"   {i}. ID: {t.id}, Date: {t.capturedate}, Lane: {t.lane}, Amount: {t.fare}")

print("\n=== END DEBUG ANALYSIS ===") 