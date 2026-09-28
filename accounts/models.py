"""Custom User model with role-based access control."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with role field for RBAC."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        TEACHER = 'teacher', 'Teacher'
        STUDENT = 'student', 'Student'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True,
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT
