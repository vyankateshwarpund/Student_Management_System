"""Teacher model linking user accounts to academic roles."""
from django.db import models
from django.conf import settings


class Teacher(models.Model):
    """Teacher profile linked to a user account."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
    )
    department = models.ForeignKey(
        'academics.Department',
        on_delete=models.PROTECT,
        related_name='teachers',
    )
    subjects = models.ManyToManyField(
        'academics.Subject',
        related_name='teachers',
        blank=True,
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    qualification = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name']
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name() or self.user.username}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
