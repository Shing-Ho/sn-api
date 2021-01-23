from rest_framework import serializers

# from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# from rest_framework.validators import UniqueValidator

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ("id", "username", "email")

# # Register Serializer
# class RegisterSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
#     username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())])
#     password = serializers.CharField(min_length=8)

#     class Meta:
#         model = User
#         fields = ("id", "username", "email", "password")
#         extra_kwargs = {"password": {"write_only": True}}

#     def create(self, validated_data):
#         user = User.objects.create_user(validated_data["username"],
# validated_data["email"], validated_data["password"])

#         return user


# # Change Password
# class ChangePasswordSerializer(serializers.Serializer):
#     model = User
#     old_password = serializers.CharField(required=True)
#     new_password = serializers.CharField(required=True)


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source="key")

    class Meta:
        model = Token
        fields = ("token",)
