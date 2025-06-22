from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'sequence', 'plazaid', 'plazaname', 'lane', 'collectorid', 
        'capturedate', 'transtype', 'vehicle_class', 'regnumber', 
        'get_payment_type_display', 'get_formatted_fare'
    ]
    list_filter = [
        'capturedate', 'lane', 'vehicle_class', 'paytype', 'transtype'
    ]
    search_fields = [
        'sequence', 'regnumber', 'collectorid', 'lane'
    ]
    date_hierarchy = 'capturedate'
    list_per_page = 25
    readonly_fields = [
        'plazaid', 'plazaname', 'lane', 'sequence', 'collectorid',
        'capturedate', 'transtype', 'vehicle_class', 'regnumber',
        'fare', 'paytype', 'pic', 'shift'
    ]
    
    def has_add_permission(self, request):
        # Prevent adding new transactions through admin
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deleting transactions through admin
        return False
    
    def has_change_permission(self, request, obj=None):
        # Make transactions read-only in admin
        return False
