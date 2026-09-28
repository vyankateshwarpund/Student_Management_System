"""URL patterns for student services app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClassScheduleViewSet, LiveClassViewSet, StudyMaterialViewSet,
    LessonViewSet, BookIssuedViewSet, LeaveRequestViewSet,
    SupportTicketViewSet, StationaryIssuedViewSet, CampusEventViewSet,
    CertificateViewSet
)

router = DefaultRouter()
router.register(r'schedules', ClassScheduleViewSet, basename='class-schedule')
router.register(r'live-classes', LiveClassViewSet, basename='live-class')
router.register(r'materials', StudyMaterialViewSet, basename='study-material')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'books', BookIssuedViewSet, basename='book-issued')
router.register(r'library', BookIssuedViewSet, basename='library')
router.register(r'leaves', LeaveRequestViewSet, basename='leave-request')
router.register(r'tickets', SupportTicketViewSet, basename='support-ticket')
router.register(r'stationery', StationaryIssuedViewSet, basename='stationary-issued')
router.register(r'events', CampusEventViewSet, basename='campus-event')
router.register(r'certificates', CertificateViewSet, basename='certificate')

urlpatterns = [
    path('', include(router.urls)),
]
