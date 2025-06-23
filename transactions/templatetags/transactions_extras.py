from django import template
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
import pytz
from transactions.models import Transaction

register = template.Library()

@register.filter
def sequential_number(page_obj, counter):
    """Calculate sequential number across pagination"""
    if hasattr(page_obj, 'number') and hasattr(page_obj, 'paginator'):
        per_page = page_obj.paginator.per_page
        page_number = page_obj.number
        return ((page_number - 1) * per_page) + counter
    return counter

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

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)

@register.filter
def utc_date(value, format_str="M d, Y"):
    """Display datetime in UTC timezone with specified format"""
    if not value:
        return ""
    
    # Convert to UTC if timezone-aware
    if timezone.is_aware(value):
        utc_value = value.astimezone(pytz.UTC)
    else:
        utc_value = value
    
    # Use Django's date filter format
    from django.template.defaultfilters import date
    return date(utc_value, format_str)

@register.filter
def utc_time(value, format_str="g:i A"):
    """Display time in UTC timezone with specified format"""
    if not value:
        return ""
    
    # Convert to UTC if timezone-aware
    if timezone.is_aware(value):
        utc_value = value.astimezone(pytz.UTC)
    else:
        utc_value = value
    
    # Use Django's time filter format
    from django.template.defaultfilters import time
    return time(utc_value, format_str)

@register.filter
def utc_datetime(value, format_str="M d, Y g:i A"):
    """Display datetime in UTC timezone with specified format"""
    if not value:
        return ""
    
    # Convert to UTC if timezone-aware
    if timezone.is_aware(value):
        utc_value = value.astimezone(pytz.UTC)
    else:
        utc_value = value
    
    # Use Django's date filter format
    from django.template.defaultfilters import date
    return date(utc_value, format_str) 