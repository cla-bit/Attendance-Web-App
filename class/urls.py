from django.urls import path
from .views import (home, user_login, user_logout, register, lecturer_profile,
                    student_profile, lecturer_dashboard, create_course, generate_qr,
                    view_qr, attendance_summary, download_attendance, student_dashboard, scan_qr,
                    student_attendance_summary, mark_attendance
                    )

urlpatterns = [
    # Authentication
    path('', home, name='home'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),

    # Profile
    path('lecturer/profile/', lecturer_profile, name='lecturer_profile'),
    path('student/profile/', student_profile, name='student_profile'),

    # Lecturer URLs
    path('lecturer/dashboard/', lecturer_dashboard, name='lecturer_dashboard'),
    path('lecturer/create-course/', create_course, name='create_course'),
    path('lecturer/generate-qr/', generate_qr, name='generate_qr'),
    path('lecturer/view-qr/<int:session_id>/', view_qr, name='view_qr'),
    path('lecturer/attendance-summary/', attendance_summary, name='attendance_summary'),
    path('lecturer/attendance-summary/<int:course_id>/', attendance_summary, name='attendance_summary_course'),
    path('lecturer/download-attendance/<int:course_id>/', download_attendance, name='download_attendance'),

    # Student URLs
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('student/scan-qr/', scan_qr, name='scan_qr'),
    path('student/attendance-summary/', student_attendance_summary, name='student_attendance_summary'),

    # API
    path('mark-attendance/<uuid:qr_code_id>/', mark_attendance, name='mark_attendance'),
]