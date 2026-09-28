"""Views for student services, timetable, library, leaves, tickets, events, certificates."""
import uuid
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import (
    ClassSchedule, LiveClass, StudyMaterial, Lesson, BookIssued,
    LeaveRequest, SupportTicket, StationaryIssued, CampusEvent, Certificate
)
from .serializers import (
    ClassScheduleSerializer, LiveClassSerializer, StudyMaterialSerializer,
    LessonSerializer, BookIssuedSerializer, LeaveRequestSerializer,
    SupportTicketSerializer, StationaryIssuedSerializer, CampusEventSerializer,
    CertificateSerializer
)
from accounts.permissions import IsAdminOrReadOnly, IsAdminOrTeacher, IsAdminOrTeacherOrReadOnly
from students.models import Student
from utils.response import success_response, created_response, error_response


class ClassScheduleViewSet(viewsets.ModelViewSet):
    queryset = ClassSchedule.objects.select_related('subject', 'teacher', 'teacher__user').all()
    serializer_class = ClassScheduleSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['day_of_week', 'subject', 'subject__course', 'subject__semester']
    search_fields = ['subject__name', 'subject__code', 'room']


class LiveClassViewSet(viewsets.ModelViewSet):
    queryset = LiveClass.objects.select_related('subject', 'teacher', 'teacher__user').all()
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['status', 'subject', 'teacher']
    search_fields = ['title', 'subject__name', 'subject__code']


class StudyMaterialViewSet(viewsets.ModelViewSet):
    queryset = StudyMaterial.objects.select_related('subject', 'teacher', 'teacher__user').all()
    serializer_class = StudyMaterialSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacherOrReadOnly]
    filterset_fields = ['subject', 'subject__course', 'subject__semester']
    search_fields = ['title', 'description', 'subject__name']


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('subject').all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['subject', 'status']
    search_fields = ['title', 'description', 'subject__name']


class BookIssuedViewSet(viewsets.ModelViewSet):
    queryset = BookIssued.objects.select_related('student', 'student__user').all()
    serializer_class = BookIssuedSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student', 'status']
    search_fields = ['book_title', 'author', 'accession_no', 'student__student_id']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            return qs.filter(student=student) if student else qs.none()
        return qs

    @action(detail=True, methods=['post'], url_path='renew')
    def renew_book(self, request, pk=None):
        book = self.get_object()
        from datetime import timedelta
        book.due_date = book.due_date + timedelta(days=14)
        book.save()
        return success_response(data=self.get_serializer(book).data, message='Book renewed for 14 additional days')


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('student', 'student__user').all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student', 'status', 'leave_type']
    search_fields = ['reason', 'student__student_id']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            return qs.filter(student=student) if student else qs.none()
        elif user.role == 'teacher':
            teacher = getattr(user, 'teacher_profile', None)
            if teacher:
                taught_subjects = teacher.subjects.all()
                courses_taught = taught_subjects.values_list('course_id', flat=True)
                semesters_taught = taught_subjects.values_list('semester', flat=True)
                return qs.filter(
                    Q(student__department=teacher.department) |
                    (Q(student__course_id__in=courses_taught) & Q(student__semester__in=semesters_taught))
                ).distinct()
            return qs.none()
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            serializer.save(student=student, status=LeaveRequest.LeaveStatus.PENDING, admin_remarks='')
        else:
            serializer.save()

    def update(self, request, *args, **kwargs):
        if request.user.role == 'student':
            if any(k in request.data for k in ('status', 'admin_remarks', 'student')):
                return error_response(
                    message='Students cannot modify leave approval status or administrative remarks.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role == 'student' and instance.status != LeaveRequest.LeaveStatus.PENDING:
            return error_response(
                message='Cannot withdraw a leave request that has already been processed.',
                status_code=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class SupportTicketViewSet(viewsets.ModelViewSet):
    queryset = SupportTicket.objects.select_related('student', 'student__user').all()
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student', 'category', 'status']
    search_fields = ['ticket_no', 'subject', 'description']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            return qs.filter(student=student) if student else qs.none()
        return qs

    def perform_create(self, serializer):
        ticket_no = f"TCK-{uuid.uuid4().hex[:6].upper()}"
        user = self.request.user
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            serializer.save(student=student, ticket_no=ticket_no, status=SupportTicket.TicketStatus.OPEN, response='')
        else:
            serializer.save(ticket_no=ticket_no)

    def update(self, request, *args, **kwargs):
        if request.user.role == 'student':
            if any(k in request.data for k in ('response', 'status', 'ticket_no', 'student')):
                return error_response(
                    message='Students cannot alter staff responses or ticket resolution status.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role == 'student':
            return error_response(
                message='Students cannot delete official helpdesk logs.',
                status_code=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class StationaryIssuedViewSet(viewsets.ModelViewSet):
    queryset = StationaryIssued.objects.select_related('student', 'student__user').all()
    serializer_class = StationaryIssuedSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student', 'status']
    search_fields = ['item_name', 'student__student_id']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            return qs.filter(student=student) if student else qs.none()
        return qs


class CampusEventViewSet(viewsets.ModelViewSet):
    queryset = CampusEvent.objects.all()
    serializer_class = CampusEventSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['event_type']
    search_fields = ['title', 'description', 'location']


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.select_related('student', 'student__course', 'student__department').all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student', 'certificate_type']
    search_fields = ['certificate_no', 'student__student_id']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            return qs.filter(student=student) if student else qs.none()
        return qs
