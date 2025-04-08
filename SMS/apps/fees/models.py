from django.db import models
from django.utils import timezone
from apps.students.models import Student  # Import Student model from students app

class FeePayment(models.Model):
    PAYMENT_STATUS = [
        ("Paid", "Paid"),
        ("Pending", "Pending"),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[
        ("Cash", "Cash"), 
        ("Online", "Online"), 
        ("Bank Transfer", "Bank Transfer")
    ])
    date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="Pending")
    fee_category = models.CharField(max_length=50, default="Regular")

    def __str__(self):
        return f"{self.student.fullname} - ₹{self.amount}"
