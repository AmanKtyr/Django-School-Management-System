from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.fee_list, name='fee_list'),
    path('add-payment/<int:student_id>/', views.add_fee_payment, name='add_fee_payment'),
    path('history/<int:student_id>/', views.student_fee_history, name='student_fee_history'),
]
