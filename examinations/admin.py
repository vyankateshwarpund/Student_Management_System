"""Admin configuration for examinations app."""
from django.contrib import admin
from .models import Exam, ExamSchedule


class ExamScheduleInline(admin.TabularInline):
    model = ExamSchedule
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'exam_type', 'academic_year', 'start_date', 'end_date', 'is_published')
    list_filter = ('exam_type', 'academic_year', 'is_published')
    search_fields = ('title', 'academic_year')
    inlines = [ExamScheduleInline]


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ('exam', 'subject', 'date', 'start_time', 'end_time', 'room_number')
    list_filter = ('exam', 'date')
    search_fields = ('subject__name', 'subject__code', 'room_number')
