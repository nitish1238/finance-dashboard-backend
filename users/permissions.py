
from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        
        if view.action == 'profile':
            return True

        
        if view.action == 'change_password':
            return True

        
        if request.user.is_admin:
            return True

       
        if view.action in ['list', 'retrieve']:
            return True

        # Create - only admin
        if view.action == 'create':
            return False

        
        if view.action in ['update', 'partial_update']:
            return True

        
        if view.action == 'destroy':
            return False

        return False

    def has_object_permission(self, request, view, obj):
        # Allow access to profile for own user
        if view.action == 'profile':
            return True

       
        if request.user.is_admin:
            return True

        
        return obj.id == request.user.id