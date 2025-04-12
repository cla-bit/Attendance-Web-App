from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import User, Lecturer, Student, Course, ClassSession, Attendance
from .forms import (
    CustomAuthenticationForm, LecturerProfileForm, StudentProfileForm,
    CourseForm, ClassSessionForm, QRScanForm
)
import csv
from io import StringIO
import uuid

def home(request):
    return render(request, 'home.html')

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            identifier = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, identifier=identifier, password=password)

            if user is not None:
                login(request, user)
                if user.is_lecturer:
                    return redirect('lecturer_dashboard')
                elif user.is_student:
                    return redirect('student_dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def lecturer_profile(request):
    if not request.user.is_lecturer:
        return redirect('home')

    lecturer = request.user.lecturer

    if request.method == 'POST':
        form = LecturerProfileForm(request.POST, instance=lecturer)
        if form.is_valid():
            form.save()
            return redirect('lecturer_dashboard')
    else:
        form = LecturerProfileForm(instance=lecturer)

    return render(request, 'lecturer_profile.html', {'form': form})

@login_required
def student_profile(request):
    if not request.user.is_student:
        return redirect('home')

    student = request.user.student

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_dashboard')
    else:
        form = StudentProfileForm(instance=student)

    return render(request, 'student_profile.html', {'form': form})

# Lecturer Views
@login_required
def lecturer_dashboard(request):
    if not request.user.is_lecturer:
        return redirect('home')

    lecturer = request.user.lecturer
    courses = Course.objects.filter(lecturer=lecturer)
    recent_sessions = ClassSession.objects.filter(course__lecturer=lecturer).order_by('-date')[:5]

    context = {
        'lecturer': lecturer,
        'courses': courses,
        'recent_sessions': recent_sessions,
    }
    return render(request, 'lecturer_dashboard.html', context)

@login_required
def create_course(request):
    if not request.user.is_lecturer:
        return redirect('home')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.lecturer = request.user.lecturer
            course.save()
            return redirect('lecturer_dashboard')
    else:
        form = CourseForm()

    return render(request, 'lecturer_create_course.html', {'form': form})

@login_required
def generate_qr(request):
    if not request.user.is_lecturer:
        return redirect('home')

    lecturer = request.user.lecturer

    if request.method == 'POST':
        form = ClassSessionForm(request.POST, lecturer=lecturer)
        if form.is_valid():
            class_session = form.save()
            return redirect('view_qr', session_id=class_session.id)
    else:
        form = ClassSessionForm(lecturer=lecturer)

    return render(request, 'lecturer_generate_qr.html', {'form': form})

@login_required
def view_qr(request, session_id):
    if not request.user.is_lecturer:
        return redirect('home')

    class_session = get_object_or_404(ClassSession, id=session_id, course__lecturer=request.user.lecturer)
    return render(request, 'lecturer_view_qr.html', {'class_session': class_session})

@login_required
def attendance_summary(request, course_id=None):
    if not request.user.is_lecturer:
        return redirect('home')

    lecturer = request.user.lecturer
    courses = Course.objects.filter(lecturer=lecturer)

    selected_course = None
    sessions = None
    attendance_data = None

    if course_id:
        selected_course = get_object_or_404(Course, id=course_id, lecturer=lecturer)
        sessions = ClassSession.objects.filter(course=selected_course).order_by('date')

        # Get all students who have attended any session for this course
        students = Student.objects.filter(
            attendance__class_session__course=selected_course
        ).distinct()

        # Prepare attendance data
        attendance_data = []
        for student in students:
            student_attendance = {
                'student': student,
                'total_sessions': sessions.count(),
                'attended_sessions': Attendance.objects.filter(
                    student=student,
                    class_session__course=selected_course
                ).count(),
                'sessions': []
            }

            for session in sessions:
                attended = Attendance.objects.filter(
                    student=student,
                    class_session=session
                ).exists()
                student_attendance['sessions'].append({
                    'session': session,
                    'attended': attended
                })

            attendance_data.append(student_attendance)

    context = {
        'courses': courses,
        'selected_course': selected_course,
        'sessions': sessions,
        'attendance_data': attendance_data,
    }
    return render(request, 'lecturer_attendance_summary.html', context)

@login_required
def download_attendance(request, course_id):
    if not request.user.is_lecturer:
        return redirect('home')

    course = get_object_or_404(Course, id=course_id, lecturer=request.user.lecturer)
    sessions = ClassSession.objects.filter(course=course).order_by('date')
    students = Student.objects.filter(
        attendance__class_session__course=course
    ).distinct()

    # Create CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{course.code}_attendance.csv"'

    writer = csv.writer(response)

    # Write header row
    header = ['Student Name', 'Matric Number', 'Total Sessions', 'Attended']
    header.extend([f"Session {i+1}" for i in range(sessions.count())])
    writer.writerow(header)

    # Write data rows
    for student in students:
        attended_sessions = Attendance.objects.filter(
            student=student,
            class_session__course=course
        ).values_list('class_session_id', flat=True)

        row = [
            student.user.get_full_name(),
            student.matric_number,
            sessions.count(),
            len(attended_sessions)
        ]

        for session in sessions:
            row.append('Present' if session.id in attended_sessions else 'Absent')

        writer.writerow(row)

    return response

# Student Views
@login_required
def student_dashboard(request):
    if not request.user.is_student:
        return redirect('home')

    student = request.user.student
    recent_attendances = Attendance.objects.filter(student=student).order_by('-timestamp')[:5]

    context = {
        'student': student,
        'recent_attendances': recent_attendances,
    }
    return render(request, 'student_dashboard.html', context)

@login_required
def scan_qr(request):
    if not request.user.is_student:
        return redirect('home')

    form = QRScanForm()
    return render(request, 'student_scan_qr.html', {'form': form})

# @login_required
# def mark_attendance(request, qr_code_id):
#     if not request.user.is_student:
#         return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=401)
#
#     try:
#         qr_code_uuid = uuid.UUID(qr_code_id)
#         class_session = ClassSession.objects.get(qr_code_id=qr_code_uuid, is_active=True)
#     except (ValueError, ClassSession.DoesNotExist):
#         return JsonResponse({'success': False, 'message': 'Invalid QR code or session expired'}, status=400)
#
#     student = request.user.student
#
#     # Check if student is already marked for this session
#     if Attendance.objects.filter(student=student, class_session=class_session).exists():
#         return JsonResponse({'success': False, 'message': 'Attendance already marked'}, status=400)
#
#     # Create attendance record
#     Attendance.objects.create(student=student, class_session=class_session)
#
#     return JsonResponse({'success': True, 'message': 'Attendance marked successfully'})

@login_required
@require_POST
def mark_attendance(request, qr_code_id):
    if not request.user.is_student:
        return JsonResponse({
            'success': False,
            'message': 'Only students can mark attendance'
        }, status=403)

    try:
        # Validate UUID format
        uuid.UUID(qr_code_id)

        class_session = get_object_or_404(
            ClassSession,
            qr_code_id=qr_code_id,
            is_active=True
        )

        student = request.user.student

        # Check if attendance already exists
        if Attendance.objects.filter(
                student=student,
                class_session=class_session
        ).exists():
            return JsonResponse({
                'success': False,
                'message': 'Attendance already marked for this session'
            })

        # Create attendance record
        Attendance.objects.create(
            student=student,
            class_session=class_session
        )

        return JsonResponse({
            'success': True,
            'message': 'Attendance marked successfully'
        })

    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid QR code'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
def student_attendance_summary(request):
    if not request.user.is_student:
        return redirect('home')

    student = request.user.student
    attendances = Attendance.objects.filter(student=student).order_by('-class_session__date')

    # Group by course and semester
    courses = {}
    for attendance in attendances:
        course = attendance.class_session.course
        semester = course.semester

        if semester not in courses:
            courses[semester] = {}

        if course.code not in courses[semester]:
            courses[semester][course.code] = {
                'title': course.title,
                'total_sessions': ClassSession.objects.filter(course=course).count(),
                'attended_sessions': 0,
                'sessions': []
            }

        courses[semester][course.code]['attended_sessions'] += 1
        courses[semester][course.code]['sessions'].append(attendance.class_session)

    context = {
        'student': student,
        'courses': courses,
    }
    return render(request, 'student_attendance_summary.html', context)