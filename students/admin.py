"""Admin configuration for students."""
from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'student_id', 'first_name', 'last_name', 'email',
        'department', 'course', 'semester', 'status',
    )
    list_filter = ('department', 'course', 'semester', 'status', 'gender')
    search_fields = ('student_id', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('-created_at',)
    list_per_page = 20

    fieldsets = (
        ('Student ID', {
            'fields': ('student_id', 'user'),
        }),
        ('Personal Information', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone',
                'date_of_birth', 'gender', 'profile_photo',
            ),
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'pincode'),
        }),
        ('Academic Information', {
            'fields': ('department', 'course', 'year', 'semester'),
        }),
        ('Enrollment', {
            'fields': ('admission_date', 'status'),
        }),
    )
