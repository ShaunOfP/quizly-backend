from rest_framework import permissions

class AuthenticatedViaRefreshToken(permissions.BasePermission):
    """
    Custom permission to check if the user is authenticated via a valid refresh token.
    """

    def has_permission(self, request, view):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return False
        return True