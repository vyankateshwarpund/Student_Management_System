"""Views for user authentication and management."""
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

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
