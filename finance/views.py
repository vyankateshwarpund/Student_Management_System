"""Views for student fees, invoices, payments, and financial summaries."""
import uuid
from decimal import Decimal
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import FeeStructure, FeeInvoice, FeePayment
from .serializers import FeeStructureSerializer, FeeInvoiceSerializer, FeePaymentSerializer
from accounts.permissions import IsAdminOrReadOnly, IsAdmin
from students.models import Student
from utils.response import success_response, created_response, error_response


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.select_related('course').all()
    serializer_class = FeeStructureSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filterset_fields = ['course', 'academic_session', 'period']
    search_fields = ['fee_type']


class FeeInvoiceViewSet(viewsets.ModelViewSet):
    queryset = FeeInvoice.objects.select_related('student', 'student__user').all()
    serializer_class = FeeInvoiceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student', 'status', 'academic_session']
    search_fields = ['invoice_no', 'title', 'student__student_id']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            return qs.filter(student=student) if student else qs.none()
        return qs

    @action(detail=True, methods=['post'], url_path='pay')
    def pay_invoice(self, request, pk=None):
        """Simulate paying an invoice."""
        invoice = self.get_object()
        amount = request.data.get('amount')
        try:
            pay_amount = Decimal(str(amount)) if amount else invoice.balance_amount
        except Exception:
            return error_response(message='Invalid amount supplied')

        if pay_amount <= 0:
            return error_response(message='Payment amount must be greater than zero')

        payment = FeePayment.objects.create(
            invoice=invoice,
            student=invoice.student,
            transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
            amount=pay_amount,
            payment_method=request.data.get('payment_method', 'Online / Card'),
            receipt_no=f"REC-{uuid.uuid4().hex[:8].upper()}",
            notes=request.data.get('notes', 'Online student portal payment')
        )

        invoice.paid_amount += pay_amount
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = FeeInvoice.InvoiceStatus.PAID
        else:
            invoice.status = FeeInvoice.InvoiceStatus.PARTIAL
        invoice.save()

        return created_response(
            data=FeePaymentSerializer(payment).data,
            message='Payment processed successfully'
        )

    def destroy(self, request, *args, **kwargs):
        invoice = self.get_object()
        # Security Guardrail 2: Admin cannot delete invoices with transaction records
        if invoice.payments.exists():
            return error_response(
                message="Cannot permanently delete an invoice with recorded financial transactions. You can update its status to cancelled instead.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        invoice.delete()
        return success_response(message="Fee invoice deleted successfully")


class FeePaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FeePayment.objects.select_related('student', 'invoice').all()
    serializer_class = FeePaymentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['student', 'payment_method']
    search_fields = ['transaction_id', 'receipt_no', 'student__student_id']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            return qs.filter(student=student) if student else qs.none()
        return qs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_fee_summary(request):
    """
    GET /api/fees/summary/?student_id=...
    Aggregates financial snapshot matching the dashboard reference image.
    """
    user = request.user
    student = None
    if user.role == 'student':
        student = getattr(user, 'student_profile', None)
    else:
        stu_id = request.query_params.get('student_id')
        if stu_id:
            if stu_id.isdigit():
                student = Student.objects.filter(id=stu_id).first()
            else:
                student = Student.objects.filter(student_id__iexact=stu_id).first()
        else:
            student = Student.objects.first()

    if not student:
        return error_response(message='Student record not found', status_code=status.HTTP_404_NOT_FOUND)

    # Calculate actual invoices and payments from database
    invoices = FeeInvoice.objects.filter(student=student)
    structures = FeeStructure.objects.filter(course=student.course) if student.course else FeeStructure.objects.all()
    if not structures.exists():
        structures = FeeStructure.objects.all()

    total_session_fee = sum(s.amount for s in structures) if structures.exists() else Decimal('0.00')
    paid_sum = FeePayment.objects.filter(student=student).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Pending invoices from database
    pending_invoices = invoices.exclude(status=FeeInvoice.InvoiceStatus.PAID)
    due_amount = sum(inv.balance_amount for inv in pending_invoices) if pending_invoices.exists() else max(Decimal('0.00'), total_session_fee - paid_sum)
    balance = due_amount

    data = {
        'student_id': student.student_id,
        'student_name': student.full_name,
        'currency_symbol': '₹',
        'previous_session_due': float(due_amount),
        'paid_amount': float(paid_sum),
        'total_session_fee': float(total_session_fee),
        'balance_amount': float(balance),
        'fee_types': [
            {
                'fee_type': s.fee_type,
                'period': s.period,
                'amount': float(s.amount)
            } for s in structures
        ]
    }

    return success_response(data=data, message='Fee summary retrieved')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def institution_fee_report(request):
    """
    GET /api/fees/report/
    Institutional financial analytics for Admin.
    """
    total_invoices = FeeInvoice.objects.count()
    paid_invoices = FeeInvoice.objects.filter(status=FeeInvoice.InvoiceStatus.PAID).count()
    partial_invoices = FeeInvoice.objects.filter(status=FeeInvoice.InvoiceStatus.PARTIAL).count()
    unpaid_invoices = FeeInvoice.objects.filter(status=FeeInvoice.InvoiceStatus.UNPAID).count()

    total_billed = FeeInvoice.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_collected = FeePayment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_outstanding = max(Decimal('0.00'), total_billed - total_collected)

    recent_payments = list(
        FeePayment.objects.select_related('student', 'invoice')
        .order_by('-payment_date')[:10]
        .values(
            'transaction_id', 'receipt_no', 'amount', 'payment_method',
            'payment_date', 'student__student_id', 'student__first_name',
            'student__last_name'
        )
    )

    data = {
        'summary': {
            'total_billed': float(total_billed),
            'total_collected': float(total_collected),
            'total_outstanding': float(total_outstanding),
            'collection_rate': round(float((total_collected / total_billed) * 100), 2) if total_billed > 0 else 0.0,
        },
        'invoices': {
            'total': total_invoices,
            'paid': paid_invoices,
            'partial': partial_invoices,
            'unpaid': unpaid_invoices,
        },
        'recent_payments': recent_payments,
    }
    return success_response(data=data, message='Institution fee report generated successfully')
