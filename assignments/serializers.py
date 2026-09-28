"""Serializers for assignments and student submissions."""
from rest_framework import serializers
from .models import Assignment, AssignmentSubmission


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_id_code = serializers.CharField(source='student.student_id', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    max_marks = serializers.IntegerField(source='assignment.max_marks', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.full_name', read_only=True, default='')

    class Meta:
        model = AssignmentSubmission
        fields = (
            'id', 'assignment', 'assignment_title', 'student', 'student_id_code',
            'student_name', 'submitted_at', 'submission_text', 'attachment',
            'status', 'marks_obtained', 'max_marks', 'feedback', 'graded_by',
            'graded_by_name', 'graded_at'
        )
        read_only_fields = ('id', 'submitted_at', 'graded_at', 'graded_by')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'student':
            for f in ['marks_obtained', 'feedback', 'status', 'student', 'assignment']:
                if f in self.fields:
                    self.fields[f].read_only = True


class AssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    semester = serializers.IntegerField(source='subject.semester', read_only=True)
    course_name = serializers.CharField(source='subject.course.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True, default='')
    total_submissions = serializers.IntegerField(read_only=True)
    is_past_due = serializers.BooleanField(read_only=True)
    my_submission = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = (
            'id', 'title', 'description', 'subject', 'subject_name',
            'subject_code', 'semester', 'course_name', 'teacher',
            'teacher_name', 'due_date', 'max_marks', 'attachment',
            'total_submissions', 'is_past_due', 'my_submission',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_my_submission(self, obj):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return None
        if request.user.role == 'student':
            student = getattr(request.user, 'student_profile', None)
            if student:
                submission = obj.submissions.filter(student=student).first()
                if submission:
                    return AssignmentSubmissionSerializer(submission).data
        return None
