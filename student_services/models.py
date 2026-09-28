"""Models for timetable, live classes, study materials, library, leaves, tickets, events, certificates."""
from django.db import models


class ClassSchedule(models.Model):
    """Weekly class timetable period."""
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]

    day_of_week = models.CharField(max_length=20, choices=DAYS_OF_WEEK)
    period_number = models.PositiveSmallIntegerField(default=1)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='timetables'
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_slots'
    )
    room = models.CharField(max_length=50, default='Room 204')

    class Meta:
        ordering = ['day_of_week', 'period_number']
        verbose_name = 'Class Schedule'
        verbose_name_plural = 'Class Schedules'

    def __str__(self):
        return f"{self.day_of_week} P{self.period_number} - {self.subject.code} ({self.room})"


class LiveClass(models.Model):
    """Online lecture / live virtual session."""
    class ClassStatus(models.TextChoices):
        UPCOMING = 'upcoming', 'Upcoming'
        LIVE = 'live', 'Live Now'
        COMPLETED = 'completed', 'Completed'

    title = models.CharField(max_length=200)
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='live_classes'
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='live_classes'
    )
    scheduled_at = models.DateTimeField()
    duration_mins = models.PositiveIntegerField(default=60)
    meeting_url = models.URLField(default='https://meet.google.com/xyz-edu-demo')
    status = models.CharField(
        max_length=20,
        choices=ClassStatus.choices,
        default=ClassStatus.UPCOMING
    )

    class Meta:
        ordering = ['-scheduled_at']
        verbose_name = 'Live Class'
        verbose_name_plural = 'Live Classes'

    def __str__(self):
        return f"{self.title} - {self.subject.code} ({self.status})"


class StudyMaterial(models.Model):
    """Subject notes, reference slides, and textbooks."""
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='study_materials'
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materials_uploaded'
    )
    description = models.TextField(blank=True, default='')
    file_attachment = models.FileField(upload_to='study_materials/', blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Study Material'
        verbose_name_plural = 'Study Materials'

    def __str__(self):
        return f"{self.title} ({self.subject.code})"


class Lesson(models.Model):
    """Chapter/Unit curriculum progress."""
    class LessonStatus(models.TextChoices):
        COMPLETED = 'completed', 'Completed'
        IN_PROGRESS = 'in_progress', 'In Progress'
        PLANNED = 'planned', 'Planned'

    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    chapter_number = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    learning_objectives = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=LessonStatus.choices,
        default=LessonStatus.PLANNED
    )

    class Meta:
        ordering = ['subject', 'chapter_number']
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'

    def __str__(self):
        return f"Ch {self.chapter_number}: {self.title} ({self.subject.code})"


class BookIssued(models.Model):
    """Library book checkout records."""
    class BookStatus(models.TextChoices):
        ISSUED = 'issued', 'Issued'
        RETURNED = 'returned', 'Returned'
        OVERDUE = 'overdue', 'Overdue'

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='books_issued'
    )
    book_title = models.CharField(max_length=250)
    author = models.CharField(max_length=200)
    accession_no = models.CharField(max_length=50)
    issue_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20,
        choices=BookStatus.choices,
        default=BookStatus.ISSUED
    )

    class Meta:
        ordering = ['-issue_date']
        verbose_name = 'Book Issued'
        verbose_name_plural = 'Books Issued'

    def __str__(self):
        return f"{self.book_title} -> {self.student.student_id}"


class LeaveRequest(models.Model):
    """Student leave application."""
    class LeaveType(models.TextChoices):
        MEDICAL = 'medical', 'Medical Leave'
        CASUAL = 'casual', 'Casual Leave'
        ACADEMIC = 'academic', 'Academic / On Duty'

    class LeaveStatus(models.TextChoices):
        PENDING = 'pending', 'Pending Approval'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices,
        default=LeaveType.CASUAL
    )
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=LeaveStatus.choices,
        default=LeaveStatus.PENDING
    )
    admin_remarks = models.TextField(blank=True, default='')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-applied_at']
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'

    def __str__(self):
        return f"{self.student.student_id} - {self.leave_type} ({self.status})"


class SupportTicket(models.Model):
    """Helpdesk support ticket."""
    class TicketCategory(models.TextChoices):
        FEE = 'fee', 'Fee & Finance'
        ACADEMICS = 'academics', 'Academics & Exams'
        HOSTEL = 'hostel', 'Hostel & Transport'
        IT = 'it', 'Portal / IT Support'
        OTHER = 'other', 'General Inquiry'

    class TicketStatus(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )
    ticket_no = models.CharField(max_length=50, unique=True, db_index=True)
    category = models.CharField(
        max_length=20,
        choices=TicketCategory.choices,
        default=TicketCategory.ACADEMICS
    )
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.OPEN
    )
    response = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'

    def __str__(self):
        return f"{self.ticket_no} - {self.subject}"


class StationaryIssued(models.Model):
    """Stationery, uniforms, and lab kit allocation."""
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='stationery_items'
    )
    item_name = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(default=1)
    issued_date = models.DateField()
    status = models.CharField(max_length=50, default='Issued')
    remarks = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        ordering = ['-issued_date']
        verbose_name = 'Stationery Issued'
        verbose_name_plural = 'Stationery Issued'

    def __str__(self):
        return f"{self.item_name} x{self.quantity} to {self.student.student_id}"


class CampusEvent(models.Model):
    """Institutional calendar event (holiday, symposium, festival)."""
    class EventType(models.TextChoices):
        HOLIDAY = 'holiday', 'Holiday'
        EVENT = 'event', 'Campus Event'
        EXAM = 'exam', 'Examination'

    title = models.CharField(max_length=200)
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.EVENT
    )
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=150, blank=True, default='Campus Main Auditorium')
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['start_date']
        verbose_name = 'Campus Event'
        verbose_name_plural = 'Campus Events'

    def __str__(self):
        return f"{self.title} ({self.start_date})"


class Certificate(models.Model):
    """Official student certificates."""
    class CertificateType(models.TextChoices):
        BONAFIDE = 'bonafide', 'Bonafide Student Certificate'
        STUDY = 'study', 'Study / Conduct Certificate'
        MERIT = 'merit', 'Academic Merit Certificate'
        TRANSFER = 'transfer', 'Transfer / Migration Certificate'

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    certificate_type = models.CharField(
        max_length=20,
        choices=CertificateType.choices,
        default=CertificateType.BONAFIDE
    )
    certificate_no = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    purpose = models.CharField(max_length=200, default='General Purpose / Passport / Visa')

    class Meta:
        ordering = ['-issue_date']
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'

    def __str__(self):
        return f"{self.certificate_no} - {self.student.student_id}"
