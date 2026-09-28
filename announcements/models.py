"""Models for institutional bulletin board and notices."""
from django.db import models
from django.conf import settings


class Announcement(models.Model):
    """Institutional circulars, exam notices, and campus bulletins."""

    class Category(models.TextChoices):
        URGENT = 'urgent', 'Urgent Notice'
        EXAM = 'exam', 'Examination & Results'
        ACADEMIC = 'academic', 'Academic Circular'
        HOLIDAY = 'holiday', 'Holiday Notification'
        EVENT = 'event', 'Campus Event'
        GENERAL = 'general', 'General Bulletin'

    class TargetRole(models.TextChoices):
        ALL = 'all', 'All Campus Members'
        STUDENTS = 'students', 'Students Only'
        TEACHERS = 'teachers', 'Faculty Only'

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL,
        db_index=True,
    )
    target_role = models.CharField(
        max_length=20,
        choices=TargetRole.choices,
        default=TargetRole.ALL,
        db_index=True,
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text='Pinned notices appear at top of notice board'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='announcements_posted'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'

    def __str__(self):
        return f"[{self.category.upper()}] {self.title}"
