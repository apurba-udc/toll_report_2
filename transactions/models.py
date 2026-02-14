from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import PermissionDenied
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone


class ReadOnlyManager(models.Manager):
    """
    Manager that prevents any write operations on Transaction table
    """
    def create(self, **kwargs):
        raise PermissionDenied("Transaction টেবিলে কোনো নতুন ডেটা যোগ করা নিষিদ্ধ। এটি read-only টেবিল।")
    
    def bulk_create(self, objs, **kwargs):
        raise PermissionDenied("Transaction টেবিলে bulk create অনুমতিত নয়।")
    
    def update(self, **kwargs):
        raise PermissionDenied("Transaction টেবিলে কোনো আপডেট অনুমতিত নয়।")
    
    def bulk_update(self, objs, fields, **kwargs):
        raise PermissionDenied("Transaction টেবিলে bulk update অনুমতিত নয়।")
    
    def delete(self):
        raise PermissionDenied("Transaction টেবিল থেকে কোনো ডেটা ডিলিট করা নিষিদ্ধ।")


class Transaction(models.Model):
    """
    Model representing toll transaction data
    This maps to the TRANSACTION table in MSSQL
    IMPORTANT: This table is READ-ONLY - no modifications allowed
    """
    
    # Table fields based on Laravel controller usage
    plazaid = models.CharField(max_length=10, db_column='PLAZAID', blank=True, null=True)
    plazaname = models.CharField(max_length=100, db_column='PLAZANAME', blank=True, null=True)
    lane = models.CharField(max_length=10, db_column='LANE', blank=True, null=True)
    sequence = models.CharField(max_length=20, db_column='SEQUENCE', primary_key=True)
    collectorid = models.CharField(max_length=20, db_column='COLLECTORID', blank=True, null=True)
    capturedate = models.DateTimeField(db_column='CAPTUREDATE', blank=True, null=True)
    transtype = models.CharField(max_length=20, db_column='TRANSTYPE', blank=True, null=True)
    vehicle_class = models.CharField(max_length=5, db_column='CLASS', blank=True, null=True)  # renamed from class to avoid Python keyword
    regnumber = models.CharField(max_length=20, db_column='REGNUMBER', blank=True, null=True)
    fare = models.DecimalField(max_digits=10, decimal_places=2, db_column='FARE', blank=True, null=True)
    paytype = models.CharField(max_length=10, db_column='PAYTYPE', blank=True, null=True)
    pic = models.BinaryField(db_column='PIC', blank=True, null=True)  # Binary image data
    shift = models.CharField(max_length=10, db_column='SHIFT', blank=True, null=True)
    exempttype = models.CharField(max_length=50, db_column='EXEMPTTYPE', blank=True, null=True)
    
    objects = ReadOnlyManager()  # Custom manager to prevent modifications
    
    class Meta:
        db_table = 'TRANSACTION'  # Direct table name for MSSQL
        managed = False  # This table exists in ZAKTOLL database, Django doesn't manage it
        ordering = ['-capturedate']
        default_permissions = ()  # No default permissions for this model
    
    def save(self, *args, **kwargs):
        raise PermissionDenied("Transaction টেবিলে কোনো পরিবর্তন অনুমতিত নয়। এটি read-only টেবিল।")
    
    def delete(self, *args, **kwargs):
        raise PermissionDenied("Transaction টেবিল থেকে কোনো ডেটা ডিলিট করা নিষিদ্ধ।")
    
    def __str__(self):
        return f"Transaction {self.sequence} - Lane {self.lane} - {self.capturedate}"
    
    @property
    def get_payment_type_display(self):
        """Convert payment type codes to display names"""
        payment_types = {
            'CSH': 'Cash',
            'VCH': 'Exempt',
            'TnG': 'T&G',
            'ETC': 'ETC',
        }
        return payment_types.get(self.paytype, self.paytype)
    
    @property
    def get_vehicle_type_display(self):
        """Get vehicle type display name"""
        vehicle_types = {
            '1': 'Motorcycle',
            '2': 'Car/Jeep',
            '3': 'Small Truck',
            '4': 'Medium Truck',
            '5': 'Large Truck',
            '6': 'Bus',
            '7': 'Large Bus',
            '8': 'Trailer',
            '9': 'Multi-Axle',
            '10': 'Special Vehicle',
            '0': 'Violation'
        }
        return vehicle_types.get(self.vehicle_class, f"Class {self.vehicle_class}")
    
    @property
    def get_lane_display(self):
        """Get lane display name"""
        lane_names = {
            'E101': 'ECR 1',
            'L101': 'Lane 1',
            'L102': 'Lane 2', 
            'L103': 'Lane 3',
            'L104': 'Lane 4',
            'L105': 'Lane 5',
            'L106': 'Lane 6',
            'L107': 'Lane 7',
            'L108': 'Lane 8',
            'L109': 'Lane 9',
            'L110': 'Lane 10',
            'L112': 'Lane 12',
            # Add more lane mappings as needed
        }
        return lane_names.get(self.lane, self.lane or 'Unknown Lane')
    
    @property
    def get_formatted_fare(self):
        """Get formatted fare with 2 decimal places"""
        if self.fare:
            return f"{self.fare:.2f}"
        return "0.00"


