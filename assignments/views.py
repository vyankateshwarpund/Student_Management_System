"""Views for assignments and assignment submissions."""
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Assignment, AssignmentSubmission
from .serializers import AssignmentSerializer, AssignmentSubmissionSerializer
from accounts.permissions import IsAdminOrTeacher
from students.models import Student
from utils.response import success_response, created_response, error_response


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    CRUD for assignments.
    Faculty & Admin can create/update.
    Students can list, view, and submit.
    """
    queryset = Assignment.objects.select_related('subject', 'subject__course', 'teacher', 'teacher__user').prefetch_related('submissions')
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['subject', 'subject__course', 'subject__semester', 'teacher']
    search_fields = ['title', 'description', 'subject__name', 'subject__code']
    ordering_fields = ['due_date', 'created_at']
    ordering = ['-due_date']

    def get_queryset(self):
        """Scope assignments so students only see coursework for their enrolled course & semester."""
        user = self.request.user
        qs = Assignment.objects.select_related(
            'subject', 'subject__course', 'teacher', 'teacher__user'
        ).prefetch_related('submissions')

        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            if student:
                return qs.filter(
                    Q(subject__course=student.course, subject__semester=student.semester) |
                    Q(submissions__student=student)
                ).distinct()
            return qs.none()
        elif user.role == 'teacher':
            teacher = getattr(user, 'teacher_profile', None)
            if teacher:
                return qs.filter(
                    Q(teacher=teacher) |
                    Q(subject__in=teacher.subjects.all()) |
                    Q(subject__course__department=teacher.department)
                ).distinct()
            return qs.none()
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'submissions']:
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message='Assignments retrieved successfully')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message='Assignment details retrieved')

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if request.user.role == 'teacher' and not data.get('teacher'):
            teacher = getattr(request.user, 'teacher_profile', None)
            if teacher:
                data['teacher'] = teacher.id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            assignment = serializer.save()
            return created_response(data=self.get_serializer(assignment).data, message='Assignment published successfully')
        return error_response(message='Failed to create assignment', errors=serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            assignment = serializer.save()
            return success_response(data=self.get_serializer(assignment).data, message='Assignment updated successfully')
        return error_response(message='Failed to update assignment', errors=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message='Assignment deleted successfully')

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        """
        POST /api/assignments/{id}/submit/
        Allows a student to submit their work for this assignment.
        """
        assignment = self.get_object()
        user = request.user

        student = None
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
        else:
            student_id = request.data.get('student')
            if student_id:
                student = Student.objects.filter(id=student_id).first()

        if not student:
            return error_response(message='Only registered students can submit coursework', status_code=status.HTTP_400_BAD_REQUEST)

        submission_text = request.data.get('submission_text', '')
        attachment = request.FILES.get('attachment')

        if not submission_text and not attachment:
            return error_response(message='Please provide submission text or attach a file', status_code=status.HTTP_400_BAD_REQUEST)

        # Check if past due date
        status_val = AssignmentSubmission.SubmissionStatus.LATE if assignment.is_past_due else AssignmentSubmission.SubmissionStatus.SUBMITTED

        submission, created = AssignmentSubmission.objects.update_or_create(
            assignment=assignment,
            student=student,
            defaults={
                'submission_text': submission_text,
                'status': status_val,
                'submitted_at': timezone.now(),
                **({'attachment': attachment} if attachment else {})
            }
        )

        msg = 'Assignment submitted successfully' if created else 'Assignment resubmitted successfully'
        return success_response(
            data=AssignmentSubmissionSerializer(submission).data,
            message=msg,
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], url_path='submissions')
    def submissions(self, request, pk=None):
        """GET /api/assignments/{id}/submissions/ -> List all student submissions for this assignment."""
        assignment = self.get_object()
        submissions = assignment.submissions.select_related('student', 'student__user', 'graded_by', 'graded_by__user')
        serializer = AssignmentSubmissionSerializer(submissions, many=True)
        return success_response(data=serializer.data, message='Submissions retrieved successfully')


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    """View and grade assignment submissions."""
    queryset = AssignmentSubmission.objects.select_related(
        'assignment', 'student', 'student__user', 'graded_by', 'graded_by__user'
    )
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['assignment', 'student', 'status']
    search_fields = ['student__student_id', 'student__user__first_name', 'student__user__last_name']

    def get_queryset(self):
        user = self.request.user
        qs = AssignmentSubmission.objects.select_related(
            'assignment', 'student', 'student__user', 'graded_by', 'graded_by__user'
        )
        if user.role == 'student':
            student = getattr(user, 'student_profile', None)
            return qs.filter(student=student) if student else qs.none()
        elif user.role == 'teacher':
            teacher = getattr(user, 'teacher_profile', None)
            if teacher:
                return qs.filter(
                    Q(assignment__teacher=teacher) |
                    Q(assignment__subject__course__department=teacher.department)
                )
        return qs

    def get_permissions(self):
        if self.action in ['destroy']:
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        submission = self.get_object()
        if request.user.role == 'student':
            if submission.status == AssignmentSubmission.SubmissionStatus.GRADED:
                return error_response(
                    message='Cannot modify a submission that has already been graded by faculty.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            if any(k in request.data for k in ('marks_obtained', 'feedback', 'status', 'graded_by', 'graded_at', 'student', 'assignment')):
                return error_response(
                    message='Students cannot alter grading marks, evaluation status, or metadata.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role == 'student':
            return error_response(
                message='Students cannot delete submitted coursework records.',
                status_code=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message='Submissions retrieved')

    @action(detail=True, methods=['post'], url_path='grade', permission_classes=[IsAuthenticated, IsAdminOrTeacher])
    def grade(self, request, pk=None):
        """
        POST /api/assignments/submissions/{id}/grade/
        Grade a student submission with marks and feedback.
        """
        submission = self.get_object()
        marks = request.data.get('marks_obtained')
        feedback = request.data.get('feedback', '')

        if marks is None:
            return error_response(message='Marks obtained is required for grading', status_code=status.HTTP_400_BAD_REQUEST)

        try:
            marks = float(marks)
        except ValueError:
            return error_response(message='Marks must be a valid number', status_code=status.HTTP_400_BAD_REQUEST)

        if marks < 0 or marks > submission.assignment.max_marks:
            return error_response(
                message=f"Marks must be between 0 and {submission.assignment.max_marks}",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        teacher = None
        if request.user.role == 'teacher':
            teacher = getattr(request.user, 'teacher_profile', None)

        submission.marks_obtained = marks
        submission.feedback = feedback
        submission.status = AssignmentSubmission.SubmissionStatus.GRADED
        submission.graded_by = teacher
        submission.graded_at = timezone.now()
        submission.save()

        return success_response(
            data=self.get_serializer(submission).data,
            message='Submission evaluated and graded successfully'
        )
