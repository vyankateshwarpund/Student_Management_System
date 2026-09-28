"""Models for student fees, invoices, structures, and payment records."""
from django.db import models


class FeeStructure(models.Model):
    """Institutional fee slab definition by course and period."""
    course = models.ForeignKey(
        'academics.Course',
        on_delete=models.CASCADE,
        related_name='fee_structures',
        null=True,
        blank=True
    )
    academic_session = models.CharField(max_length=50, default='2026-2027')
    fee_type = models.CharField(max_length=100)
    period = models.CharField(max_length=50, default='Monthly')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['fee_type']
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'

    def __str__(self):
        return f"{self.fee_type} ({self.period}) - ₹{self.amount}"


class FeeInvoice(models.Model):
    """Student fee billing invoice."""
    class InvoiceStatus(models.TextChoices):
        PAID = 'paid', 'Paid'
        UNPAID = 'unpaid', 'Unpaid'
        PARTIAL = 'partial', 'Partially Paid'

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    invoice_no = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=150)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.UNPAID
    )
    academic_session = models.CharField(max_length=50, default='2026-2027')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date']
        verbose_name = 'Fee Invoice'
        verbose_name_plural = 'Fee Invoices'

    def __str__(self):
        return f"{self.invoice_no} - {self.student.student_id} (₹{self.total_amount})"

    @property
    def balance_amount(self):
        return max(self.total_amount - self.paid_amount, 0)


class FeePayment(models.Model):
    """Payment transaction log and receipt."""
    invoice = models.ForeignKey(
        FeeInvoice,
        on_delete=models.SET_NULL,
        related_name='payments',
        null=True,
        blank=True
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='Online / Card')
    payment_date = models.DateTimeField(auto_now_add=True)
    receipt_no = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Fee Payment'
        verbose_name_plural = 'Fee Payments'

    def __str__(self):
        return f"{self.receipt_no} - ₹{self.amount} by {self.student.student_id}"
