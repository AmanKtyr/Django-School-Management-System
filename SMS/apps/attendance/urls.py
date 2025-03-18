from django.urls import path
from .views import attendance_list, get_students, submit_attendance

urlpatterns = [
    path('attendance_list/', attendance_list, name='attendance_list'),
    path('get_students/<int:class_id>/', get_students, name='get_students'),
    path('submit_attendance/', submit_attendance, name='submit_attendance'),
]
