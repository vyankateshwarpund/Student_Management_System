from django.db import transaction
from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Attendance
from .serializers import AttendanceSerializer
from accounts.permissions import IsAdminOrTeacher
from students.models import Student
from academics.models import Subject
from utils.response import success_response, created_response, error_response


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    CRUD for Attendance.
    Admin & Teachers can mark and edit attendance.
    Students can only view their own attendance records and percentage.
    """
    serializer_class = AttendanceSerializer
    filterset_fields = ['student', 'subject', 'status', 'date']
    search_fields = [
        'student__first_name', 'student__last_name', 'student__student_id',
        'subject__name', 'subject__code',
    ]
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        user = self.request.user
        qs = Attendance.objects.select_related('student', 'subject', 'teacher')
        if user.role == 'student':
            return qs.filter(student__user=user)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message='Attendance records retrieved successfully')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message='Attendance record retrieved successfully')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            att = serializer.save(teacher=request.user)
            return created_response(data=self.get_serializer(att).data, message='Attendance marked successfully')
        return error_response(message='Failed to mark attendance', errors=serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            att = serializer.save()
            return success_response(data=self.get_serializer(att).data, message='Attendance updated successfully')
        return error_response(message='Failed to update attendance', errors=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message='Attendance record deleted successfully')

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        GET /api/attendance/summary/?student_id=STU001
        Returns total classes, present, absent, leave, and percentage per subject and overall.
        """
        student_param = request.query_params.get('student_id')
        user = request.user

        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            if not student:
                return error_response(message='Student profile not found for this user', status_code=status.HTTP_404_NOT_FOUND)
        else:
            if not student_param:
                return error_response(message='student_id query parameter is required for non-student users')
            if student_param.isdigit():
                student = Student.objects.filter(id=student_param).first()
            else:
                student = Student.objects.filter(student_id__iexact=student_param).first()

            if not student:
                return error_response(message='Student not found', status_code=status.HTTP_404_NOT_FOUND)

        # Calculate statistics
        records = Attendance.objects.filter(student=student)
        total_classes = records.count()
        total_present = records.filter(status='present').count()
        total_absent = records.filter(status='absent').count()
        total_leave = records.filter(status='leave').count()

        overall_percentage = round((total_present / total_classes * 100), 2) if total_classes > 0 else 0.0

        # Per-subject breakdown
        subject_stats = []
        subjects = Subject.objects.filter(attendance_records__student=student).distinct()
        for subj in subjects:
            subj_records = records.filter(subject=subj)
            s_total = subj_records.count()
            s_present = subj_records.filter(status='present').count()
            s_absent = subj_records.filter(status='absent').count()
            s_leave = subj_records.filter(status='leave').count()
            s_pct = round((s_present / s_total * 100), 2) if s_total > 0 else 0.0

            subject_stats.append({
                'subject_id': subj.id,
                'subject_name': subj.name,
                'subject_code': subj.code,
                'total_classes': s_total,
                'present': s_present,
                'absent': s_absent,
                'leave': s_leave,
                'percentage': s_pct,
            })

        return success_response(
            data={
                'student_id': student.student_id,
                'student_name': student.full_name,
                'total_classes': total_classes,
                'present': total_present,
                'absent': total_absent,
                'leave': total_leave,
                'overall_percentage': overall_percentage,
                'subject_breakdown': subject_stats,
            },
            message='Attendance summary calculated successfully'
        )

    @action(detail=False, methods=['post'], url_path='bulk-mark')
    def bulk_mark(self, request):
        """
        POST /api/attendance/bulk-mark/
        Payload:
        {
            "subject": 1,
            "date": "2026-09-24",
            "records": [
                {"student": 1, "status": "present", "remarks": ""},
                {"student": 2, "status": "absent", "remarks": "Late"}
            ]
        }
        """
        if request.user.role not in ['admin', 'teacher']:
            return error_response(message='Permission denied. Only faculty and admins can mark attendance.', status_code=status.HTTP_403_FORBIDDEN)

        subject_id = request.data.get('subject')
        att_date = request.data.get('date')
        records = request.data.get('records', [])

        if not subject_id or not att_date:
            return error_response(message='Subject and date are required fields.')

        if not records:
            return error_response(message='No student records provided for batch attendance.')

        subject = Subject.objects.filter(id=subject_id).first()
        if not subject:
            return error_response(message='Subject not found', status_code=status.HTTP_404_NOT_FOUND)

        saved_count = 0
        with transaction.atomic():
            for rec in records:
                student_id = rec.get('student')
                status_val = rec.get('status', 'present')
                remarks = rec.get('remarks', '')

                student = Student.objects.filter(id=student_id).first()
                if not student:
                    continue

                Attendance.objects.update_or_create(
                    student=student,
                    subject=subject,
                    date=att_date,
                    defaults={
                        'status': status_val,
                        'teacher': request.user,
                        'remarks': remarks
                    }
                )
                saved_count += 1

        return success_response(
            data={'saved_count': saved_count, 'date': att_date, 'subject': subject.name},
            message=f"Successfully recorded attendance for {saved_count} students in {subject.name}"
        )

