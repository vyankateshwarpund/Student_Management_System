"""Serializers for attendance management."""
from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance CRUD."""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_code = serializers.CharField(source='student.student_id', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)

    class Meta:
        model = Attendance
        fields = (
            'id', 'student', 'student_name', 'student_code',
            'subject', 'subject_name', 'subject_code',
            'date', 'status', 'teacher', 'teacher_name',
            'remarks', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'teacher', 'created_at', 'updated_at')

    def validate(self, attrs):
        student = attrs.get('student', getattr(self.instance, 'student', None))
        subject = attrs.get('subject', getattr(self.instance, 'subject', None))
        date = attrs.get('date', getattr(self.instance, 'date', None))

        qs = Attendance.objects.filter(student=student, subject=subject, date=date)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Attendance has already been marked for this student and subject on this date.')

        return attrs
