"""Custom permission classes for role-based access control."""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow access only to admin users."""
    message = 'Admin access required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsTeacher(BasePermission):
    """Allow access only to teacher users."""
    message = 'Teacher access required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'teacher'
        )


class IsStudent(BasePermission):
    """Allow access only to student users."""
    message = 'Student access required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'student'
        )


class IsAdminOrTeacher(BasePermission):
    """Allow access to admin or teacher users."""
    message = 'Admin or Teacher access required.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'teacher')
        )


class IsOwnerOrAdmin(BasePermission):
    """Allow access if user is the object owner or an admin."""
    message = 'You can only access your own data.'

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        # Check if the object has a 'user' field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Check if the object IS a user
        return obj == request.user


class IsAdminOrReadOnly(BasePermission):
    """Admin gets full access, others get read-only."""
    message = 'Admin access required for this action.'

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return bool(request.user and request.user.is_authenticated)
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsAdminOrTeacherOrReadOnly(BasePermission):
    """Admin and Faculty get full access, students/others get read-only."""
    message = 'Admin or Faculty access required for this action.'

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return bool(request.user and request.user.is_authenticated)
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'teacher')
        )

