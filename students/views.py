"""Views for Student CRUD with RBAC, search, filtering, and pagination."""
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from academics.services.transcript import calculate_student_transcript

from .models import Student
from .serializers import (
    StudentListSerializer,
    StudentDetailSerializer,
    StudentCreateUpdateSerializer,
)
from .filters import StudentFilter
from accounts.permissions import IsAdmin, IsAdminOrTeacher
from utils.response import success_response, created_response, error_response


class StudentViewSet(viewsets.ModelViewSet):
    """
    Student CRUD with role-based access control.

    GET    /api/students/          — List students (admin: all, teacher: assigned classes, student: own)
    POST   /api/students/          — Create student (admin only)
    GET    /api/students/{id}/     — Student details
    PUT    /api/students/{id}/     — Full update (admin only)
    PATCH  /api/students/{id}/     — Partial update (admin only)
    DELETE /api/students/{id}/     — Delete student (admin only)

    Search: ?search=Rahul  (searches student_id, first_name, last_name, email, phone)
    Filter: ?department=1&semester=7&status=active
    Sort:   ?ordering=-created_at
    Page:   ?page=2&page_size=20
    """
    filterset_class = StudentFilter
    search_fields = ['student_id', 'first_name', 'last_name', 'email', 'phone']
    ordering_fields = [
        'student_id', 'first_name', 'last_name',
        'created_at', 'semester', 'admission_date',
    ]
    ordering = ['-created_at']

    def get_queryset(self):
        """Scope queryset based on user role."""
        user = self.request.user
        qs = Student.objects.select_related('department', 'course')

        if user.role == 'student':
            # Students can only see their own record
            return qs.filter(user=user)
        elif user.role == 'teacher':
            # Teachers can only view students from their assigned classes, subjects, or department
            teacher = getattr(user, 'teacher_profile', None)
            if teacher:
                taught_subjects = teacher.subjects.all()
                courses_taught = taught_subjects.values_list('course_id', flat=True)
                semesters_taught = taught_subjects.values_list('semester', flat=True)
                return qs.filter(
                    Q(department=teacher.department) |
                    (Q(course_id__in=courses_taught) & Q(semester__in=semesters_taught))
                ).distinct()
            return qs.none()
        # Admin can see all students
        return qs

    def get_serializer_class(self):
        """Use different serializers for list vs detail vs create/update."""
        if self.action == 'list':
            return StudentListSerializer
        if self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentCreateUpdateSerializer

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ('create', 'destroy'):
            return [IsAuthenticated(), IsAdmin()]
        if self.action in ('update', 'partial_update'):
            return [IsAuthenticated(), IsAdmin()]
        # list and retrieve: any authenticated user (queryset handles scoping)
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data=serializer.data,
            message='Students retrieved successfully',
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = StudentDetailSerializer(instance)
        return success_response(
            data=serializer.data,
            message='Student retrieved successfully',
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            return created_response(
                data=StudentDetailSerializer(student).data,
                message='Student created successfully',
            )
        return error_response(
            message='Student creation failed',
            errors=serializer.errors,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial,
        )
        if serializer.is_valid():
            student = serializer.save()
            return success_response(
                data=StudentDetailSerializer(student).data,
                message='Student updated successfully',
            )
        return error_response(
            message='Student update failed',
            errors=serializer.errors,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Security Guardrail 2: Admin cannot permanently delete critical records without superuser authorization
        if request.query_params.get('hard_delete') == 'true':
            if not request.user.is_superuser:
                return error_response(
                    message="Permanent deletion of critical student records requires Super Administrator authorization. Please deactivate the student instead.",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            instance.delete()
            return success_response(message='Student record permanently deleted')

        # Default safe deactivation
        instance.status = Student.Status.INACTIVE
        instance.save()
        if instance.user:
            instance.user.is_active = False
            instance.user.save()
        return success_response(message='Student record deactivated successfully. Academic history preserved.')

    @action(detail=True, methods=['post'], url_path='deactivate', permission_classes=[IsAuthenticated, IsAdmin])
    def deactivate(self, request, pk=None):
        """POST /api/students/{id}/deactivate/"""
        student = self.get_object()
        student.status = Student.Status.INACTIVE
        student.save()
        if student.user:
            student.user.is_active = False
            student.user.save()
        return success_response(message=f"Student {student.student_id} deactivated successfully.")

    @action(detail=True, methods=['post'], url_path='activate', permission_classes=[IsAuthenticated, IsAdmin])
    def activate(self, request, pk=None):
        """POST /api/students/{id}/activate/"""
        student = self.get_object()
        student.status = Student.Status.ACTIVE
        student.save()
        if student.user:
            student.user.is_active = True
            student.user.save()
        return success_response(message=f"Student {student.student_id} activated successfully.")

    @action(detail=True, methods=['get'])
    def transcript(self, request, pk=None):
        """GET /api/students/{id}/transcript/"""
        student = self.get_object()
        data = calculate_student_transcript(student)
        return success_response(data=data, message=f"Official academic transcript for {student.full_name} generated successfully")

