"""Models for coursework assignments and student submissions."""
from django.db import models
from django.utils import timezone


class Assignment(models.Model):
    """Assignment or coursework posted by faculty."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments'
    )
    due_date = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=100)
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date', '-created_at']
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'

    def __str__(self):
        return f"{self.title} ({self.subject.code})"

    @property
    def is_past_due(self):
        return timezone.now() > self.due_date

    @property
    def total_submissions(self):
        return self.submissions.count()


class AssignmentSubmission(models.Model):
    """Student submission and evaluation for an assignment."""

    class SubmissionStatus(models.TextChoices):
        SUBMITTED = 'submitted', 'Submitted'
        LATE = 'late', 'Late Submission'
        GRADED = 'graded', 'Graded'

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='assignment_submissions'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    submission_text = models.TextField(blank=True, default='')
    attachment = models.FileField(upload_to='submissions/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.SUBMITTED
    )
    marks_obtained = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True, default='')
    graded_by = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Assignment Submission'
        verbose_name_plural = 'Assignment Submissions'
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student.student_id} - {self.assignment.title}"
