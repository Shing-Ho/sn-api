from rest_framework.authentication import TokenAuthentication


class TokenAuthSupportQueryString(TokenAuthentication):
    def authenticate(self, request):
        if "auth_token" in request.query_params:
            auth_token = request.query_params.get("auth_token")
            return self.authenticate_credentials(auth_token)
        else:
            return super().authenticate(request)
