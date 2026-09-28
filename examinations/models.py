"""Models for examinations, schedules, and hall tickets."""
from django.db import models


class Exam(models.Model):
    """Institutional examination term or series."""

    class ExamType(models.TextChoices):
        MID_TERM = 'mid_term', 'Mid-Semester Examination'
        FINAL = 'final', 'End-Semester Final Examination'
        PRACTICAL = 'practical', 'Practical / Viva Voce'
        UNIT_TEST = 'unit_test', 'Unit Test'

    title = models.CharField(max_length=200)
    exam_type = models.CharField(
        max_length=20,
        choices=ExamType.choices,
        default=ExamType.MID_TERM,
        db_index=True
    )
    academic_year = models.CharField(max_length=20, default='2025-2026')
    start_date = models.DateField()
    end_date = models.DateField()
    is_published = models.BooleanField(
        default=True,
        help_text='If published, students can view schedule and generate Hall Tickets'
    )
    instructions = models.TextField(
        blank=True,
        null=True,
        default='1. Candidates must arrive at the examination hall 15 minutes before scheduled commencement.\n2. Electronic gadgets, mobile phones, and programmable calculators are strictly prohibited.\n3. Hall ticket and institutional photo ID card are mandatory for entry.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Examination'
        verbose_name_plural = 'Examinations'

    def __str__(self):
        return f"{self.title} ({self.academic_year})"


class ExamSchedule(models.Model):
    """Specific paper timetable within an examination."""

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='exam_schedules'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50, default='Examination Hall 1')
    max_marks = models.IntegerField(default=100)

    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = 'Exam Schedule'
        verbose_name_plural = 'Exam Schedules'
        unique_together = ['exam', 'subject']

    def __str__(self):
        return f"{self.exam.title} - {self.subject.name} on {self.date}"
