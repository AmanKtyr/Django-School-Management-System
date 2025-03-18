from django.db import models
from apps.corecode.models import StudentClass  # Ensure corecode is installed correctly

class Student(models.Model):
    name = models.CharField(max_length=100)
    unique_id = models.CharField(max_length=50, unique=True)
    father_name = models.CharField(max_length=100)
    class_id = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name="students")  # ✅ Avoid conflict
    section = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')], default='Absent')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.status} ({self.date})"

class StudentAttendance(models.Model):
    registration_number = models.CharField(max_length=50, unique=True)
    fullname = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    parent_number = models.CharField(max_length=15)
    address = models.TextField()
    current_class = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    attendance_status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')], default='Absent')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.fullname} - {self.registration_number}"
