"""Serializers for student services models."""
from rest_framework import serializers
from .models import (
    ClassSchedule, LiveClass, StudyMaterial, Lesson, BookIssued,
    LeaveRequest, SupportTicket, StationaryIssued, CampusEvent, Certificate
)


class ClassScheduleSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True, default='')

    class Meta:
        model = ClassSchedule
        fields = (
            'id', 'day_of_week', 'period_number', 'start_time', 'end_time',
            'subject', 'subject_code', 'subject_name', 'teacher', 'teacher_name', 'room'
        )


class LiveClassSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True, default='')

    class Meta:
        model = LiveClass
        fields = (
            'id', 'title', 'subject', 'subject_code', 'subject_name',
            'teacher', 'teacher_name', 'scheduled_at', 'duration_mins',
            'meeting_url', 'status'
        )


class StudyMaterialSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True, default='')

    class Meta:
        model = StudyMaterial
        fields = (
            'id', 'title', 'subject', 'subject_code', 'subject_name',
            'teacher', 'teacher_name', 'description', 'file_attachment',
            'external_url', 'uploaded_at'
        )


class LessonSerializer(serializers.ModelSerializer):
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'id', 'subject', 'subject_code', 'subject_name',
            'chapter_number', 'title', 'description',
            'learning_objectives', 'status'
        )


class BookIssuedSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id_code = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = BookIssued
        fields = (
            'id', 'student', 'student_name', 'student_id_code', 'book_title',
            'author', 'accession_no', 'issue_date', 'due_date', 'return_date',
            'fine_amount', 'status'
        )


class LeaveRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id_code = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = (
            'id', 'student', 'student_name', 'student_id_code', 'leave_type',
            'from_date', 'to_date', 'reason', 'status', 'admin_remarks', 'applied_at'
        )
        read_only_fields = ('id', 'applied_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'student':
            for f in ['status', 'admin_remarks', 'student']:
                if f in self.fields:
                    self.fields[f].read_only = True


class SupportTicketSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id_code = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = SupportTicket
        fields = (
            'id', 'student', 'student_name', 'student_id_code', 'ticket_no',
            'category', 'subject', 'description', 'status', 'response',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'ticket_no', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'student':
            for f in ['response', 'status', 'student']:
                if f in self.fields:
                    self.fields[f].read_only = True


class StationaryIssuedSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id_code = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = StationaryIssued
        fields = (
            'id', 'student', 'student_name', 'student_id_code', 'item_name',
            'quantity', 'issued_date', 'status', 'remarks'
        )


class CampusEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEvent
        fields = (
            'id', 'title', 'event_type', 'start_date', 'end_date',
            'location', 'description'
        )


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id_code = serializers.CharField(source='student.student_id', read_only=True)
    course_name = serializers.CharField(source='student.course.name', read_only=True)
    department_name = serializers.CharField(source='student.department.name', read_only=True)

    class Meta:
        model = Certificate
        fields = (
            'id', 'student', 'student_name', 'student_id_code', 'course_name',
            'department_name', 'certificate_type', 'certificate_no',
            'issue_date', 'purpose'
        )
