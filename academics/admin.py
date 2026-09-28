"""Admin configuration for academics."""
from django.contrib import admin
from .models import Department, Course, Subject, Marks


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'duration', 'status')
    list_filter = ('department', 'status')
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'course', 'semester', 'credits')
    list_filter = ('course', 'semester')
    search_fields = ('name', 'code')
    ordering = ('semester', 'name')


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'semester', 'total_marks', 'grade', 'academic_year')
    list_filter = ('semester', 'grade', 'academic_year')
    search_fields = ('student__student_id', 'student__first_name', 'student__last_name', 'subject__name', 'subject__code')
    ordering = ('-created_at',)

