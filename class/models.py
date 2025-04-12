from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from django.conf import settings


# class User(AbstractUser):
#     is_lecturer = models.BooleanField(default=False)
#     is_student = models.BooleanField(default=False)
#
#     def __str__(self):
#         return self.username
#
#
# class Lecturer(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
#     lecturer_number = models.CharField(max_length=20, unique=True)
#     department = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.user.get_full_name() or self.user.username
#
#
# class Student(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
#     matric_number = models.CharField(max_length=20, unique=True)
#     department = models.CharField(max_length=100)
#
#     def __str__(self):
#         return f"{self.user.get_full_name()} - {self.matric_number}"


class CustomUserManager(BaseUserManager):
    def create_user(self, identifier, password=None, **extra_fields):
        if not identifier:
            raise ValueError('The identifier must be set')
        user = self.model(identifier=identifier, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, identifier, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(identifier, password, **extra_fields)

class User(AbstractUser):
    username = None
    identifier = models.CharField(max_length=20, unique=True)
    is_lecturer = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    USERNAME_FIELD = 'identifier'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.identifier

class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    lecturer_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.lecturer_number}"

    def save(self, *args, **kwargs):
        if not self.user:
            # Create user account first
            user = User.objects.create_user(
                identifier=self.lecturer_number,
                is_lecturer=True,
                first_name=self.first_name,
                last_name=self.last_name
            )
            self.user = user
        super().save(*args, **kwargs)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    matric_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.matric_number}"

    def save(self, *args, **kwargs):
        if not self.user:
            # Create user account first
            user = User.objects.create_user(
                identifier=self.matric_number,
                is_student=True,
                first_name=self.first_name,
                last_name=self.last_name
            )
            self.user = user
        super().save(*args, **kwargs)

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=100)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.code} - {self.title}"


class ClassSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    qr_code = models.ImageField(upload_to='qr_codes', blank=True)
    qr_code_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course} - {self.date}"

    def save(self, *args, **kwargs):
        if not self.qr_code:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            # Data to encode in QR code
            qr_data = f"{settings.SITE_URL}/attendance/mark-attendance/{self.qr_code_id}/"
            qr.add_data(qr_data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format="PNG")

            # Save QR code to model
            file_name = f"qr_code_{self.course.code}_{self.date}.png"
            self.qr_code.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'class_session')

    def __str__(self):
        return f"{self.student} attended {self.class_session}"