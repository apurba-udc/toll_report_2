from django.db import models
from django.contrib.auth.models import User


class Transaction(models.Model):
    """
    Model representing toll transaction data
    This maps to the TRANSACTION table in MSSQL
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
    
    class Meta:
        db_table = '[TRANSACTION]'  # Escaped table name for SQL Server
        managed = False  # This is a database view, not managed by Django
        ordering = ['-capturedate']
    
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
            'E101': 'Emergency Lane',
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
