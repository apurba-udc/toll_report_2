# Toll Report System - Quick Start Guide

## 🚀 Quick Start

### 1. Verify Read-Only Compliance
```bash
cd /home/atonu/toll_report
python manage.py check_readonly --verbose
```
This should show all ✓ green checks for read-only compliance.

### 2. Start the Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### 3. Access the Application
Open your browser and go to:
- **Local**: http://localhost:8000
- **Network**: http://YOUR_IP:8000

### 4. Login
Use your existing ZAKTOLL database credentials to log in.

## 📊 Available Reports

### 1. Daily Transaction Report
- **URL**: `/report_date/`
- **Features**: 
  - Detailed transaction listings with pagination
  - Date/time filtering
  - Vehicle images and registration details
  - Payment type filtering

### 2. Lane-wise Report
- **URL**: `/summary_lane/`
- **Features**: 
  - Summary statistics (total vehicles, lanes, classes, average per lane)
  - Detailed lane-wise breakdown
  - PDF download capability
  - Date/time filtering

### 3. Class-wise Report  
- **URL**: `/summary_class/`
- **Features**:
  - Summary statistics by vehicle class
  - Class-wise breakdown across all lanes
  - PDF download capability
  - Date/time filtering

### 4. Exempt Vehicles Report
- **URL**: `/exempt/`
- **Features**:
  - Summary statistics for exempt vehicles
  - Lane-wise exempt vehicle breakdown
  - PDF download capability
  - Date/time filtering

## 🔒 Security Features

### Read-Only Operation
- ✅ **NO DATA MODIFICATION**: Application cannot modify ZAKTOLL database
- ✅ **SAFE TO RUN**: Can be deployed with read-only database permissions
- ✅ **AUDIT LOGGING**: All operations are logged for security

### Monitoring
- **General Logs**: `logs/toll_system.log`
- **Security Logs**: `logs/security.log`

## 🛠️ Common Operations

### Generate Daily Report
1. Go to `/report_date/`
2. Select date range and time
3. Submit form
4. View paginated transaction details

### Generate Lane Report
1. Go to `/summary_lane/`
2. Select date range
3. Submit form
4. View summary statistics
5. Download PDF if needed

### Generate Class Report
1. Go to `/summary_class/`
2. Select date range  
3. Submit form
4. View summary statistics
5. Download PDF if needed

### Generate Exempt Report
1. Go to `/exempt/`
2. Select date range
3. Submit form
4. View summary statistics
5. Download PDF if needed

## 🔧 Troubleshooting

### Check Application Status
```bash
python manage.py check_readonly
```

### View Recent Logs
```bash
tail -f logs/toll_system.log
tail -f logs/security.log
```

### Test Database Connection
```bash
python manage.py shell
# In shell:
from transactions.models import Transaction
print(f"Total transactions: {Transaction.objects.count()}")
```

## ⚠️ Important Notes

- **Database**: Connects to ZAKTOLL at 115.127.158.186
- **User**: Uses 'online' database user
- **Read-Only**: NO data will be modified
- **Logging**: All activities are logged
- **PDF Generation**: Available for summary reports
- **Focus**: Application is focused on reporting and analytics only

## 📞 Support

If you encounter issues:
1. Check the compliance: `python manage.py check_readonly`
2. Review logs in `logs/` directory
3. Ensure database connectivity
4. Verify user permissions

---

**Ready to start generating reports safely!** 🎉 