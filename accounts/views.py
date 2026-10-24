"""Views for user authentication and management."""
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsAdmin
from utils.response import (
    success_response,
    created_response,
    error_response,
)


class RegisterView(APIView):
    """Public self-registration is permanently disabled for privacy and security.
    Only Institute Administrators can provision user accounts via /api/users/.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        return error_response(
            message='Public registration is disabled. All Student and Teacher accounts must be created exclusively by the Administrator.',
            status_code=status.HTTP_403_FORBIDDEN
        )



class LoginView(APIView):
    """Authenticate user and return JWT tokens.

    POST /api/auth/login/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return success_response(
                data={
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    },
                },
                message='Login successful',
            )
        return error_response(
            message='Login failed',
            errors=serializer.errors,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutView(APIView):
    """Blacklist the refresh token to logout.

    POST /api/auth/logout/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return error_response(message='Refresh token is required')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return success_response(message='Logout successful')
        except Exception:
            return error_response(message='Invalid or expired token')


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile.

    GET /api/auth/profile/
    PATCH /api/auth/profile/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response(
            data=serializer.data,
            message='Profile retrieved successfully',
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data,
            partial=partial,
        )
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message='Profile updated successfully',
            )
        return error_response(
            message='Profile update failed',
            errors=serializer.errors,
        )


class ChangePasswordView(APIView):
    """Change the authenticated user's password.

    POST /api/auth/change-password/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return success_response(message='Password changed successfully')
        return error_response(
            message='Password change failed',
            errors=serializer.errors,
        )


class ForgotPasswordRequestView(APIView):
    """Initiate password reset request using email or username.

    POST /api/auth/forgot-password/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        identity = (request.data.get('identity') or request.data.get('email') or request.data.get('username') or '').strip()
        if not identity:
            return error_response(
                message='Please provide your registered Username or Email address.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(username__iexact=identity).first()
        if not user:
            user = User.objects.filter(email__iexact=identity).first()

        if user and user.is_active:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"/reset-password/?uid={uid}&token={token}"

            # If user has an email, dispatch message
            if user.email:
                subject = "EduManager — Password Reset Request"
                message = (
                    f"Hello {user.get_full_name() or user.username},\n\n"
                    f"A password reset request was received for your EduManager account.\n\n"
                    f"You can reset your password using the following link:\n"
                    f"{request.build_absolute_uri(reset_link)}\n\n"
                    f"UID: {uid}\n"
                    f"Token: {token}\n\n"
                    f"If you did not request this, please contact your College Administrator."
                )
                try:
                    send_mail(
                        subject,
                        message,
                        getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@edumanager.local'),
                        [user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

            return success_response(
                data={
                    'uid': uid,
                    'token': token,
                    'reset_url': reset_link,
                    'email_hint': f"{user.email[:2]}***@{user.email.split('@')[-1]}" if user.email and '@' in user.email else None
                },
                message='Password reset instructions generated successfully.',
            )

        # For security / non-existent user:
        return success_response(
            message='If an account exists with this credential, reset instructions have been dispatched.',
        )


class ResetPasswordConfirmView(APIView):
    """Confirm password reset with token and new password.

    POST /api/auth/reset-password-confirm/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = (request.data.get('new_password') or '').strip()

        if not uidb64 or not token or not new_password:
            return error_response(
                message='UID, Token, and New Password are required.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password) < 8:
            return error_response(
                message='Password must be at least 8 characters long.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return error_response(
                message='Invalid or corrupted reset link.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return error_response(
                message='Reset token is invalid or has expired. Please request a fresh reset link.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return success_response(
            message='Password has been reset successfully! You can now log in with your new password.',
        )


class UserViewSet(viewsets.ModelViewSet):
    """Admin-only CRUD for managing users.

    GET    /api/users/
    POST   /api/users/
    GET    /api/users/{id}/
    PUT    /api/users/{id}/
    PATCH  /api/users/{id}/
    DELETE /api/users/{id}/
    POST   /api/users/{id}/reset-password/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filterset_fields = ['role', 'is_active']
    ordering_fields = ['username', 'email', 'date_joined', 'role']
    ordering = ['-date_joined']

    def get_queryset(self):
        qs = super().get_queryset()
        # Security Guardrail: Non-super admin cannot list or query superuser accounts
        if not self.request.user.is_superuser:
            qs = qs.exclude(is_superuser=True)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data=serializer.data,
            message='Users retrieved successfully',
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Security Guardrail 1: Admin cannot access Super Admin's account without authorization
        if instance.is_superuser and not request.user.is_superuser:
            return error_response(
                message="Cannot view or access Super Administrator account without authorization.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(instance)
        return success_response(
            data=serializer.data,
            message='User retrieved successfully',
        )

    def create(self, request, *args, **kwargs):
        # Security Guardrails: Privileged escalation checks
        if not request.user.is_superuser:
            if request.data.get('is_superuser') or request.data.get('is_staff'):
                return error_response(
                    message="Only Super Administrators can create or grant Super Administrator privileges.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            if request.data.get('role') == 'admin':
                return error_response(
                    message="Only Super Administrators can provision new Administrator accounts.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return created_response(
                data=self.get_serializer(user).data,
                message='User account created successfully',
            )
        return error_response(
            message='User creation failed',
            errors=serializer.errors,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Security Guardrail 1: Admin cannot change Super Admin account
        if instance.is_superuser and not request.user.is_superuser:
            return error_response(
                message="Cannot change or modify Super Administrator account without authorization.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # Security Guardrail 7: Admin cannot change another administrator's permissions unless authorized
        if instance.role == 'admin' and instance != request.user and not request.user.is_superuser:
            return error_response(
                message="Cannot modify another Administrator's account or permissions unless authorized as Super Administrator.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # Non-superusers cannot escalate privileges
        if not request.user.is_superuser:
            if 'is_superuser' in request.data or 'is_staff' in request.data:
                return error_response(
                    message="Permission denied: Modifying superuser or staff status is restricted to Super Administrators.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            if 'role' in request.data and request.data['role'] == 'admin' and instance.role != 'admin':
                return error_response(
                    message="Permission denied: Promoting accounts to Administrator requires Super Administrator authorization.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            user = serializer.save()
            return success_response(
                data=self.get_serializer(user).data,
                message='User updated successfully',
            )
        return error_response(
            message='User update failed',
            errors=serializer.errors,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Prevent deactivating own account
        if instance == request.user:
            return error_response(
                message="You cannot deactivate your own administrative account.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Security Guardrail 1: Admin cannot deactivate or delete Super Admin account
        if instance.is_superuser and not request.user.is_superuser:
            return error_response(
                message="Cannot deactivate or delete Super Administrator account without authorization.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # Security Guardrail 7: Admin cannot change another administrator's permissions / deactivate
        if instance.role == 'admin' and not request.user.is_superuser:
            return error_response(
                message="Cannot deactivate another Administrator's account unless authorized as Super Administrator.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # Security Guardrail 2: Soft delete instead of permanent deletion
        instance.is_active = False
        instance.save()
        return success_response(message='User account deactivated successfully')

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        """Admin reset password for a user."""
        instance = self.get_object()

        # Security Guardrail 1: Admin cannot change Super Admin's account
        if instance.is_superuser and not request.user.is_superuser:
            return error_response(
                message="Cannot reset Super Administrator password without authorization.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # Security Guardrail 7: Admin cannot change another administrator's permissions/password
        if instance.role == 'admin' and instance != request.user and not request.user.is_superuser:
            return error_response(
                message="Cannot reset another Administrator's password without Super Administrator authorization.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        new_password = request.data.get('new_password')
        if not new_password or len(str(new_password).strip()) < 8:
            return error_response(
                message="New password must be provided and must be at least 8 characters long.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        instance.set_password(str(new_password).strip())
        instance.save()
        return success_response(message=f"Password for user '{instance.username}' reset successfully.")
