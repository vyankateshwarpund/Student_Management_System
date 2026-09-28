"""Views for campus announcements and bulletin board."""
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from .models import Announcement
from .serializers import AnnouncementSerializer
from accounts.permissions import IsAdminOrTeacher
from utils.response import success_response, created_response, error_response


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    CRUD for Campus Bulletins and Announcements.
    Admin & Teachers can post and manage circulars.
    Students can read announcements targeted to them or all campus members.
    """
    serializer_class = AnnouncementSerializer
    filterset_fields = ['category', 'target_role', 'is_pinned']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'is_pinned', 'category']
    ordering = ['-is_pinned', '-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Announcement.objects.select_related('created_by')
        if not user.is_authenticated:
            return qs.none()

        if user.role == 'admin':
            return qs
        elif user.role == 'teacher':
            return qs.filter(Q(target_role__in=['all', 'teachers', 'teacher']) | Q(created_by=user))
        else:
            return qs.filter(Q(target_role__in=['all', 'students', 'student']))

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message='Announcements retrieved successfully')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message='Announcement retrieved successfully')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            ann = serializer.save(created_by=request.user)
            return created_response(data=self.get_serializer(ann).data, message='Announcement published successfully')
        return error_response(message='Failed to post announcement', errors=serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if request.user.role == 'teacher' and instance.created_by != request.user:
            return error_response(
                message='Teachers can only modify announcements they authored.',
                status_code=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            ann = serializer.save()
            return success_response(data=self.get_serializer(ann).data, message='Announcement updated successfully')
        return error_response(message='Failed to update announcement', errors=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role == 'teacher' and instance.created_by != request.user:
            return error_response(
                message='Teachers can only remove announcements they authored.',
                status_code=status.HTTP_403_FORBIDDEN
            )
        instance.delete()
        return success_response(message='Announcement deleted successfully')
