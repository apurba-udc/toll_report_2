from django import template
import base64

register = template.Library()

@register.filter
def to_base64(binary_data):
    """Convert binary image data to base64 string for HTML display"""
    if binary_data and isinstance(binary_data, bytes):
        try:
            return base64.b64encode(binary_data).decode('utf-8')
        except Exception:
            return None
    return None

@register.filter
def format_currency(value):
    """Format currency with commas and 2 decimal places"""
    if value is None:
        return "0.00"
    try:
        return f"{float(value):,.2f}"
    except (ValueError, TypeError):
        return "0.00"

@register.filter
def lookup(dictionary, key):
    """Template filter to dynamically lookup dictionary keys"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, 0)
    else:
        # If it's an object, try to get the attribute
        try:
            return getattr(dictionary, key, 0)
        except (AttributeError, TypeError):
            return 0

@register.filter
def add(value, arg):
    """Add two values together (useful for string concatenation)"""
    try:
        return str(value) + str(arg)
    except (ValueError, TypeError):
        return value 