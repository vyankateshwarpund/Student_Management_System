"""Serializers for examinations and schedules."""
from django.db.models import Q
from rest_framework import serializers
from .models import Exam, ExamSchedule


class ExamScheduleSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    semester = serializers.IntegerField(source='subject.semester', read_only=True)
    course_name = serializers.CharField(source='subject.course.name', read_only=True)
    course_code = serializers.CharField(source='subject.course.code', read_only=True)
    exam_title = serializers.CharField(source='exam.title', read_only=True)

    class Meta:
        model = ExamSchedule
        fields = (
            'id', 'exam', 'exam_title', 'subject', 'subject_name',
            'subject_code', 'semester', 'course_name', 'course_code',
            'date', 'start_time', 'end_time', 'room_number', 'max_marks'
        )
        read_only_fields = ('id',)


class ExamSerializer(serializers.ModelSerializer):
    schedules_count = serializers.SerializerMethodField()
    schedules = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = (
            'id', 'title', 'exam_type', 'academic_year',
            'start_date', 'end_date', 'is_published', 'instructions',
            'schedules_count', 'schedules', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_schedules_count(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.role == 'student':
                student = getattr(request.user, 'student_profile', None)
                dept = student.department if student else None
                if not dept and student and student.course:
                    dept = student.course.department
                if dept:
                    return obj.schedules.filter(subject__course__department=dept).count()
            elif request.user.role == 'teacher':
                teacher = getattr(request.user, 'teacher_profile', None)
                if teacher and teacher.department:
                    return obj.schedules.filter(
                        Q(subject__course__department=teacher.department) |
                        Q(subject__in=teacher.subjects.all())
                    ).distinct().count()
        return obj.schedules.count()

    def get_schedules(self, obj):
        request = self.context.get('request')
        schedules = obj.schedules.select_related('subject', 'subject__course', 'subject__course__department').all()
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.role == 'student':
                student = getattr(request.user, 'student_profile', None)
                dept = student.department if student else None
                if not dept and student and student.course:
                    dept = student.course.department
                if dept:
                    schedules = schedules.filter(subject__course__department=dept)
            elif request.user.role == 'teacher':
                teacher = getattr(request.user, 'teacher_profile', None)
                if teacher and teacher.department:
                    schedules = schedules.filter(
                        Q(subject__course__department=teacher.department) |
                        Q(subject__in=teacher.subjects.all())
                    ).distinct()
        return ExamScheduleSerializer(schedules, many=True).data
