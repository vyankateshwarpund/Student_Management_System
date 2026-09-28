"""URL configuration for dashboard app."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.UnifiedDashboardView.as_view(), name='dashboard-unified'),
    path('admin/', views.AdminDashboardView.as_view(), name='dashboard-admin'),
    path('teacher/', views.TeacherDashboardView.as_view(), name='dashboard-teacher'),
    path('student/', views.StudentDashboardView.as_view(), name='dashboard-student'),
]
