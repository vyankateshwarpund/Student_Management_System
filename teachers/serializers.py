"""Serializers for teacher management."""
from rest_framework import serializers
from .models import Teacher
from academics.models import Subject
from accounts.models import User
from accounts.serializers import UserSerializer


class TeacherSerializer(serializers.ModelSerializer):
    """Serializer for Teacher CRUD."""
    user_details = UserSerializer(source='user', read_only=True)
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    subject_details = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = (
            'id', 'user', 'user_details', 'employee_id', 'full_name',
            'department', 'department_name', 'department_code',
            'subjects', 'subject_details',
            'phone', 'qualification',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_subject_details(self, obj):
        return [
            {'id': s.id, 'name': s.name, 'code': s.code, 'semester': s.semester}
            for s in obj.subjects.all()
        ]

    def validate_employee_id(self, value):
        qs = Teacher.objects.filter(employee_id__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('A teacher with this employee ID already exists.')
        return value.upper()
