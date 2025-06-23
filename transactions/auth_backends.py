from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class TollUserBackend(BaseBackend):
    """
    Custom authentication backend for TollUser model
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
            
        try:
            # Get user from USERS table
            user = User.objects.get(username=username)
            
            # Check if user is active
            if not user.active:
                return None
                
            # Check if user has allowed role (handle both old and new role names)
            allowed_roles = [
                'admin', 'webadmin', 'webuser',  # New role names
                'ADMIN', 'OPERATOR'  # Existing role names in database
            ]
            if user.role not in allowed_roles:
                return None
                
            # Check password
            if user.check_password(password):
                # Note: Not updating lastLogin to maintain read-only database compliance
                # user.lastLogin = timezone.now()
                # user.save(update_fields=['lastLogin'])
                return user
                
        except User.DoesNotExist:
            # Run a dummy password check to prevent timing attacks
            User().set_password(password)
            return None
            
        return None
    
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return user if user.active else None
        except User.DoesNotExist:
            return None
    
    def user_can_authenticate(self, user):
        """
        Reject users with active=False and roles not in allowed list
        """
        allowed_roles = [
            'admin', 'webadmin', 'webuser',  # New role names
            'ADMIN', 'OPERATOR'  # Existing role names in database
        ]
        return (
            getattr(user, 'active', True) and 
            getattr(user, 'role', None) in allowed_roles
        ) 