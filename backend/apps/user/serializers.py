from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.save()
        return user

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "password")


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)


class GenerateResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
