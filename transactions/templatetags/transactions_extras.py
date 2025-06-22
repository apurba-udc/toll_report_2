from django import template
from django.db.models import Q
from transactions.models import Transaction

register = template.Library()

@register.filter
def get_exempt_by_lane_count(lane, max_date, min_date):
    """Get exempt count by lane"""
    count = Transaction.objects.filter(
        capturedate__lte=max_date,
        capturedate__gte=min_date,
        lane=lane,
        paytype='VCH'
    ).exclude(
        transtype__in=['LOGIN', 'LOGOUT']
    ).exclude(
        vehicle_class__in=['0', '', None]
    ).count()
    
    return count if count else 0

@register.filter
def get_exempt_by_class_count(lane, vehicle_class, max_date, min_date):
    """Get exempt count by class and lane"""
    count = Transaction.objects.filter(
        capturedate__lte=max_date,
        capturedate__gte=min_date,
        lane=lane,
        vehicle_class=vehicle_class,
        paytype='VCH'
    ).exclude(
        transtype__in=['LOGIN', 'LOGOUT']
    ).exclude(
        vehicle_class__in=['0', '', None]
    ).count()
    
    return count if count else 0 