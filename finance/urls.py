"""URL patterns for finance app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeeStructureViewSet,
    FeeInvoiceViewSet,
    FeePaymentViewSet,
    student_fee_summary,
    institution_fee_report,
)

router = DefaultRouter()
router.register(r'structures', FeeStructureViewSet, basename='fee-structure')
router.register(r'invoices', FeeInvoiceViewSet, basename='fee-invoice')
router.register(r'payments', FeePaymentViewSet, basename='fee-payment')

urlpatterns = [
    path('summary/', student_fee_summary, name='fee-summary'),
    path('report/', institution_fee_report, name='fee-report'),
    path('', include(router.urls)),
]
