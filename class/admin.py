from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Lecturer, Student, Course, ClassSession, Attendance

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_lecturer', 'is_student', 'is_staff')
    list_filter = ('is_lecturer', 'is_student', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_lecturer', 'is_student')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Lecturer)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(ClassSession)
admin.site.register(Attendance)
