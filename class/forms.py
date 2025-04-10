from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Lecturer, Student, Course, ClassSession


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    is_lecturer = forms.BooleanField(required=False)
    is_student = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_lecturer', 'is_student']

class LecturerProfileForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ['department']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['matric_number', 'department']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'title', 'semester']

class ClassSessionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.lecturer = kwargs.pop('lecturer', None)
        super().__init__(*args, **kwargs)

        if self.lecturer:
            self.fields['course'].queryset = Course.objects.filter(lecturer=self.lecturer)

    class Meta:
        model = ClassSession
        fields = ['course', 'date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class QRScanForm(forms.Form):
    qr_code = forms.CharField(widget=forms.HiddenInput())