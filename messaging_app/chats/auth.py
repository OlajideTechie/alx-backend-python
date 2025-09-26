from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication
)
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomAuthentication:
    """
    Custom authentication that supports:
    - JWT (via djangorestframework-simplejwt)
    - SessionAuthentication (useful for browsable API)
    - BasicAuthentication (username:password in headers)
    """

    def __init__(self):
        self.jwt_auth = JWTAuthentication()
        self.session_auth = SessionAuthentication()
        self.basic_auth = BasicAuthentication()

    def authenticate(self, request):
        # Try JWT first
        try:
            result = self.jwt_auth.authenticate(request)
            if result is not None:
                return result
        except Exception:
            pass

        # Try Basic Authentication next
        try:
            result = self.basic_auth.authenticate(request)
            if result is not None:
                return result
        except Exception:
            pass

        # Finally fall back to Session Authentication
        return self.session_auth.authenticate(request)