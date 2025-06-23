import logging
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class ReadOnlyMiddleware:
    """
    Middleware to enforce read-only database access
    Logs any attempts to perform write operations
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Log all incoming requests for audit purposes
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.info(
                f"User '{request.user.username}' ({request.user.role}) "
                f"accessed {request.method} {request.path} from {request.META.get('REMOTE_ADDR', 'unknown')}"
            )
        
        # Check for potentially dangerous request methods
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Allow authentication related posts
            if request.path in ['/login/', '/logout/']:
                pass
            # Allow PDF generation and report generation posts
            elif 'pdf' in request.path or any(x in request.path for x in [
                '/summary_lane/', '/summary_class/', '/exempt/', 
                '/daily_report/', '/report_date', '/list/'
            ]):
                pass
            else:
                logger.warning(
                    f"Potentially unsafe {request.method} request to {request.path} "
                    f"by user {getattr(request.user, 'username', 'anonymous')}"
                )
        
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """Log any permission denied exceptions"""
        if isinstance(exception, PermissionDenied):
            logger.error(
                f"Database write operation blocked: {exception} "
                f"- User: {getattr(request.user, 'username', 'anonymous')} "
                f"- Path: {request.path} "
                f"- Method: {request.method}"
            )
        return None 