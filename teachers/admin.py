"""Admin configuration for teachers app."""
from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'department', 'phone', 'qualification')
    list_filter = ('department',)
    search_fields = (
        'employee_id', 'user__first_name', 'user__last_name',
        'user__username', 'user__email', 'phone',
    )
    filter_horizontal = ('subjects',)
    ordering = ('user__first_name',)
