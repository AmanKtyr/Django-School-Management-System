from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)

    class Meta:
        app_label = 'fees'  
    def __str__(self):
        return self.name

class FeePayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[("Cash", "Cash"), ("Online", "Online"), ("Bank Transfer", "Bank Transfer")])
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'fees'  

    def __str__(self):
        return f"{self.student.name} - ₹{self.amount}"