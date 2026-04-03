from rest_framework import permissions

class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Allow access to profile endpoint for all authenticated users
        if view.action == 'profile':
            return True
        
        # Admin can do everything
        if request.user.is_admin:
            return True
        
        # List and retrieve - users can view their own profile
        if view.action in ['list', 'retrieve']:
            return True
        
        # Create - only admin
        if view.action == 'create':
            return False
        
        # Update - only admin or self
        if view.action in ['update', 'partial_update']:
            return True
        
        # Delete - only admin
        if view.action == 'destroy':
            return False
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Allow access to profile for own user
        if view.action == 'profile':
            return True
        
        # Admin can access any user
        if request.user.is_admin:
            return True
        
        # Users can access their own profile
        return obj.id == request.user.id