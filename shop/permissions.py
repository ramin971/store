from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    The request is admin as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and
            request.user.is_staff
        )
    

class IsAdminOrIsAuthenticated(permissions.BasePermission):
    """
    The request is admin as a user, or is a authenticated user.
    """

    def has_permission(self, request, view):
        # return True
        if request.method in permissions.SAFE_METHODS :
            return bool(request.user and request.user.is_staff)
        return bool(
            # request.method in permissions.SAFE_METHODS and 
            # request.user and
            # request.user.is_staff or
            request.user and
            request.user.is_authenticated
        )