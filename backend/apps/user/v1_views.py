import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from unique_names_generator import get_random_name
from unique_names_generator.data import ANIMALS

from apps.smear.pagination import SmearPagination
from apps.user.email import send_password_reset_email
from apps.user.permissions import IsOwnerPermission
from apps.user.serializers import (
    ChangePasswordSerializer,
    GenerateResetSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)

LOG = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    serializer_class = UserSerializer
    ordering = "-date_joined"
    pagination_class = SmearPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        else:
            return User.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == "POST":
            self.permission_classes = [
                AllowAny,
            ]
        else:
            self.permission_classes = [
                IsOwnerPermission,
            ]
        return super(UserViewSet, self).get_permissions()

    def create(self, request, *args, **kwargs):
        # This is a hack because extending the User model is a pain
        is_anonymous_arg = request.data.get("is_anonymous", "false")
        is_anonymous = is_anonymous_arg.lower() == "true"
        if is_anonymous:
            request.data["email"] = settings.ANONYMOUS_EMAIL
            request.data["first_name"] = f"Anon. {get_random_name(combo=[ANIMALS])}"
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def changepassword(self, request):
        user = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(serializer.data["old_password"]):
            return Response({"old_password", "Unable to verify current password"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.data["new_password"])
        user.save()
        return Response({"status": "password set"})

    @action(detail=False, methods=["post"])
    def generatereset(self, request):
        serializer = GenerateResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=serializer.data["email"])
        except User.DoesNotExist:
            return Response({"email", "Could not find user with specified email"}, status=status.HTTP_400_BAD_REQUEST)

        reset_token = default_token_generator.make_token(user)

        success = send_password_reset_email(user.username, reset_token)

        if not success:
            return Response(
                {"error", "Unable to send password reset email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({"status": "email sent"})

    @action(detail=False, methods=["post"])
    def resetpassword(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=serializer.data["email"])
        except User.DoesNotExist:
            return Response({"email", "Could not find user with specified email"}, status=status.HTTP_400_BAD_REQUEST)

        valid = default_token_generator.check_token(user, serializer.data["token"])

        if not valid:
            return Response({"error", "Unable to validate password reset code"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.data["new_password"])
        user.save()
        return Response({"status": "password reset"})

    @action(
        detail=False,
        methods=["get"],
        url_path="cleanup-anonymous",
        url_name="cleanup-anonymous",
    )
    def cleanup_anonymous(self, request):
        one_month = timezone.now() - timedelta(days=31)
        old_anonymous_users = User.objects.filter(email=settings.ANONYMOUS_EMAIL, date_joined__lte=one_month)
        num_objects, results = old_anonymous_users.delete()
        LOG.info(f"Deleted {num_objects} objects from anonymous users")
        return Response({"status": "success", "num_objects": num_objects, "results": results})
