"""URL configuration for frontend app."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('reset-password/', views.reset_password_view, name='reset-password'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),

    # Dashboards
    path('dashboard/admin/', views.admin_dashboard_view, name='admin-dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard_view, name='teacher-dashboard'),
    path('dashboard/student/', views.student_dashboard_view, name='student-dashboard'),

    # Students
    path('students/', views.student_list_view, name='student-list'),
    path('students/add/', views.student_add_view, name='student-add'),
    path('students/<int:id>/', views.student_detail_view, name='student-detail'),
    path('students/<int:id>/edit/', views.student_edit_view, name='student-edit'),
    path('students/<int:id>/id-card/', views.student_id_card_view, name='student-id-card'),
    path('students/<int:id>/transcript/', views.student_transcript_view, name='student-transcript'),

    # Academics
    path('departments/', views.departments_view, name='departments'),
    path('courses/', views.courses_view, name='courses'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('marks/', views.marks_view, name='marks'),

    # Examinations & Assignments
    path('exams/', views.exam_list_view, name='exam-list'),
    path('exams/admit-card/', views.admit_card_view, name='exam-admit-card'),
    path('exams/results/', views.results_view, name='exam-results'),
    path('assignments/', views.assignments_view, name='assignments'),

    # Student Portal & 23 Options
    path('fees/invoices/', views.fee_invoices_view, name='fee-invoices'),
    path('fees/structure/', views.fee_structure_view, name='fee-structure'),
    path('fees/history/', views.payment_history_view, name='payment-history'),
    path('materials/', views.study_materials_view, name='study-materials'),
    path('lessons/', views.lessons_view, name='lessons'),
    path('timetable/', views.class_timetable_view, name='class-timetable'),
    path('live-classes/', views.live_classes_view, name='live-classes'),
    path('library/', views.books_issued_view, name='books-issued'),
    path('stationary/', views.stationary_issued_view, name='stationary-issued'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('events/', views.events_view, name='events'),
    path('certificates/', views.certificates_view, name='certificates'),
    path('leave-requests/', views.leave_requests_view, name='leave-requests'),
    path('tickets/', views.support_tickets_view, name='support-tickets'),
    path('chat/', views.chat_view, name='chat'),
    path('noticeboard/', views.noticeboard_view, name='noticeboard'),

    # User management
    path('users/', views.users_view, name='users'),
]
