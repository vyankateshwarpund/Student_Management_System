"""Views serving HTML templates for the frontend web interface."""
from django.shortcuts import render, redirect


def index_view(request):
    """Home / landing view that redirects to login or dashboard."""
    return render(request, 'dashboard/index.html')


def login_view(request):
    """User login view."""
    return render(request, 'auth/login.html')


def reset_password_view(request):
    """Password reset view."""
    return render(request, 'auth/reset_password.html')


def register_view(request):
    """Public registration is disabled. Redirect to login."""
    return redirect('/login/')


def admin_dashboard_view(request):
    """Admin analytics dashboard."""
    return render(request, 'dashboard/admin_dashboard.html')


def teacher_dashboard_view(request):
    """Teacher dashboard."""
    return render(request, 'dashboard/teacher_dashboard.html')


def student_dashboard_view(request):
    """Student dashboard."""
    return render(request, 'dashboard/student_dashboard.html')


def student_list_view(request):
    """List students with search, filters, sorting, and pagination."""
    return render(request, 'students/student_list.html')


def student_add_view(request):
    """Add student form."""
    return render(request, 'students/student_form.html', {'is_edit': False})


def student_edit_view(request, id):
    """Edit student form."""
    return render(request, 'students/student_form.html', {'is_edit': True, 'student_id': id})


def student_detail_view(request, id):
    """Student profile details view."""
    return render(request, 'students/student_detail.html', {'student_id': id})


def student_id_card_view(request, id):
    """Printable digital student ID badge view."""
    return render(request, 'students/id_card.html', {'student_id': id})


def student_transcript_view(request, id):
    """Printable official university transcript / marksheet view."""
    return render(request, 'students/transcript.html', {'student_id': id})


def departments_view(request):
    """Departments management view."""
    return render(request, 'academics/departments.html')


def courses_view(request):
    """Courses management view."""
    return render(request, 'academics/courses.html')


def attendance_view(request):
    """Attendance management and summary view."""
    return render(request, 'attendance/attendance_page.html')


def marks_view(request):
    """Marks and grades management view."""
    return render(request, 'academics/marks_page.html')


def users_view(request):
    """User management view for admins."""
    return render(request, 'users/users_page.html')


def profile_view(request):
    """User own profile view."""
    return render(request, 'users/profile_page.html')


def exam_list_view(request):
    """Examinations and schedules list view."""
    return render(request, 'exams/exam_list.html')


def admit_card_view(request):
    """Printable examination hall ticket / admit card view."""
    return render(request, 'exams/admit_card.html')


def results_view(request):
    """Interactive semester examination results portal."""
    return render(request, 'exams/results_page.html')


def assignments_view(request):
    """Coursework and assignments management view."""
    return render(request, 'assignments/assignment_list.html')


# --- Student Portal & 23 Options Views ---

def fee_invoices_view(request):
    return render(request, 'portal/fee_invoices.html')


def fee_structure_view(request):
    return render(request, 'portal/fee_structure.html')


def payment_history_view(request):
    return render(request, 'portal/payment_history.html')


def study_materials_view(request):
    return render(request, 'portal/study_materials.html')


def lessons_view(request):
    return render(request, 'portal/lessons.html')


def class_timetable_view(request):
    return render(request, 'portal/class_timetable.html')


def live_classes_view(request):
    return render(request, 'portal/live_classes.html')


def books_issued_view(request):
    return render(request, 'portal/books_issued.html')


def stationary_issued_view(request):
    return render(request, 'portal/stationary_issued.html')


def calendar_view(request):
    return render(request, 'portal/calendar_page.html')


def events_view(request):
    return render(request, 'portal/events_page.html')


def certificates_view(request):
    return render(request, 'portal/certificates_page.html')


def leave_requests_view(request):
    return render(request, 'portal/leave_requests.html')


def support_tickets_view(request):
    return render(request, 'portal/support_tickets.html')


def chat_view(request):
    return render(request, 'portal/chat_page.html')


def noticeboard_view(request):
    return render(request, 'portal/noticeboard.html')


