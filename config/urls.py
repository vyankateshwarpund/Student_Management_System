"""Root URL configuration for Student Management System."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from accounts.urls import auth_urlpatterns, user_urlpatterns

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Authentication endpoints
    path('api/auth/', include((auth_urlpatterns, 'auth'))),

    # User management (admin only)
    path('api/', include((user_urlpatterns, 'users'))),

    # Student management
    path('api/students/', include('students.urls')),

    # Academic structure (departments, courses, subjects, marks)
    path('api/', include('academics.urls')),

    # Attendance management
    path('api/attendance/', include('attendance.urls')),

    # Teacher management
    path('api/teachers/', include('teachers.urls')),

    # Dashboard & Analytics
    path('api/dashboard/', include('dashboard.urls')),

    # Campus Announcements & Bulletin Board
    path('api/announcements/', include('announcements.urls')),

    # Examinations & Hall Tickets
    path('api/exams/', include('examinations.urls')),

    # Coursework & Assignments
    path('api/assignments/', include('assignments.urls')),

    # Fees & Financial Accounts
    path('api/fees/', include('finance.urls')),

    # Student Services, Library, Timetable, Leaves, Tickets
    path('api/services/', include('student_services.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # DRF Browsable API auth (login/logout buttons)
    path('api-auth/', include('rest_framework.urls')),

    # Frontend web application
    path('', include('frontend.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
