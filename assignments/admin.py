"""Admin configuration for assignments."""
from django.contrib import admin
from .models import Assignment, AssignmentSubmission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'teacher', 'due_date', 'max_marks', 'total_submissions')
    list_filter = ('subject__course', 'subject__semester', 'due_date')
    search_fields = ('title', 'description', 'subject__name')


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'status', 'marks_obtained', 'submitted_at', 'graded_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('student__student_id', 'student__user__first_name', 'assignment__title')
