"""Admin registration for finance models."""
from django.contrib import admin
from .models import FeeStructure, FeeInvoice, FeePayment


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('fee_type', 'course', 'period', 'amount', 'academic_session')
    list_filter = ('course', 'period', 'academic_session')


@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'student', 'title', 'due_date', 'total_amount', 'paid_amount', 'status')
    list_filter = ('status', 'academic_session', 'due_date')
    search_fields = ('invoice_no', 'title', 'student__student_id', 'student__user__first_name')


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_no', 'student', 'amount', 'payment_method', 'payment_date', 'transaction_id')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('receipt_no', 'transaction_id', 'student__student_id')
