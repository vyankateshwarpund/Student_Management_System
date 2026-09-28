"""Views for teacher management."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Teacher
from .serializers import TeacherSerializer
from accounts.permissions import IsAdmin, IsAdminOrReadOnly, IsAdminOrTeacher
from utils.response import success_response, created_response, error_response


class TeacherViewSet(viewsets.ModelViewSet):
    """
    CRUD for Teachers.
    Admin has full control.
    Others have read-only access.
    """
    queryset = Teacher.objects.select_related('user', 'department').prefetch_related('subjects')
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['department']
    search_fields = [
        'employee_id', 'user__first_name', 'user__last_name',
        'user__email', 'user__username', 'department__name',
    ]
    ordering_fields = ['employee_id', 'user__first_name', 'created_at']
    ordering = ['user__first_name']

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message='Teachers retrieved successfully')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message='Teacher retrieved successfully')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            teacher = serializer.save()
            return created_response(data=self.get_serializer(teacher).data, message='Teacher profile created successfully')
        return error_response(message='Failed to create teacher profile', errors=serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if request.user.role == 'teacher' and instance.user != request.user:
            return error_response(
                message="You cannot access or modify another faculty member's private profile.",
                status_code=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            teacher = serializer.save()
            return success_response(data=self.get_serializer(teacher).data, message='Teacher profile updated successfully')
        return error_response(message='Failed to update teacher profile', errors=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Security Guardrail 2: Admin cannot permanently delete critical records without superuser authorization
        if request.query_params.get('hard_delete') == 'true':
            if not request.user.is_superuser:
                return error_response(
                    message="Permanent deletion of faculty records requires Super Administrator authorization. Please deactivate the teacher instead.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            instance.delete()
            return success_response(message='Teacher profile permanently deleted')

        # Safe soft deactivation
        if instance.user:
            instance.user.is_active = False
            instance.user.save()
        return success_response(message='Teacher profile deactivated successfully. Faculty history preserved.')

    @action(detail=True, methods=['post'], url_path='deactivate', permission_classes=[IsAuthenticated, IsAdmin])
    def deactivate(self, request, pk=None):
        """POST /api/teachers/{id}/deactivate/"""
        teacher = self.get_object()
        if teacher.user:
            teacher.user.is_active = False
            teacher.user.save()
        return success_response(message=f"Teacher {teacher.employee_id} deactivated successfully.")

    @action(detail=True, methods=['post'], url_path='activate', permission_classes=[IsAuthenticated, IsAdmin])
    def activate(self, request, pk=None):
        """POST /api/teachers/{id}/activate/"""
        teacher = self.get_object()
        if teacher.user:
            teacher.user.is_active = True
            teacher.user.save()
        return success_response(message=f"Teacher {teacher.employee_id} activated successfully.")
