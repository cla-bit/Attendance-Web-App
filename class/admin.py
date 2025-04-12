from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Lecturer, Student, Course, ClassSession, Attendance

class CustomUserAdmin(UserAdmin):
    list_display = ('identifier', 'first_name', 'last_name', 'is_lecturer', 'is_student', 'is_staff')
    list_filter = ('is_lecturer', 'is_student', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('identifier', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_lecturer', 'is_student')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('identifier', 'password1', 'password2', 'is_lecturer', 'is_student'),
        }),
    )
    search_fields = ('identifier', 'first_name', 'last_name')
    ordering = ('identifier',)

class LecturerAdmin(admin.ModelAdmin):
    list_display = ('lecturer_number', 'first_name', 'last_name', 'department')
    search_fields = ('lecturer_number', 'first_name', 'last_name')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('matric_number', 'first_name', 'last_name', 'department')
    search_fields = ('matric_number', 'first_name', 'last_name')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Lecturer, LecturerAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Course)
admin.site.register(ClassSession)
admin.site.register(Attendance)
