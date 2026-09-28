"""Admin registration for student services."""
from django.contrib import admin
from .models import (
    ClassSchedule, LiveClass, StudyMaterial, Lesson, BookIssued,
    LeaveRequest, SupportTicket, StationaryIssued, CampusEvent, Certificate
)

admin.site.register(ClassSchedule)
admin.site.register(LiveClass)
admin.site.register(StudyMaterial)
admin.site.register(Lesson)
admin.site.register(BookIssued)
admin.site.register(LeaveRequest)
admin.site.register(SupportTicket)
admin.site.register(StationaryIssued)
admin.site.register(CampusEvent)
admin.site.register(Certificate)
