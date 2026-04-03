from rest_framework import permissions

class RoleBasedPermission(permissions.BasePermission):
    """
    Permission class for role-based access control
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Define action requirements
        action_requirements = {
            'list': ['viewer', 'analyst', 'admin'],
            'retrieve': ['viewer', 'analyst', 'admin'],
            'create': ['analyst', 'admin'],
            'update': ['analyst', 'admin'],
            'partial_update': ['analyst', 'admin'],
            'destroy': ['admin'],
        }
        
        action = getattr(view, 'action', None)
        if action and action in action_requirements:
            return request.user.role in action_requirements[action]
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # Admin can access any object
        if request.user.role == 'admin':
            return True
        
        # Users can only access their own objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return True

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsAnalyst(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'analyst'

class IsViewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'viewer'