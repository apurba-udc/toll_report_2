-- =====================================================
-- MINIMAL ZAKTOLL DATABASE SETUP FOR READ-ONLY REPORTING
-- =====================================================
-- This script creates ONLY the essential database objects
-- needed for the Django toll reporting application
-- 
-- Requirements: SQL Server 2016+ or Azure SQL Database
-- Zero Django framework tables needed!
-- =====================================================

USE ZAKTOLL;
GO

-- =====================================================
-- STEP 1: CREATE USERS TABLE (if not exists)
-- =====================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='USERS' AND xtype='U')
BEGIN
    CREATE TABLE [dbo].[USERS] (
        [id] [int] IDENTITY(1,1) NOT NULL,
        [username] [nvarchar](150) NOT NULL,
        [password] [nvarchar](128) NOT NULL,
        [first_name] [nvarchar](150) NULL,
        [last_name] [nvarchar](150) NULL,
        [email] [nvarchar](254) NULL,
        [is_staff] [bit] NOT NULL DEFAULT 0,
        [is_active] [bit] NOT NULL DEFAULT 1,
        [date_joined] [datetime2] NOT NULL DEFAULT GETDATE(),
        [role] [nvarchar](20) NULL DEFAULT 'user',
        CONSTRAINT [PK_USERS] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [UQ_USERS_username] UNIQUE ([username])
    );
    
    PRINT 'USERS table created successfully.';
END
ELSE
BEGIN
    PRINT 'USERS table already exists.';
END
GO

-- =====================================================
-- STEP 2: VERIFY TRANSACTION TABLE EXISTS
-- =====================================================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TRANSACTION' AND xtype='U')
BEGIN
    PRINT 'ERROR: TRANSACTION table does not exist!';
    PRINT 'This table should already exist in your ZAKTOLL database.';
    PRINT 'Please ensure the TRANSACTION table is created with toll data.';
END
ELSE
BEGIN
    PRINT 'TRANSACTION table exists - OK.';
END
GO

-- =====================================================
-- STEP 3: CREATE READ-ONLY DATABASE USER (RECOMMENDED)
-- =====================================================
-- Create a dedicated read-only user for the Django application
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'django_readonly')
BEGIN
    -- Create login at server level (run on master database)
    PRINT 'Creating read-only user for Django application...';
    
    -- Note: This requires sysadmin privileges to create login
    -- If you don't have sysadmin access, ask your DBA to create this user
    
    CREATE USER [django_readonly] WITHOUT LOGIN;
    
    -- Grant read permissions
    GRANT SELECT ON [dbo].[TRANSACTION] TO [django_readonly];
    GRANT SELECT ON [dbo].[USERS] TO [django_readonly];
    
    -- Explicitly deny write operations (extra security)
    DENY INSERT, UPDATE, DELETE ON [dbo].[TRANSACTION] TO [django_readonly];
    DENY INSERT, UPDATE, DELETE ON [dbo].[USERS] TO [django_readonly];
    
    PRINT 'Read-only user created and permissions granted.';
END
ELSE
BEGIN
    PRINT 'django_readonly user already exists.';
END
GO

-- =====================================================
-- STEP 4: INSERT SAMPLE USERS (if table is empty)
-- =====================================================
IF NOT EXISTS (SELECT * FROM [dbo].[USERS])
BEGIN
    PRINT 'Creating sample users...';
    
    INSERT INTO [dbo].[USERS] ([username], [password], [first_name], [last_name], [email], [is_staff], [is_active], [role])
    VALUES 
        ('admin', 'pbkdf2_sha256$600000$samplehash123$', 'Administrator', 'User', 'admin@toll.com', 1, 1, 'admin'),
        ('operator', 'pbkdf2_sha256$600000$samplehash456$', 'Toll', 'Operator', 'operator@toll.com', 0, 1, 'operator'),
        ('viewer', 'pbkdf2_sha256$600000$samplehash789$', 'Report', 'Viewer', 'viewer@toll.com', 0, 1, 'viewer');
    
    PRINT 'Sample users created. Default passwords need to be set properly.';
    PRINT 'WARNING: These are sample passwords - change them before production!';
END
ELSE
BEGIN
    PRINT 'USERS table already contains data.';
END
GO

-- =====================================================
-- STEP 5: VERIFY DATABASE SETUP
-- =====================================================
PRINT '=====================================================';
PRINT 'DATABASE SETUP VERIFICATION';
PRINT '=====================================================';

-- Check TRANSACTION table
IF EXISTS (SELECT * FROM sysobjects WHERE name='TRANSACTION' AND xtype='U')
BEGIN
    DECLARE @transaction_count INT;
    SELECT @transaction_count = COUNT(*) FROM [dbo].[TRANSACTION];
    PRINT 'TRANSACTION table: ✓ EXISTS (' + CAST(@transaction_count AS VARCHAR) + ' records)';
END
ELSE
BEGIN
    PRINT 'TRANSACTION table: ✗ MISSING';
END

-- Check USERS table  
IF EXISTS (SELECT * FROM sysobjects WHERE name='USERS' AND xtype='U')
BEGIN
    DECLARE @user_count INT;
    SELECT @user_count = COUNT(*) FROM [dbo].[USERS];
    PRINT 'USERS table: ✓ EXISTS (' + CAST(@user_count AS VARCHAR) + ' users)';
END
ELSE
BEGIN
    PRINT 'USERS table: ✗ MISSING';
END

-- Check user permissions
IF EXISTS (SELECT * FROM sys.database_principals WHERE name = 'django_readonly')
BEGIN
    PRINT 'Read-only user: ✓ EXISTS';
END
ELSE
BEGIN
    PRINT 'Read-only user: ⚠ NOT CREATED (you may need DBA assistance)';
END

PRINT '=====================================================';
PRINT 'SETUP COMPLETE - TRULY MINIMAL DATABASE!';
PRINT '=====================================================';
PRINT '';
PRINT 'DATABASE SUMMARY:';
PRINT '• Total tables required: 2 (TRANSACTION + USERS)';
PRINT '• Django framework tables: 0 (all disabled!)';
PRINT '• Session storage: In-memory cache (no database)';
PRINT '• Migrations: Completely disabled';
PRINT '• Write permissions: Not required';
PRINT '';
PRINT 'NEXT STEPS:';
PRINT '1. Update Django settings.py with correct database credentials';
PRINT '2. Test connection: python manage.py check_readonly';
PRINT '3. Start application: python manage.py runserver 0.0.0.0:8000';
PRINT '';
PRINT 'DJANGO CONFIGURATION:';
PRINT 'DATABASES = {';
PRINT '    "default": {';
PRINT '        "ENGINE": "mssql",';
PRINT '        "NAME": "ZAKTOLL",';
PRINT '        "USER": "django_readonly",  # or your existing user';
PRINT '        "PASSWORD": "your_password",';
PRINT '        "HOST": "115.127.158.186",';
PRINT '        "OPTIONS": {';
PRINT '            "driver": "ODBC Driver 18 for SQL Server",';
PRINT '            "extra_params": "TrustServerCertificate=yes;",';
PRINT '        },';
PRINT '    }';
PRINT '}';
PRINT '';
PRINT 'SESSIONS = In-memory cache (no django_session table needed)';
PRINT 'MIGRATIONS = Completely disabled for all apps';
PRINT '';
PRINT 'IMPORTANT: This application requires ONLY read permissions!';
PRINT 'Zero Django framework tables needed - sessions use memory cache.';
GO 