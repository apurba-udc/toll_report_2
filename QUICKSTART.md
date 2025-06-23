# ZAKTOLL Reporting System - Quick Start Guide

## 🎯 **Truly Minimal Django Setup**

This application requires **only 2 database tables** with **read-only access** and **zero Django framework tables**. No messages middleware, no session tables, no migrations - just pure reporting functionality.

## 📋 **Prerequisites**

- Python 3.8+ with Django 4.2+
- Access to ZAKTOLL database (read-only)
- ODBC Driver 18 for SQL Server
- Required Python packages: `django-mssql`, `pyodbc`, `reportlab`

## 🚀 **Quick Start**

### 1. **Verify Read-Only Compliance**
```bash
cd /home/atonu/toll_report
python manage.py check_readonly --verbose
```

**Expected Output:**
```
✓ Transaction model has managed=False
✓ TollUser model has managed=False  
✓ All write operations properly blocked
✓ Read operations work (found X transactions)
✓ Can read user data (X users found)
✓ ReadOnlyRouter is configured
✓ ReadOnlyMiddleware is configured
```

### 2. **Start the Development Server**
```bash
python manage.py runserver 0.0.0.0:8000
```

### 3. **Access the Application**
- **Local:** http://localhost:8000
- **Network:** http://115.127.158.188:8000
- **SSL:** https://115.127.158.188:443 (if SSL is configured)

### 4. **Login**
Use existing ZAKTOLL database credentials:
- Navigate to the login page
- Enter your username and password
- Access granted based on user role in the USERS table

## 📊 **Available Reports**

### **1. Lane-wise Toll Reports**
- **URL:** `/transactions/lane-wise/`
- **Features:** Revenue summary by lane, vehicle class breakdowns
- **PDF Export:** Available with summary statistics
- **Filters:** Date range, time range

### **2. Class-wise Vehicle Reports**  
- **URL:** `/transactions/class-wise/`
- **Features:** Vehicle type analysis, lane distribution
- **PDF Export:** Detailed breakdown with charts
- **Filters:** Date/time, lane selection, vehicle type

### **3. Traffic Summary Reports**
- **URL:** `/transactions/exempt/`
- **Features:** Exempt vehicle tracking, violation analysis
- **PDF Export:** Comprehensive summary
- **Filters:** Custom date ranges, exemption types

## 🛡️ **Security Features**

- **Read-Only Operation:** Cannot modify any data
- **Safe Operation:** Zero risk of database writes
- **Audit Logging:** All operations logged to `logs/`
- **Session Security:** Memory-based sessions (no database storage)
- **Database Protection:** Multi-layer write prevention

## 🔧 **Common Operations**

### **Generate Lane Report**
1. Go to **Lane-wise Reports**
2. Select date range and time period
3. Click **Generate Report**
4. Optionally download as PDF

### **Generate Class Report**
1. Navigate to **Class-wise Reports**
2. Choose filters (lane, vehicle type, date range)
3. Click **Generate Report**  
4. Export to PDF if needed

### **Generate Traffic Summary**
1. Access **Traffic Summary**
2. Set date/time filters
3. View exempt vehicle statistics
4. Download comprehensive PDF report

## 🔍 **Troubleshooting**

### **Check Application Status**
```bash
python manage.py check
```

### **View Recent Logs**
```bash
tail -f logs/toll_system.log
tail -f logs/security.log
```

### **Test Database Connection**
```bash
python manage.py check_readonly
```

## ⚙️ **Database Configuration**

### **Minimal Requirements**
- **Tables Required:** 2 (TRANSACTION + USERS)
- **Django Framework Tables:** 0 (completely eliminated)
- **Permissions:** SELECT only
- **Session Storage:** Memory cache (no database)

### **Setup Script**
```bash
# Run the minimal database setup
sqlcmd -S 115.127.158.186 -d ZAKTOLL -i create_minimal_zaktoll_setup.sql
```

## ⚠️ **Important Notes**

- **Database Connectivity:** Requires access to ZAKTOLL database on 115.127.158.186
- **User Permissions:** Login credentials must exist in USERS table
- **Logging:** All activities logged to `logs/` directory
- **Performance:** Optimized for read-only operations, no migration overhead
- **Security:** Impossible to modify database - all write operations blocked
- **Session Management:** Sessions stored in memory, expire on server restart

## 📞 **Support**

If you encounter issues:
1. **Check compliance:** `python manage.py check_readonly`
2. **Review logs:** Check `logs/toll_system.log` and `logs/security.log`
3. **Verify database:** Ensure ZAKTOLL database is accessible
4. **Test connection:** Use `python manage.py check`

---

**Note:** This application is a **streamlined reporting tool** focused solely on data analysis and reporting. It requires **zero Django framework tables** and operates with **complete read-only safety**. No administrative interface or data modification capabilities are included for enhanced security and simplicity. 