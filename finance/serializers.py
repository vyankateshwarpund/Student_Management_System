"""Serializers for fees, invoices, structures, and payments."""
from rest_framework import serializers
from .models import FeeStructure, FeeInvoice, FeePayment


class FeeStructureSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.code', read_only=True, default='')
    course_name = serializers.CharField(source='course.name', read_only=True, default='All Courses')

    class Meta:
        model = FeeStructure
        fields = (
            'id', 'course', 'course_code', 'course_name', 'academic_session',
            'fee_type', 'period', 'amount'
        )


class FeeInvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id_code = serializers.CharField(source='student.student_id', read_only=True)
    balance_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = FeeInvoice
        fields = (
            'id', 'student', 'student_name', 'student_id_code', 'invoice_no',
            'title', 'due_date', 'total_amount', 'paid_amount', 'balance_amount',
            'status', 'academic_session', 'created_at', 'updated_at'
        )


class FeePaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_id_code = serializers.CharField(source='student.student_id', read_only=True)
    invoice_title = serializers.CharField(source='invoice.title', read_only=True, default='')
    invoice_no = serializers.CharField(source='invoice.invoice_no', read_only=True, default='')

    class Meta:
        model = FeePayment
        fields = (
            'id', 'invoice', 'invoice_no', 'invoice_title', 'student',
            'student_name', 'student_id_code', 'transaction_id', 'amount',
            'payment_method', 'payment_date', 'receipt_no', 'notes'
        )
