"""URL configuration for students app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.StudentViewSet, basename='student')

urlpatterns = router.urls
