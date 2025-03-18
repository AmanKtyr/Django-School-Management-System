# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from apps.students.models import Student
from .models import Attendance
from apps.corecode.models import StudentClass

def attendance_list(request):
    classes = StudentClass.objects.all()
    selected_class_id = request.GET.get('class_id')

    students = []
    if selected_class_id:
        students = Student.objects.filter(current_class_id=selected_class_id)

    present_leave = Attendance.objects.filter(status__in=["Present", "Leave"]).count()
    absent = Attendance.objects.filter(status="Absent").count()

    context = {
        "classes": classes,
        "students": students,
        "selected_class_id": selected_class_id,
        "present_leave": present_leave,
        "absent": absent,
    }
    return render(request, 'attendance/attendance_list.html', context)

def get_students(request, class_id):
    selected_class = get_object_or_404(StudentClass, id=class_id)
    students = Student.objects.filter(current_class=selected_class)

    students_data = [
        {
            "id": student.id,
            "fullname": student.fullname,
            "registration_number": student.registration_number,
            "section": student.section,
            "date": student.date.strftime('%Y-%m-%d')
        }
        for student in students
    ]
    return JsonResponse(students_data, safe=False)

def submit_attendance(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("attendance_"):
                student_id = key.split("_")[1]
                student = get_object_or_404(Student, id=student_id)
                Attendance.objects.create(student=student, status=value)
                
    return JsonResponse({"message": "Attendance saved successfully!"})
