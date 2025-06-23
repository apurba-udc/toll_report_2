# ZAKTOLL Reporting System - Quick Start Guide

## Prerequisites
- Python 3.8+ with Django 4.2+
- Access to ZAKTOLL database (read-only)
- Required Python packages installed

## Quick Start Steps

### 1. Verify Read-Only Compliance
```bash
cd /home/atonu/toll_report
python manage.py check_readonly --verbose
```
**Expected Result**: All checks should be ✓ green

### 2. Start the Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### 3. Access the Application
- **Local Access**: http://localhost:8000
- **Network Access**: http://[server-ip]:8000

### 4. Login
- Use existing ZAKTOLL database credentials
- No admin interface available (streamlined application)
- Direct access to reporting features

## Available Reports

### 1. Lane-wise Toll Reports
- **URL**: `/reports/lane/`
- **Features**: 
  - View transactions by lane
  - Filter by date range and time
  - Export to PDF
  - Real-time data from ZAKTOLL database

### 2. Class-wise Vehicle Reports
- **URL**: `/reports/class/`
- **Features**:
  - Analyze traffic by vehicle class
  - Revenue analysis by vehicle type
  - Statistical summaries
  - PDF export capabilities

### 3. Traffic Summary Reports
- **URL**: `/reports/traffic-summary/`
- **Features**:
  - Overall traffic statistics
  - Peak hour analysis
  - Revenue summaries
  - Comprehensive overview

## Security Features

- **Read-Only Operation**: No data modification allowed
- **Safe Operation**: Application is safe to run with read-only database permissions
- **Audit Logging**: All operations are logged for security
- **Database Protection**: Multiple layers of write protection

## Common Operations

### Generate Lane Report
1. Navigate to homepage
2. Click "Lane-wise Reports" 
3. Select date range (optional)
4. Click "Generate Report"
5. Use "Download PDF" for offline viewing

### Generate Class Report  
1. Click "Class-wise Reports" from homepage
2. Apply filters as needed
3. View results in table format
4. Export to PDF if required

### Generate Traffic Summary
1. Click "Traffic Summary" from homepage
2. Review comprehensive statistics
3. Download report for records

## Troubleshooting

### Check Application Status
```bash
python manage.py check
```

### View Recent Logs
```bash
tail -f logs/toll_system.log
tail -f logs/security.log
```

### Test Database Connection
```bash
python manage.py check_readonly
```

## Important Notes

- **Database**: Connected to ZAKTOLL at 115.127.158.186
- **User Permissions**: Read-only access only
- **Logging**: All activities logged in `logs/` directory
- **Performance**: Optimized for read operations
- **Security**: Multiple protection layers against data modification

## Support

If you encounter issues:
1. Check compliance: `python manage.py check_readonly`
2. Review logs in `logs/` directory
3. Verify database connectivity
4. Ensure read-only permissions are working

---

**Note**: This is a streamlined reporting application focused solely on data analysis and reporting. No administrative interface or data modification capabilities are included for enhanced security and simplicity. 