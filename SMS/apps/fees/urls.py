from django.urls import path
from .views import fee_list, submit_fee  # Changed fee_management to fee_list

urlpatterns = [
    path("", fee_list, name="fee_list"),  # Changed fee_management to fee_list
    path("submit/", submit_fee, name="submit_fee"),
]
