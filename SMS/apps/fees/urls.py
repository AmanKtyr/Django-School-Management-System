from django.urls import path
from .views import fee_management, submit_fee  

urlpatterns = [
    path("", fee_management, name="fee_list"),
    path("submit/", submit_fee, name="submit_fee"),
]
