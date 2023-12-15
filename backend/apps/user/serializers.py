from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.CharField(write_only=True, default="")
    is_anonymous = serializers.SerializerMethodField()

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.save()
        return user

    def get_is_anonymous(self, user):
        # This is a hack because extending the User model is a pain
        return user.email == settings.ANONYMOUS_EMAIL

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "password", "email", "is_anonymous")


class UserSummarySerializer(serializers.ModelSerializer):
    is_anonymous = serializers.SerializerMethodField()

    def get_is_anonymous(self, user):
        # This is a hack because extending the User model is a pain
        return user.email == "is_anonymous@playsmear.com"

    class Meta:
        model = User
        fields = ("id", "username", "is_anonymous", "first_name")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)


class GenerateResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
