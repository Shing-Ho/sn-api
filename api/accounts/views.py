from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from bearer_auth.models import AccessToken
from bearer_auth.settings import token_settings

# from django.contrib.auth import login

# from rest_framework.authtoken.serializers import AuthTokenSerializer
# from knox.views import LoginView as KnoxLoginView

# from rest_framework import generics, permissions, status
# from rest_framework.response import Response
# from knox.models import AuthToken
# #from .serializers import UserSerializer, RegisterSerializer, ChangePasswordSerializer
# from django.views.decorators.debug import sensitive_post_parameters
# from django.contrib.auth.models import User
# from rest_framework.permissions import IsAuthenticated

# from rest_framework.views import APIView


class LoginAPI(ObtainAuthToken):
    model = AccessToken
    serializer_class = AuthTokenSerializer

    def post(self, request):
        data = request.data
        data["grant_type"] = "password"
        serializer = self.serializer_class(data=data, context={"request": request})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token = AccessToken.objects.create(user=user)
            return Response(
                {
                    "token_type": "Bearer",
                    "access_token": token.key,
                    "refresh_token": token.refresh_token,
                    "expires_in": token_settings.TOKEN_EXPIRES_IN,
                }
            )
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


# # Register API
# class RegisterAPI(generics.GenericAPIView):
#     serializer_class = RegisterSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         return Response({
#             "user": UserSerializer(user, context=self.get_serializer_context()).data,
#             "token": AuthToken.objects.create(user)[1]
#         })

# # Login API
# class LoginAPI(KnoxLoginView):
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request, format=None):
#         serializer = AuthTokenSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         login(request, user)
#         return super(LoginAPI, self).post(request, format=None)

# # Get User API
# class UserAPI(generics.RetrieveAPIView):
#     permission_classes = [permissions.IsAuthenticated,]
#     serializer_class = UserSerializer

#     def get_object(self):
#         return self.request.user


# # Change Password
# class ChangePasswordView(generics.UpdateAPIView):
#     serializer_class = ChangePasswordSerializer
#     model = User
#     permission_classes = (IsAuthenticated,)

#     def get_object(self, queryset=None):
#         obj = self.request.user
#         return obj

#     def update(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         serializer = self.get_serializer(data=request.data)

#         if serializer.is_valid():
#             # Check old password
#             if not self.object.check_password(serializer.data.get("old_password")):
#                 return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
#             # set_password also hashes the password that the user will get
#             self.object.set_password(serializer.data.get("new_password"))
#             self.object.save()
#             response = {
#                 'status': 'success',
#                 'code': status.HTTP_200_OK,
#                 'message': 'Password updated successfully',
#                 'data': []
#             }

#             return Response(response)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
