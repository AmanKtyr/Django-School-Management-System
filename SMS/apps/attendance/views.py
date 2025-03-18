from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView
from .models import StudentAttendance, Student, Attendance
from apps.corecode.models import StudentClass  # Ensure correct import

def attendance_list(request):
    selected_class_id = request.GET.get('class')
    classes = StudentClass.objects.all()
    students = Student.objects.filter(class_id=selected_class_id) if selected_class_id else Student.objects.none()

    if request.method == 'POST':
        for student in students:
            attendance_status = request.POST.get(f'attendance_{student.id}')
            Attendance.objects.create(student=student, status=attendance_status)
        return redirect('attendance:attendance_list')

    context = {
        'classes': classes,
        'students': students,
        'selected_class_id': selected_class_id,
        'class_name': StudentClass.objects.get(id=selected_class_id).name if selected_class_id else '',
        'class_teacher': StudentClass.objects.get(id=selected_class_id).teacher if selected_class_id else '',
        'total_students': students.count(),
        'present_leave': students.filter(attendance__status__in=['Present', 'Leave']).count(),
        'absent': students.filter(attendance__status='Absent').count(),
    }
    return render(request, 'attendance/attendance_list.html', context)

class AttendanceListView(LoginRequiredMixin, ListView):
    model = StudentAttendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'

class AttendanceDetailView(LoginRequiredMixin, DetailView):
    model = StudentAttendance
    template_name = "attendance/attendance_detail.html"

class AttendanceUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = StudentAttendance
    fields = ["registration_number", "fullname", "gender", "parent_number", "address", "current_class", "attendance_status"]
    success_message = "Attendance record successfully updated."
    template_name = 'attendance/attendance_update.html'
