"""Views for academic structure: Department, Course, Subject, Marks."""
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Department, Course, Subject, Marks
from .serializers import (
    DepartmentSerializer,
    CourseSerializer,
    SubjectSerializer,
    MarksSerializer,
)
from accounts.permissions import IsAdmin, IsAdminOrTeacher, IsAdminOrReadOnly
from students.models import Student
from utils.response import success_response, created_response, error_response


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    CRUD for Departments.
    Admin has full access; others have read-only access.
    """
    queryset = Department.objects.all().prefetch_related('courses', 'students')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message='Departments retrieved successfully')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message='Department retrieved successfully')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            dept = serializer.save()
            return created_response(data=self.get_serializer(dept).data, message='Department created successfully')
        return error_response(message='Department creation failed', errors=serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            dept = serializer.save()
            return success_response(data=self.get_serializer(dept).data, message='Department updated successfully')
        return error_response(message='Department update failed', errors=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message='Department deleted successfully')


class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD for Courses.
    Admin has full access; others have read-only access.
    """
    queryset = Course.objects.select_related('department').prefetch_related('subjects', 'students')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['department', 'status']
    search_fields = ['name', 'code', 'department__name']
    ordering_fields = ['name', 'code', 'duration', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        user = self.request.user
        qs = Course.objects.select_related('department').prefetch_related('subjects', 'students')
        if not user.is_authenticated:
            return qs.none()
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            if student and student.department:
                return qs.filter(department=student.department)
        elif user.role == 'teacher':
            teacher = getattr(user, 'teacher_profile', None)
            if teacher and teacher.department:
                return qs.filter(department=teacher.department)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message='Courses retrieved successfully')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message='Course retrieved successfully')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            course = serializer.save()
            return created_response(data=self.get_serializer(course).data, message='Course created successfully')
        return error_response(message='Course creation failed', errors=serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            course = serializer.save()
            return success_response(data=self.get_serializer(course).data, message='Course updated successfully')
        return error_response(message='Course update failed', errors=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message='Course deleted successfully')


class SubjectViewSet(viewsets.ModelViewSet):
    """
    CRUD for Subjects.
    Admin has full access; others have read-only access.
    """
    queryset = Subject.objects.select_related('course', 'course__department')
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['course', 'semester']
    search_fields = ['name', 'code', 'course__name']
    ordering_fields = ['semester', 'name', 'code', 'credits']
    ordering = ['semester', 'name']

    def get_queryset(self):
        user = self.request.user
        qs = Subject.objects.select_related('course', 'course__department')
        if not user.is_authenticated:
            return qs.none()
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            if student and student.department:
                return qs.filter(course__department=student.department)
        elif user.role == 'teacher':
            teacher = getattr(user, 'teacher_profile', None)
            if teacher and teacher.department:
                return qs.filter(
                    Q(course__department=teacher.department) |
                    Q(id__in=teacher.subjects.values_list('id', flat=True))
                ).distinct()
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message='Subjects retrieved successfully')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message='Subject retrieved successfully')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            subj = serializer.save()
            return created_response(data=self.get_serializer(subj).data, message='Subject created successfully')
        return error_response(message='Subject creation failed', errors=serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            subj = serializer.save()
            return success_response(data=self.get_serializer(subj).data, message='Subject updated successfully')
        return error_response(message='Subject update failed', errors=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message='Subject deleted successfully')


class MarksViewSet(viewsets.ModelViewSet):
    """
    CRUD for Marks.
    Admin & Teachers can manage marks.
    Students can only view their own marks.
    """
    serializer_class = MarksSerializer
    filterset_fields = ['student', 'subject', 'semester', 'academic_year', 'grade']
    search_fields = ['student__first_name', 'student__last_name', 'student__student_id', 'subject__name', 'subject__code']
    ordering_fields = ['total_marks', 'semester', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Marks.objects.select_related('student', 'subject', 'created_by')
        if user.role == 'student':
            return qs.filter(student__user=user)
        elif user.role == 'teacher':
            teacher = getattr(user, 'teacher_profile', None)
            if teacher:
                return qs.filter(
                    Q(created_by=user) |
                    Q(subject__in=teacher.subjects.all()) |
                    Q(subject__course__department=teacher.department)
                ).distinct()
            return qs.none()
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message='Marks retrieved successfully')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message='Marks retrieved successfully')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if request.user.role == 'teacher':
                teacher = getattr(request.user, 'teacher_profile', None)
                subject = serializer.validated_data.get('subject')
                if teacher and subject and not (subject in teacher.subjects.all() or subject.course.department == teacher.department):
                    return error_response(
                        message='You are only authorized to enter marks for your assigned subjects.',
                        status_code=status.HTTP_403_FORBIDDEN
                    )
            marks = serializer.save(created_by=request.user)
            return created_response(data=self.get_serializer(marks).data, message='Marks recorded successfully')
        return error_response(message='Failed to record marks', errors=serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if request.user.role == 'teacher':
            teacher = getattr(request.user, 'teacher_profile', None)
            if teacher and not (instance.subject in teacher.subjects.all() or instance.subject.course.department == teacher.department or instance.created_by == request.user):
                return error_response(
                    message='You are only authorized to update marks for your assigned subjects.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            marks = serializer.save()
            return success_response(data=self.get_serializer(marks).data, message='Marks updated successfully')
        return error_response(message='Failed to update marks', errors=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        if request.user.role == 'teacher':
            return error_response(
                message='Teachers cannot delete permanent academic examination records. Please contact Admin if a correction is needed.',
                status_code=status.HTTP_403_FORBIDDEN
            )
        instance = self.get_object()
        instance.delete()
        return success_response(message='Marks record deleted successfully')

    @action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)')
    def student_marks(self, request, student_id=None):
        """GET /api/marks/student/{student_id}/"""
        # Lookup student by ID or student_id string
        student = None
        if student_id.isdigit():
            student = Student.objects.filter(id=student_id).first()
        if not student:
            student = Student.objects.filter(student_id__iexact=student_id).first()

        if not student:
            return error_response(message='Student not found', status_code=status.HTTP_404_NOT_FOUND)

        # Check permissions: student can only view their own
        if request.user.role == 'student' and student.user != request.user:
            return error_response(message='You do not have permission to view marks for this student.', status_code=status.HTTP_403_FORBIDDEN)

        marks_records = Marks.objects.filter(student=student).select_related('subject')
        serializer = self.get_serializer(marks_records, many=True)
        return success_response(
            data={
                'student_id': student.student_id,
                'student_name': student.full_name,
                'department': student.department.name,
                'course': student.course.name,
                'semester': student.semester,
                'marks': serializer.data,
            },
            message=f"Marks for {student.full_name} retrieved successfully"
        )
