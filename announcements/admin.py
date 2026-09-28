"""Admin configuration for announcements app."""
from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'target_role', 'is_pinned', 'created_by', 'created_at')
    list_filter = ('category', 'target_role', 'is_pinned')
    search_fields = ('title', 'content')
    ordering = ('-is_pinned', '-created_at')
