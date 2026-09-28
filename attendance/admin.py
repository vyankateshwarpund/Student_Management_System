"""Admin configuration for attendance app."""
from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status', 'teacher')
    list_filter = ('status', 'date', 'subject')
    search_fields = (
        'student__student_id', 'student__first_name', 'student__last_name',
        'subject__name', 'subject__code',
    )
    ordering = ('-date', 'student')
