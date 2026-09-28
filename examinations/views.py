"""Views for examinations, schedules, and hall tickets."""
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Exam, ExamSchedule
from .serializers import ExamSerializer, ExamScheduleSerializer
from accounts.permissions import IsAdmin, IsAdminOrReadOnly
from students.models import Student
from utils.response import success_response, created_response, error_response


class ExamViewSet(viewsets.ModelViewSet):
    """
    CRUD for Examinations.
    Admin has full control. Faculty & students have read-only access.
    """
    queryset = Exam.objects.all().prefetch_related('schedules', 'schedules__subject', 'schedules__subject__course', 'schedules__subject__course__department')
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['exam_type', 'academic_year', 'is_published']
    search_fields = ['title', 'academic_year']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-start_date']

    def get_queryset(self):
        user = self.request.user
        qs = Exam.objects.all().prefetch_related('schedules', 'schedules__subject', 'schedules__subject__course', 'schedules__subject__course__department')
        if not user.is_authenticated:
            return qs.filter(is_published=True)
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            dept = student.department if student else None
            if not dept and student and student.course:
                dept = student.course.department
            if dept:
                # Student only sees exams that have schedules for their department
                return qs.filter(is_published=True, schedules__subject__course__department=dept).distinct()
            return qs.filter(is_published=True)
        elif user.role == 'teacher':
            teacher = getattr(user, 'teacher_profile', None)
            if teacher and teacher.department:
                return qs.filter(
                    Q(schedules__subject__course__department=teacher.department) |
                    Q(schedules__subject__in=teacher.subjects.all())
                ).distinct()
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message='Examinations retrieved successfully')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message='Examination details retrieved successfully')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            exam = serializer.save()
            return created_response(data=self.get_serializer(exam).data, message='Examination created successfully')
        return error_response(message='Failed to create examination', errors=serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            exam = serializer.save()
            return success_response(data=self.get_serializer(exam).data, message='Examination updated successfully')
        return error_response(message='Failed to update examination', errors=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message='Examination deleted successfully')

    @action(detail=True, methods=['get'], url_path='hall-ticket')
    def hall_ticket(self, request, pk=None):
        """
        GET /api/exams/{id}/hall-ticket/?student_id=...
        Generates Hall Ticket / Admit Card data for the examination.
        """
        exam = self.get_object()
        user = request.user
        student = None

        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
        else:
            student_param = request.query_params.get('student_id')
            if student_param:
                if student_param.isdigit():
                    student = Student.objects.filter(id=student_param).first()
                else:
                    student = Student.objects.filter(student_id__iexact=student_param).first()
            else:
                student = Student.objects.first()

        if not student:
            return error_response(
                message='Student record not found for hall ticket generation',
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Get exam schedules matching student's course and semester
        schedules = ExamSchedule.objects.filter(
            exam=exam,
            subject__course=student.course,
            subject__semester=student.semester
        ).select_related('subject')

        if not schedules.exists():
            # If no course-specific schedule, list department schedules for that exam
            dept = student.department or (student.course.department if student.course else None)
            if dept:
                schedules = ExamSchedule.objects.filter(exam=exam, subject__course__department=dept).select_related('subject')
            else:
                schedules = ExamSchedule.objects.filter(exam=exam).select_related('subject')

        papers = [{
            'subject_code': s.subject.code,
            'subject_name': s.subject.name,
            'date': str(s.date),
            'start_time': s.start_time.strftime('%I:%M %p') if s.start_time else '',
            'end_time': s.end_time.strftime('%I:%M %p') if s.end_time else '',
            'room_number': s.room_number,
            'max_marks': s.max_marks
        } for s in schedules]

        data = {
            'exam_title': exam.title,
            'academic_year': exam.academic_year,
            'instructions': exam.instructions,
            'student_id': student.student_id,
            'student_name': student.full_name,
            'department': student.department.name,
            'course': student.course.name,
            'semester': student.semester,
            'papers': papers
        }

        return success_response(
            data=data,
            message=f"Hall ticket for {student.full_name} generated successfully"
        )


class ExamScheduleViewSet(viewsets.ModelViewSet):
    """CRUD for Exam Schedules."""
    queryset = ExamSchedule.objects.select_related('exam', 'subject', 'subject__course', 'subject__course__department')
    serializer_class = ExamScheduleSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['exam', 'subject', 'subject__course', 'subject__semester', 'date']
    search_fields = ['subject__name', 'subject__code', 'room_number', 'exam__title']
    ordering_fields = ['date', 'start_time']
    ordering = ['date', 'start_time']

    def get_queryset(self):
        user = self.request.user
        qs = ExamSchedule.objects.select_related('exam', 'subject', 'subject__course', 'subject__course__department')
        if not user.is_authenticated:
            return qs.none()
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            if student:
                # Role-based scoping: Students only see their own department's exam details
                dept = student.department or (student.course.department if student.course else None)
                if dept:
                    return qs.filter(subject__course__department=dept)
            return qs.none()
        elif user.role == 'teacher':
            teacher = getattr(user, 'teacher_profile', None)
            if teacher:
                # Teachers see exam details for their department or assigned subjects
                return qs.filter(
                    Q(subject__course__department=teacher.department) |
                    Q(subject__in=teacher.subjects.all())
                ).distinct()
            return qs.none()
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message='Exam schedules retrieved successfully')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message='Exam schedule details retrieved successfully')
