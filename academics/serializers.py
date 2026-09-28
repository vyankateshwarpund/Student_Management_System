"""Serializers for academic structure: Departments, Courses, Subjects, Marks."""
from rest_framework import serializers
from .models import Department, Course, Subject, Marks
from students.models import Student


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""
    courses_count = serializers.IntegerField(source='courses.count', read_only=True)
    students_count = serializers.IntegerField(source='students.count', read_only=True)

    class Meta:
        model = Department
        fields = (
            'id', 'name', 'code', 'description',
            'courses_count', 'students_count',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    subjects_count = serializers.IntegerField(source='subjects.count', read_only=True)
    students_count = serializers.IntegerField(source='students.count', read_only=True)

    class Meta:
        model = Course
        fields = (
            'id', 'name', 'code', 'department',
            'department_name', 'department_code',
            'duration', 'status',
            'subjects_count', 'students_count',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model."""
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    department_name = serializers.CharField(source='course.department.name', read_only=True)

    class Meta:
        model = Subject
        fields = (
            'id', 'name', 'code', 'course',
            'course_name', 'course_code', 'department_name',
            'semester', 'credits',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class MarksSerializer(serializers.ModelSerializer):
    """Serializer for Marks creation and update."""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_code = serializers.CharField(source='student.student_id', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)

    class Meta:
        model = Marks
        fields = (
            'id', 'student', 'student_name', 'student_code',
            'subject', 'subject_name', 'subject_code',
            'semester', 'academic_year',
            'internal_marks', 'external_marks', 'practical_marks',
            'total_marks', 'grade',
            'created_by', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'total_marks', 'grade', 'created_by', 'created_at', 'updated_at')

    def validate(self, attrs):
        # Validate marks ranges
        internal = attrs.get('internal_marks', getattr(self.instance, 'internal_marks', 0))
        external = attrs.get('external_marks', getattr(self.instance, 'external_marks', 0))
        practical = attrs.get('practical_marks', getattr(self.instance, 'practical_marks', 0))

        if internal < 0 or internal > 100:
            raise serializers.ValidationError({'internal_marks': 'Internal marks must be between 0 and 100.'})
        if external < 0 or external > 100:
            raise serializers.ValidationError({'external_marks': 'External marks must be between 0 and 100.'})
        if practical < 0 or practical > 100:
            raise serializers.ValidationError({'practical_marks': 'Practical marks must be between 0 and 100.'})

        return attrs