class ExemptList(models.Model):
    """
    Model representing exempt list data
    This maps to the EXEMT_LIST table in MSSQL
    IMPORTANT: This table is READ-ONLY - no modifications allowed
    """
    
    # Table structure based on actual database schema
    id = models.IntegerField(db_column='ID', primary_key=True)
    reg_number = models.CharField(max_length=30, db_column='REG_NUMBER', blank=True, null=True)
    owner_name = models.CharField(max_length=30, db_column='OWNER_NAME', blank=True, null=True)
    owner_group = models.CharField(max_length=30, db_column='OWNER_GROUP', blank=True, null=True)
    reference = models.CharField(max_length=30, db_column='REFERENCE', blank=True, null=True)
    contact_number = models.CharField(max_length=30, db_column='CONTACT_NUMBER', blank=True, null=True)
    approved_by = models.CharField(max_length=30, db_column='APPROVED_BY', blank=True, null=True)
    comments = models.CharField(max_length=30, db_column='COMMENTS', blank=True, null=True)
    pic = models.BinaryField(db_column='PIC', blank=True, null=True)
    suspended = models.BooleanField(db_column='SUSPENDED', blank=True, null=True)
    date_created = models.DateTimeField(db_column='DATE_CREATED', blank=True, null=True)
    
    # Backward compatibility properties
    @property
    def registration(self):
        return self.reg_number
    
    @property
    def owner(self):
        return self.owner_name
    
    objects = ReadOnlyManager()  # Custom manager to prevent modifications
    
    class Meta:
        db_table = 'EXEMT_LIST'  # Direct table name for MSSQL (note: EXEMT not EXEMPT)
        managed = False  # This table exists in ZAKTOLL database, Django doesn't manage it
        default_permissions = ()  # No default permissions for this model
    
    def save(self, *args, **kwargs):
        raise PermissionDenied("EXEMPT_LIST টেবিলে কোনো পরিবর্তন অনুমতিত নয়। এটি read-only টেবিল।")
    
    def delete(self, *args, **kwargs):
        raise PermissionDenied("EXEMPT_LIST টেবিল থেকে কোনো ডেটা ডিলিট করা নিষিদ্ধ।")
    
    def __str__(self):
        return f"Exempt {self.reg_number} - {self.owner_name}"


class CustomUserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(username=username)

class TollUser(AbstractBaseUser):
    """Custom User model mapping to USERS table"""
    userId = models.CharField(max_length=20, primary_key=True, db_column='userId')
    username = models.CharField(max_length=50, unique=True, db_column='username')
    password = models.CharField(max_length=128, db_column='password')
    name = models.CharField(max_length=100, db_column='name')
    role = models.CharField(max_length=20, db_column='role')
    active = models.BooleanField(default=True, db_column='active')
    createdDate = models.DateTimeField(auto_now_add=True, db_column='createdDate')
    lastLogin = models.DateTimeField(null=True, blank=True, db_column='lastLogin')
    
    # Override the last_login field from AbstractBaseUser to use our lastLogin field
    last_login = None  # Disable the inherited last_login field
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'USERS'
        managed = False  # Don't let Django manage this table
    
    def __str__(self):
        return self.username
    
    @property
    def is_active(self):
        return self.active
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def has_perm(self, perm, obj=None):
        """Check if user has permission"""
        # Allow admin/ADMIN full access
        if self.role.lower() in ['admin'] or self.role.upper() in ['ADMIN']:
            return True
        # Allow webadmin and operators basic access
        if self.role.lower() in ['webadmin', 'webuser'] or self.role.upper() in ['OPERATOR']:
            return True
        return False
    
    def has_perms(self, perm_list, obj=None):
        """Check if user has all permissions in list"""
        return all(self.has_perm(perm, obj) for perm in perm_list)
    
    def has_module_perms(self, app_label):
        """Check if user has permissions for app"""
        allowed_roles = ['admin', 'webadmin', 'webuser', 'ADMIN', 'OPERATOR']
        return self.role in allowed_roles
    
    def check_password(self, raw_password):
        """Check password - assuming passwords are stored as plain text in your DB"""
        # If passwords are hashed, use: return check_password(raw_password, self.password)
        # If passwords are plain text (not recommended), use:
        return self.password == raw_password
    
    def set_password(self, raw_password):
        """Set password"""
        # If you want to hash passwords: self.password = make_password(raw_password)
        # If keeping plain text: self.password = raw_password
        self.password = raw_password
