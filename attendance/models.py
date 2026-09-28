"""Attendance model for tracking student presence."""
from django.db import models
from django.conf import settings


class Attendance(models.Model):
    """Track student attendance per subject per day."""

    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        LEAVE = 'leave', 'Leave'

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PRESENT,
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_recorded',
    )
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'student']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'
        unique_together = ['student', 'subject', 'date']

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.date} - {self.status}"
