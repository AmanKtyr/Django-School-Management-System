from django.urls import path
from .views import fee_management  

urlpatterns = [
    path("fee_management/", fee_management, name="fee_management"),
]
