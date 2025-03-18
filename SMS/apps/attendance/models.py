from django.db import models
from apps.corecode.models import StudentClass   
from apps.students.models import Student
from django.utils.timezone import now

class Attendance(models.Model):
    ATTENDANCE_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Leave', 'Leave'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance")
    status = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES, default='Absent')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.fullname} - {self.status} ({self.date})"

class StudentAttendance(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    ATTENDANCE_STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    registration_number = models.CharField(max_length=50, unique=True, verbose_name="Registration Number")
    fullname = models.CharField(max_length=100, verbose_name="Full Name")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Gender")
    parent_number = models.CharField(max_length=15, verbose_name="Parent's Contact Number")
    address = models.TextField(verbose_name="Address")
    current_class = models.CharField(max_length=50, verbose_name="Current Class")
    section = models.CharField(max_length=10, verbose_name="Section")
    attendance_status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS_CHOICES, default='Absent', verbose_name="Attendance Status")
    date = models.DateField(auto_now_add=True, verbose_name="Date")

    def __str__(self):
        return f"{self.fullname} ({self.registration_number})"