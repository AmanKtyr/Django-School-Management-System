from django.urls import path
from .views import AttendanceListView, AttendanceDetailView, AttendanceUpdateView, attendance_list

app_name = 'attendance'  # ✅ Fix for NoReverseMatch error

urlpatterns = [
    path('', attendance_list, name='attendance_list'),  # ✅ Main Attendance Page
    path('list/', AttendanceListView.as_view(), name='attendance_list_view'),  # ✅ ListView
    path('<int:pk>/', AttendanceDetailView.as_view(), name='attendance_detail'),  # ✅ DetailView
    path('<int:pk>/update/', AttendanceUpdateView.as_view(), name='attendance_update'),  # ✅ UpdateView
    path('submit/', attendance_list, name='submit_attendance'),  # ✅ Corrected URL
]
