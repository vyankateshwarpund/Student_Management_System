"""Serializers for Student CRUD operations."""
from rest_framework import serializers
from .models import Student
from academics.models import Department, Course


class StudentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for student list views."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            'id', 'student_id', 'first_name', 'last_name', 'full_name',
            'email', 'department', 'department_name',
            'course', 'course_name', 'semester', 'status',
            'profile_photo',
        )

    def get_full_name(self, obj):
        return obj.full_name


class StudentDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer with nested department and course."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = (
            'id', 'student_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'date_of_birth', 'gender',
            'address', 'city', 'state', 'pincode',
            'department', 'department_name', 'department_code',
            'course', 'course_name', 'course_code',
            'year', 'semester',
            'admission_date', 'profile_photo', 'status',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.full_name


class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating students with validation."""

    class Meta:
        model = Student
        fields = (
            'id', 'student_id', 'first_name', 'last_name',
            'email', 'phone', 'date_of_birth', 'gender',
            'address', 'city', 'state', 'pincode',
            'department', 'course', 'year', 'semester',
            'admission_date', 'profile_photo', 'status',
        )
        read_only_fields = ('id',)

    def validate_email(self, value):
        """Ensure email is unique (case-insensitive)."""
        qs = Student.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A student with this email already exists.')
        return value.lower()

    def validate_student_id(self, value):
        """Ensure student_id is unique."""
        qs = Student.objects.filter(student_id=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A student with this ID already exists.')
        return value

    def validate_semester(self, value):
        """Semester must be between 1 and 8."""
        if value < 1 or value > 8:
            raise serializers.ValidationError('Semester must be between 1 and 8.')
        return value

    def validate(self, attrs):
        """Ensure course belongs to the selected department."""
        department = attrs.get('department', getattr(self.instance, 'department', None))
        course = attrs.get('course', getattr(self.instance, 'course', None))
        if department and course and course.department != department:
            raise serializers.ValidationError({
                'course': 'This course does not belong to the selected department.'
            })
        return attrs
