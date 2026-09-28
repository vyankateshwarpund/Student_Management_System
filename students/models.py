"""Student model with all fields from the PRD."""
from django.db import models
from django.conf import settings
from academics.models import Department, Course


class Student(models.Model):
    """Student record with personal, academic, and contact information."""

    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        GRADUATED = 'graduated', 'Graduated'
        SUSPENDED = 'suspended', 'Suspended'

    # Link to auth user (optional — set when student registers an account)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_profile',
    )

    # Unique student identifier
    student_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text='Unique student ID (e.g., STU001)',
    )

    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        null=True,
    )

    # Address
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    # Academic information
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='students',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='students',
    )
    year = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField()

    # Enrollment
    admission_date = models.DateField(blank=True, null=True)
    profile_photo = models.ImageField(
        upload_to='student_photos/',
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['department', 'semester']),
        ]

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
