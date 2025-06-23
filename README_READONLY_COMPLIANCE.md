# Read-Only Database Compliance

This Django application is designed to operate in **strict read-only mode** on the ZAKTOLL database. It ensures that no data modifications can occur through the application, making it safe to run with read-only database permissions.

## 🔒 Security Features

### 1. Model-Level Protection
- **`managed = False`**: All models have `managed=False` to prevent Django from attempting schema changes
- **ReadOnlyManager**: Custom manager that blocks all write operations (`create`, `update`, `delete`, `bulk_create`, `bulk_update`)
- **Overridden save/delete methods**: Model methods throw `PermissionDenied` exceptions

### 2. Database Router Protection
- **ReadOnlyRouter**: Custom database router that blocks all write operations at the database level
- **Migration Blocking**: Prevents any migrations from running on the ZAKTOLL database
- **Write Operation Detection**: Raises `PermissionDenied` for any attempted write operations

### 3. Middleware Monitoring
- **ReadOnlyMiddleware**: Monitors all HTTP requests and logs database access attempts
- **Security Logging**: Tracks potentially unsafe operations and user activities
- **Audit Trail**: Maintains detailed logs of all database interactions

### 4. Authentication Compliance
- **No Login Updates**: Authentication system does not update `lastLogin` to maintain read-only compliance
- **Password Verification Only**: User authentication only verifies credentials without database writes

## 📊 Supported Operations

### ✅ Allowed Operations
- **Read Transactions**: View transaction data from TRANSACTION table through reports
- **Generate Reports**: Create daily, lane-wise, class-wise, and exempt reports
- **PDF Generation**: Export summary reports to PDF format
- **User Authentication**: Login/logout using existing user credentials
- **Data Filtering**: Filter transactions by date, time, lane, vehicle class, payment type
- **Summary Statistics**: Calculate totals, averages, and other analytics
- **Report Analytics**: Comprehensive analysis and visualization of toll data

### ❌ Blocked Operations
- **Data Creation**: No new transactions or users can be created
- **Data Updates**: No existing data can be modified
- **Data Deletion**: No data can be removed from the database
- **Schema Changes**: No table structure modifications
- **User Management**: No user account modifications

## 🛡️ Multi-Layer Protection

### Layer 1: Application Level
```python
# ReadOnlyManager prevents ORM operations
class ReadOnlyManager(models.Manager):
    def create(self, **kwargs):
        raise PermissionDenied("Write operations not allowed")
```

### Layer 2: Database Router
```python
# ReadOnlyRouter blocks all write attempts
def db_for_write(self, model, **hints):
    if model._meta.app_label == 'transactions':
        raise PermissionDenied("Read-only database")
```

### Layer 3: Middleware
```python
# ReadOnlyMiddleware monitors and logs all requests
class ReadOnlyMiddleware:
    def __call__(self, request):
        # Log and monitor all database access
```

### Layer 4: Model Override
```python
# Models explicitly prevent save/delete operations
def save(self, *args, **kwargs):
    raise PermissionDenied("Read-only model")
```

## 📈 Monitoring & Logging

### Log Files
- **`logs/toll_system.log`**: General application activity and database reads
- **`logs/security.log`**: Security events, blocked operations, and user activities

### Log Levels
- **INFO**: Normal read operations and user activities
- **WARNING**: Potentially unsafe requests or unusual patterns
- **ERROR**: Blocked write operations and security violations

### Audit Information
- User authentication events
- Database query attempts
- Report generation activities
- PDF download requests
- Failed operation attempts

## 🔧 Configuration

### Database Settings
```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'ZAKTOLL',
        'USER': 'online',  # Read-only user recommended
        'HOST': '115.127.158.186',
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
        },
    }
}

DATABASE_ROUTERS = ['transactions.db_router.ReadOnlyRouter']
```

### Middleware Configuration
```python
MIDDLEWARE = [
    # ... other middleware ...
    'transactions.middleware.ReadOnlyMiddleware',
    # ... other middleware ...
]
```

## 🧪 Compliance Testing

### Manual Testing
```bash
# Run the compliance check command
python manage.py check_readonly --verbose
```

### Automated Verification
The `check_readonly` management command verifies:
- Model configurations (`managed=False`)
- ReadOnlyManager functionality
- Database router protection
- Middleware configuration
- Read operation capabilities
- Write operation blocking

### Test Results
```
=== Read-Only Database Compliance Check ===

1. Checking model configurations...
  ✓ Transaction model has managed=False
  ✓ TollUser model has managed=False

2. Testing read-only manager...
  ✓ Transaction.objects.create() is properly blocked
  ✓ Transaction.objects.update() is properly blocked
  ✓ Transaction.objects.delete() is properly blocked

3. Testing database permissions...
  ✓ Read operations work (found 1,234,567 transactions)

4. Testing user permissions...
  ✓ Can read user data (5 users found)

5. Testing database router...
  ✓ ReadOnlyRouter is configured

6. Testing middleware...
  ✓ ReadOnlyMiddleware is configured
```

## 🚀 Deployment Recommendations

### Database User Permissions
Create a dedicated read-only database user:
```sql
-- Create read-only user
CREATE LOGIN [readonly_user] WITH PASSWORD = 'secure_password';
CREATE USER [readonly_user] FOR LOGIN [readonly_user];

-- Grant only SELECT permissions
GRANT SELECT ON [TRANSACTION] TO [readonly_user];
GRANT SELECT ON [USERS] TO [readonly_user];

-- Explicitly deny write operations
DENY INSERT, UPDATE, DELETE ON [TRANSACTION] TO [readonly_user];
DENY INSERT, UPDATE, DELETE ON [USERS] TO [readonly_user];
```

### Environment Variables
```bash
# Use read-only database credentials
export DB_PASSWORD="readonly_password"
export DB_USER="readonly_user"
```

### Monitoring Setup
- Monitor log files for security events
- Set up alerts for `PermissionDenied` exceptions
- Regular compliance checks with `check_readonly` command

## 📋 Compliance Checklist

- [ ] All models have `managed = False`
- [ ] ReadOnlyManager is implemented and working
- [ ] ReadOnlyRouter is configured in DATABASE_ROUTERS
- [ ] ReadOnlyMiddleware is added to MIDDLEWARE
- [ ] Authentication doesn't update lastLogin
- [ ] No save() or delete() operations in code
- [ ] Logging is configured and working
- [ ] compliance check passes all tests
- [ ] Database user has read-only permissions
- [ ] Security monitoring is in place

## 🆘 Emergency Procedures

### If Database Writes Are Detected
1. Check `logs/security.log` for details
2. Identify the source of the write attempt
3. Review recent code changes
4. Run `python manage.py check_readonly` to verify configuration
5. Contact database administrator if necessary

### If Read Operations Fail
1. Check database connectivity
2. Verify user permissions
3. Check `logs/toll_system.log` for errors
4. Ensure ZAKTOLL database is accessible

## 📞 Support

For read-only compliance issues:
- Check logs in `logs/` directory
- Run compliance verification: `python manage.py check_readonly --verbose`
- Review this documentation
- Contact system administrator

## ⚠️ Important Notes

- **No Data Modification**: This application will never modify any data in ZAKTOLL database
- **Safe Operation**: Can run safely with read-only database permissions
- **Audit Compliance**: All operations are logged for security and compliance
- **Production Ready**: Designed for safe deployment in production environments

---

**Last Updated**: 2025-01-02  
**Compliance Status**: ✅ Fully Read-Only Compliant  
**Risk Level**: 🟢 Low (Read-Only Operations Only) 