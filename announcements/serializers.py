"""Serializers for campus announcements."""
from rest_framework import serializers
from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    author_role = serializers.CharField(source='created_by.role', read_only=True)

    class Meta:
        model = Announcement
        fields = (
            'id', 'title', 'content', 'category', 'target_role',
            'is_pinned', 'author_name', 'author_role',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'author_name', 'author_role', 'created_at', 'updated_at')
