"""Dashboard views providing aggregated statistics and analytics for Admin, Teacher, and Student."""
from datetime import date
from decimal import Decimal
from django.db.models import Count, Avg, Sum, Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.permissions import IsAdmin, IsTeacher, IsAdminOrTeacher
from accounts.models import User
from students.models import Student
from academics.models import Department, Course, Subject, Marks
from attendance.models import Attendance
from teachers.models import Teacher
from assignments.models import Assignment, AssignmentSubmission
from examinations.models import Exam, ExamSchedule
from announcements.models import Announcement
from finance.models import FeeInvoice, FeePayment
from utils.response import success_response, error_response


class AdminDashboardView(APIView):
    """
    API endpoint for Admin Dashboard.
    Provides institution-wide statistics, department distributions, and attendance metrics.
    GET /api/dashboard/admin/
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        total_students = Student.objects.count()
        total_teachers = Teacher.objects.count()
        total_courses = Course.objects.count()
        total_departments = Department.objects.count()

        active_students = Student.objects.filter(status='active').count()
        inactive_students = Student.objects.filter(status='inactive').count()

        # Students by department (for charts)
        students_by_department = list(
            Department.objects.annotate(
                student_count=Count('students')
            ).values('name', 'code', 'student_count')
        )

        # Students by semester (for charts)
        students_by_semester = list(
            Student.objects.values('semester')
            .annotate(count=Count('id'))
            .order_by('semester')
        )

        # Students by gender (for charts)
        students_by_gender = list(
            Student.objects.values('gender')
            .annotate(count=Count('id'))
            .filter(gender__isnull=False)
        )

        # Overall attendance overview
        total_attendance = Attendance.objects.count()
        present_count = Attendance.objects.filter(status='present').count()
        absent_count = Attendance.objects.filter(status='absent').count()
        leave_count = Attendance.objects.filter(status='leave').count()
        attendance_percentage = (
            round((present_count / total_attendance) * 100, 2)
            if total_attendance > 0 else 0.0
        )

        # Recent registrations (last 5 students)
        recent_students = list(
            Student.objects.select_related('department', 'course')
            .order_by('-created_at')[:5]
            .values(
                'id', 'student_id', 'first_name', 'last_name',
                'email', 'department__name', 'course__name',
                'semester', 'status', 'created_at',
            )
        )

        # Overall fees overview
        total_billed = FeeInvoice.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        total_collected = FeePayment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        total_pending = max(Decimal('0.00'), total_billed - total_collected)

        # Assignments overview
        total_assignments = Assignment.objects.count()
        total_submissions = AssignmentSubmission.objects.count()

        # Examinations overview
        total_exams = Exam.objects.count()
        total_schedules = ExamSchedule.objects.count()

        # Announcements overview
        total_circulars = Announcement.objects.count()
        pinned_circulars = Announcement.objects.filter(is_pinned=True).count()

        data = {
            'overview': {
                'total_students': total_students,
                'total_teachers': total_teachers,
                'total_courses': total_courses,
                'total_departments': total_departments,
                'active_students': active_students,
                'inactive_students': inactive_students,
            },
            'fees_overview': {
                'total_billed': float(total_billed),
                'total_collected': float(total_collected),
                'total_pending': float(total_pending),
            },
            'assignments_overview': {
                'total_assignments': total_assignments,
                'total_submissions': total_submissions,
            },
            'examinations_overview': {
                'total_exams': total_exams,
                'total_schedules': total_schedules,
            },
            'notifications_overview': {
                'total_circulars': total_circulars,
                'pinned_circulars': pinned_circulars,
            },
            'charts': {
                'students_by_department': students_by_department,
                'students_by_semester': students_by_semester,
                'students_by_gender': students_by_gender,
            },
            'attendance_overview': {
                'total_records': total_attendance,
                'present': present_count,
                'absent': absent_count,
                'leave': leave_count,
                'percentage': attendance_percentage,
            },
            'recent_students': recent_students,
        }

        return success_response(data=data, message='Admin dashboard complete institution statistics retrieved successfully')


class TeacherDashboardView(APIView):
    """
    API endpoint for Teacher Dashboard.
    Provides statistics on assigned students, today's attendance, subjects, and recent marks.
    GET /api/dashboard/teacher/
    """
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]

    def get(self, request):
        user = request.user
        teacher = getattr(user, 'teacher_profile', None)

        if not teacher and user.role == 'admin':
            # Allow admin to preview a teacher dashboard via query param
            teacher_id = request.query_params.get('teacher_id')
            if teacher_id:
                teacher = Teacher.objects.filter(id=teacher_id).first()
            else:
                teacher = Teacher.objects.first()

        if not teacher:
            return error_response(
                message='Teacher profile not found. Please ensure a teacher profile is linked.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Subjects taught by this teacher
        subjects = list(
            teacher.subjects.select_related('course').values(
                'id', 'name', 'code', 'semester', 'course__name', 'credits'
            )
        )
        subject_ids = [s['id'] for s in subjects]

        # Assigned students (students in the teacher's department or courses of subjects taught)
        assigned_students_count = Student.objects.filter(
            Q(department=teacher.department) |
            Q(course__subjects__in=subject_ids)
        ).distinct().count()

        # Today's attendance
        today = date.today()
        today_attendance = Attendance.objects.filter(
            teacher=teacher.user,
            date=today,
        )
        today_present = today_attendance.filter(status='present').count()
        today_absent = today_attendance.filter(status='absent').count()
        today_leave = today_attendance.filter(status='leave').count()
        today_total = today_attendance.count()

        # Recent marks entered by this teacher (or for their subjects)
        recent_marks = list(
            Marks.objects.filter(
                Q(created_by=teacher.user) | Q(subject__in=subject_ids)
            )
            .select_related('student', 'subject')
            .order_by('-created_at')[:5]
            .values(
                'id', 'student__student_id', 'student__first_name',
                'student__last_name', 'subject__name', 'semester',
                'total_marks', 'grade', 'created_at',
            )
        )

        # Attendance statistics recorded by this teacher
        total_marked = Attendance.objects.filter(teacher=teacher.user).count()
        total_present_marked = Attendance.objects.filter(teacher=teacher.user, status='present').count()
        teacher_attendance_rate = (
            round((total_present_marked / total_marked) * 100, 2)
            if total_marked > 0 else 0.0
        )

        data = {
            'teacher_profile': {
                'id': teacher.id,
                'employee_id': teacher.employee_id,
                'name': teacher.full_name,
                'department': teacher.department.name,
                'qualification': teacher.qualification,
                'phone': teacher.phone,
            },
            'assigned_students_count': assigned_students_count,
            'subjects': subjects,
            'todays_attendance': {
                'date': str(today),
                'total': today_total,
                'present': today_present,
                'absent': today_absent,
                'leave': today_leave,
            },
            'recent_marks': recent_marks,
            'attendance_stats': {
                'total_recorded': total_marked,
                'present_recorded': total_present_marked,
                'attendance_rate': teacher_attendance_rate,
            },
        }

        return success_response(data=data, message='Teacher dashboard statistics retrieved successfully')


class StudentDashboardView(APIView):
    """
    API endpoint for Student Dashboard.
    Provides personalized academic performance, attendance percentage, and enrolled subjects.
    GET /api/dashboard/student/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        student = getattr(user, 'student_profile', None)

        if not student and user.role in ['admin', 'teacher']:
            # Allow admin or teacher to view a student's dashboard
            student_param = request.query_params.get('student_id')
            if student_param:
                if student_param.isdigit():
                    student = Student.objects.filter(id=student_param).first()
                else:
                    student = Student.objects.filter(student_id__iexact=student_param).first()
            else:
                student = Student.objects.first()

        if not student:
            return error_response(
                message='Student profile not found. Please ensure a student profile is linked.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Profile summary
        roll_no = student.student_id[-3:] if (student.student_id and len(student.student_id) >= 3 and student.student_id[-3:].isdigit()) else f"{student.id:03d}"
        profile = {
            'id': student.id,
            'student_id': student.student_id,
            'roll_number': roll_no,
            'full_name': student.full_name,
            'email': student.email,
            'phone': student.phone,
            'department': student.department.name if student.department else '',
            'department_code': student.department.code if student.department else '',
            'course': student.course.name if student.course else '',
            'course_code': student.course.code if student.course else '',
            'semester': student.semester,
            'year': student.year or ((student.semester + 1) // 2 if student.semester else 1),
            'status': student.status,
            'admission_date': student.admission_date,
            'profile_photo': student.profile_photo.url if student.profile_photo else None,
        }

        # Current subjects for this semester
        enrolled_subjects = list(
            Subject.objects.filter(
                course=student.course,
                semester=student.semester,
            ).values('id', 'name', 'code', 'credits')
        )

        # Attendance calculation
        attendance_records = Attendance.objects.filter(student=student)
        total_classes = attendance_records.count()
        total_present = attendance_records.filter(status='present').count()
        total_absent = attendance_records.filter(status='absent').count()
        total_leave = attendance_records.filter(status='leave').count()
        attendance_percentage = (
            round((total_present / total_classes) * 100, 2)
            if total_classes > 0 else 0.0
        )

        # Recent marks
        student_marks = list(
            Marks.objects.filter(student=student)
            .select_related('subject')
            .order_by('-created_at')
            .values(
                'id', 'subject__name', 'subject__code', 'semester',
                'internal_marks', 'external_marks', 'practical_marks',
                'total_marks', 'grade', 'academic_year',
            )
        )

        # Academic performance metrics
        avg_marks = (
            Marks.objects.filter(student=student)
            .aggregate(avg=Avg('total_marks'))['avg']
        )
        avg_marks = round(float(avg_marks), 2) if avg_marks else 0.0

        graded_count = len(student_marks)
        passed_count = sum(1 for m in student_marks if m['grade'] != 'F')

        # Pending assignments calculation from real database
        assignments_qs = Assignment.objects.filter(
            Q(subject__course=student.course) | Q(subject__isnull=True)
        )
        if student.semester:
            assignments_qs = assignments_qs.filter(
                Q(subject__semester=student.semester) | Q(subject__isnull=True)
            )
        if not assignments_qs.exists():
            assignments_qs = Assignment.objects.all()

        submitted_ids = AssignmentSubmission.objects.filter(
            student=student, status__in=['submitted', 'graded']
        ).values_list('assignment_id', flat=True)

        pending_assignments_qs = assignments_qs.exclude(id__in=submitted_ids).order_by('due_date')
        pending_assignments_count = pending_assignments_qs.count()
        pending_assignments_list = [
            {
                'id': a.id,
                'title': a.title,
                'subject_name': a.subject.name if a.subject else 'General',
                'due_date': a.due_date.strftime('%d %b') if a.due_date else '',
                'due_date_iso': a.due_date.isoformat() if a.due_date else '',
            }
            for a in pending_assignments_qs[:5]
        ]

        # Upcoming examinations calculation from real database
        exam_schedules_qs = ExamSchedule.objects.filter(
            Q(subject__course=student.course) | Q(subject__isnull=True)
        )
        if student.semester:
            exam_schedules_qs = exam_schedules_qs.filter(
                Q(subject__semester=student.semester) | Q(subject__isnull=True)
            )
        if not exam_schedules_qs.exists():
            exam_schedules_qs = ExamSchedule.objects.all()

        upcoming_schedules = exam_schedules_qs.select_related('exam', 'subject').order_by('date', 'start_time')[:5]
        next_exam = None
        if upcoming_schedules:
            first_exam = upcoming_schedules[0]
            days_left = (first_exam.date - date.today()).days if first_exam.date else None
            next_exam = {
                'id': first_exam.id,
                'exam_title': first_exam.exam.title if first_exam.exam else 'Exam',
                'subject_name': first_exam.subject.name if first_exam.subject else 'General',
                'date_str': first_exam.date.strftime('%d %b') if first_exam.date else '',
                'time_str': f"{first_exam.start_time.strftime('%I:%M %p')} - {first_exam.end_time.strftime('%I:%M %p')}" if first_exam.start_time and first_exam.end_time else '',
                'room': first_exam.room_number or 'Main Hall',
                'days_left': f"{days_left} Days" if (days_left is not None and days_left > 0) else ('Today' if days_left == 0 else 'Past Due'),
            }

        upcoming_exams_list = [
            {
                'id': es.id,
                'title': es.exam.title if es.exam else (es.subject.name if es.subject else 'Exam'),
                'subject': es.subject.name if es.subject else 'General',
                'location': es.room_number or 'Main Hall',
                'time': f"{es.start_time.strftime('%I:%M %p')} - {es.end_time.strftime('%I:%M %p')}" if es.start_time and es.end_time else '',
                'date': es.date.strftime('%d %b') if es.date else '',
            }
            for es in upcoming_schedules
        ]

        # Financial summary from database
        invoices = FeeInvoice.objects.filter(student=student)
        total_invoiced = invoices.aggregate(s=Sum('total_amount'))['s'] or Decimal('0.00')
        total_paid = invoices.aggregate(s=Sum('paid_amount'))['s'] or Decimal('0.00')
        unpaid_invoices = invoices.exclude(status='paid').order_by('due_date')
        earliest_unpaid = unpaid_invoices.first()
        fee_balance = max(Decimal('0.00'), total_invoiced - total_paid)

        # Real notices / announcements from database
        notices_qs = Announcement.objects.filter(
            Q(target_role='all') | Q(target_role='student')
        ).order_by('-is_pinned', '-created_at')[:5]
        notices_list = [
            {
                'id': n.id,
                'title': n.title,
                'content': n.content,
                'date': n.created_at.strftime('%b %d') if n.created_at else '',
                'category': n.category,
                'is_pinned': n.is_pinned,
            }
            for n in notices_qs
        ]

        data = {
            'profile': profile,
            'enrolled_subjects': enrolled_subjects,
            'attendance': {
                'total_classes': total_classes,
                'present': total_present,
                'absent': total_absent,
                'leave': total_leave,
                'percentage': attendance_percentage,
            },
            'recent_marks': student_marks,
            'academic_performance': {
                'average_score': avg_marks,
                'total_subjects_graded': graded_count,
                'passed_subjects': passed_count,
            },
            'pending_assignments': {
                'count': pending_assignments_count,
                'items': pending_assignments_list,
            },
            'upcoming_exams': {
                'next_exam': next_exam,
                'items': upcoming_exams_list,
            },
            'fees': {
                'total_amount': float(total_invoiced),
                'paid_amount': float(total_paid),
                'balance_amount': float(fee_balance),
                'due_date': earliest_unpaid.due_date.strftime('%b %d, %Y') if earliest_unpaid and earliest_unpaid.due_date else None,
                'status': 'paid' if fee_balance <= 0 else 'unpaid',
            },
            'latest_notices': notices_list,
        }

        return success_response(data=data, message='Student dashboard retrieved successfully')


class UnifiedDashboardView(APIView):
    """
    Auto-routing dashboard endpoint.
    Automatically returns the appropriate dashboard data based on the authenticated user's role.
    GET /api/dashboard/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.user.role
        if role == User.Role.ADMIN:
            return AdminDashboardView().get(request)
        elif role == User.Role.TEACHER:
            return TeacherDashboardView().get(request)
        elif role == User.Role.STUDENT:
            return StudentDashboardView().get(request)
        else:
            return error_response(message='Unknown user role', status_code=status.HTTP_400_BAD_REQUEST)
