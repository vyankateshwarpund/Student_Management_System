"""Serializers for user authentication and management."""
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'phone',
        )
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower()

    def validate(self, attrs):
        """Ensure passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': 'Passwords do not match.'}
            )
        return attrs

    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Allow login with email or username
        user = authenticate(username=username, password=password)
        if user is None:
            # Try email-based login
            try:
                user_obj = User.objects.get(email__iexact=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is None:
            raise serializers.ValidationError('Invalid credentials.')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user CRUD (admin use)."""
    full_name = serializers.SerializerMethodField()
    profile_info = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'full_name', 'role', 'phone', 'profile_photo',
            'is_active', 'date_joined', 'last_login', 'profile_info',
        )
        read_only_fields = ('id', 'date_joined', 'last_login')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_profile_info(self, obj):
        if obj.role == 'student':
            student = getattr(obj, 'student_profile', None)
            if student:
                course_name = student.course.name if student.course else ''
                dept_name = student.department.name if student.department else ''
                course_short = student.course.code if (student.course and student.course.code) else (course_name[:10] if course_name else 'Student')
                return {
                    'role_title': 'Student',
                    'subtitle': f"{course_short} • Sem {student.semester}",
                    'student_id': student.student_id,
                    'roll_number': getattr(student, 'roll_number', student.student_id),
                    'course': course_name,
                    'course_code': student.course.code if student.course else '',
                    'semester': student.semester,
                    'department': dept_name,
                }
            return {'role_title': 'Student', 'subtitle': 'Student Portal'}
        elif obj.role == 'teacher':
            teacher = getattr(obj, 'teacher_profile', None)
            if teacher:
                dept_name = teacher.department.name if teacher.department else ''
                dept_short = teacher.department.code if (teacher.department and teacher.department.code) else dept_name
                return {
                    'role_title': 'Teacher / Faculty',
                    'subtitle': f"Faculty • {dept_short}" if dept_short else 'Faculty / Teacher',
                    'employee_id': teacher.employee_id,
                    'department': dept_name,
                    'qualification': teacher.qualification,
                }
            return {'role_title': 'Teacher / Faculty', 'subtitle': 'Faculty / Teacher'}
        else:
            return {'role_title': 'Administrator', 'subtitle': 'System Administrator'}


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for authenticated user's own profile."""
    full_name = serializers.SerializerMethodField()
    profile_info = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'phone', 'profile_photo',
            'is_active', 'date_joined', 'last_login', 'profile_info',
        )
        read_only_fields = (
            'id', 'username', 'email', 'role',
            'is_active', 'date_joined', 'last_login',
        )

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        # Sync basic personal details to linked student profile
        student = getattr(instance, 'student_profile', None)
        if student:
            if 'first_name' in validated_data:
                student.first_name = validated_data['first_name']
            if 'last_name' in validated_data:
                student.last_name = validated_data['last_name']
            if 'phone' in validated_data:
                student.phone = validated_data['phone']
            # Allow basic personal address/contact fields if provided
            request = self.context.get('request')
            if request and hasattr(request, 'data') and isinstance(request.data, dict):
                for field in ('address', 'city', 'state', 'pincode'):
                    if field in request.data:
                        setattr(student, field, request.data[field])
            student.save()
        return instance

    def get_profile_info(self, obj):
        if obj.role == 'student':
            student = getattr(obj, 'student_profile', None)
            if student:
                course_name = student.course.name if student.course else ''
                dept_name = student.department.name if student.department else ''
                course_short = student.course.code if (student.course and student.course.code) else (course_name[:10] if course_name else 'Student')
                return {
                    'role_title': 'Student',
                    'subtitle': f"{course_short} • Sem {student.semester}",
                    'student_id': student.student_id,
                    'roll_number': getattr(student, 'roll_number', student.student_id),
                    'course': course_name,
                    'course_code': student.course.code if student.course else '',
                    'semester': student.semester,
                    'department': dept_name,
                }
            return {'role_title': 'Student', 'subtitle': 'Student Portal'}
        elif obj.role == 'teacher':
            teacher = getattr(obj, 'teacher_profile', None)
            if teacher:
                dept_name = teacher.department.name if teacher.department else ''
                dept_short = teacher.department.code if (teacher.department and teacher.department.code) else dept_name
                return {
                    'role_title': 'Teacher / Faculty',
                    'subtitle': f"Faculty • {dept_short}" if dept_short else 'Faculty / Teacher',
                    'employee_id': teacher.employee_id,
                    'department': dept_name,
                    'qualification': teacher.qualification,
                }
            return {'role_title': 'Teacher / Faculty', 'subtitle': 'Faculty / Teacher'}
        else:
            return {'role_title': 'Administrator', 'subtitle': 'System Administrator'}


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
    )
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'New passwords do not match.'}
            )
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
