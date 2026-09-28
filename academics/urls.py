"""URL configuration for academics app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'marks', views.MarksViewSet, basename='marks')

urlpatterns = [
    path('', include(router.urls)),
]
