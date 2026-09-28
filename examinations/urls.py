"""URL configuration for examinations app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'schedules', views.ExamScheduleViewSet, basename='exam-schedule')
router.register(r'', views.ExamViewSet, basename='exam')

urlpatterns = [
    path('', include(router.urls)),
]
