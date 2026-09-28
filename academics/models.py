"""Models for academic structure: Departments, Courses, Subjects, Marks."""
from django.db import models
from django.conf import settings


class Department(models.Model):
    """Academic department (e.g., Computer Science, Mechanical Engineering)."""
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    """Academic course offered by a department."""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses',
    )
    duration = models.IntegerField(
        help_text='Duration in years',
        default=4,
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return f"{self.name} ({self.code})"


class Subject(models.Model):
    """Subject within a course for a specific semester."""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subjects',
    )
    semester = models.IntegerField()
    credits = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['semester', 'name']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'

    def __str__(self):
        return f"{self.name} ({self.code}) - Sem {self.semester}"


class Marks(models.Model):
    """Student marks for a subject with auto-calculated total and grade."""

    GRADE_THRESHOLDS = [
        (90, 'O'),
        (80, 'A+'),
        (70, 'A'),
        (60, 'B+'),
        (50, 'B'),
        (40, 'C'),
        (0, 'F'),
    ]

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='marks',
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='marks',
    )
    semester = models.IntegerField()
    academic_year = models.CharField(
        max_length=20,
        help_text='e.g., 2025-2026',
        blank=True,
        null=True,
    )
    internal_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
    )
    external_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
    )
    practical_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
    )
    total_marks = models.DecimalField(
        max_digits=6, decimal_places=2, default=0,
    )
    grade = models.CharField(max_length=5, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marks_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Marks'
        verbose_name_plural = 'Marks'
        unique_together = ['student', 'subject', 'semester', 'academic_year']

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.total_marks} ({self.grade})"

    def calculate_total(self):
        """Calculate total marks from components."""
        self.total_marks = (
            self.internal_marks + self.external_marks + self.practical_marks
        )
        return self.total_marks

    def calculate_grade(self):
        """Calculate grade based on total marks (percentage assumed out of max)."""
        total = float(self.total_marks)
        for threshold, grade in self.GRADE_THRESHOLDS:
            if total >= threshold:
                self.grade = grade
                return grade
        self.grade = 'F'
        return 'F'

    def save(self, *args, **kwargs):
        """Auto-calculate total and grade before saving."""
        self.calculate_total()
        self.calculate_grade()
        super().save(*args, **kwargs)

