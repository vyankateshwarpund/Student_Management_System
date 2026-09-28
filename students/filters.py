"""Filters for student queryset using django-filter."""
import django_filters
from .models import Student


class StudentFilter(django_filters.FilterSet):
    """Filter students by department, course, semester, status, etc."""

    # Exact match filters
    department = django_filters.NumberFilter(field_name='department__id')
    department_code = django_filters.CharFilter(
        field_name='department__code',
        lookup_expr='iexact',
    )
    course = django_filters.NumberFilter(field_name='course__id')
    course_code = django_filters.CharFilter(
        field_name='course__code',
        lookup_expr='iexact',
    )
    semester = django_filters.NumberFilter()
    year = django_filters.NumberFilter()
    status = django_filters.CharFilter(lookup_expr='iexact')
    gender = django_filters.CharFilter(lookup_expr='iexact')

    # Date range filters
    admission_date_from = django_filters.DateFilter(
        field_name='admission_date',
        lookup_expr='gte',
    )
    admission_date_to = django_filters.DateFilter(
        field_name='admission_date',
        lookup_expr='lte',
    )

    # Created date range
    created_from = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__gte',
    )
    created_to = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__lte',
    )

    class Meta:
        model = Student
        fields = [
            'department', 'department_code',
            'course', 'course_code',
            'semester', 'year', 'status', 'gender',
            'admission_date_from', 'admission_date_to',
            'created_from', 'created_to',
        ]
