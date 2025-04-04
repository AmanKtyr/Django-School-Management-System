from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student, FeePayment

def fee_management(request):
    students = Student.objects.all()
    payments = FeePayment.objects.all()

    if request.method == "POST":
        student_id = request.POST.get("student_id")
        amount = request.POST.get("amount")
        payment_method = request.POST.get("payment_method")

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            messages.error(request, "Invalid Student ID!")
            return redirect("fee_management")

        try:
            amount = float(amount)
            if amount <= 0:
                messages.error(request, "Amount should be greater than zero.")
                return redirect("fee_management")
        except ValueError:
            messages.error(request, "Invalid amount entered.")
            return redirect("fee_management")

        FeePayment.objects.create(student=student, amount=amount, payment_method=payment_method)
        messages.success(request, "Fee submitted successfully!")

        return redirect("fee_management")

    return render(request, "fees/fee_list.html", {"students": students, "payments": payments})



def submit_fee(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        amount = request.POST.get("amount")
        payment_method = request.POST.get("payment_method")

        try:
            student = Student.objects.get(id=student_id)
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount should be greater than zero.")
        except (Student.DoesNotExist, ValueError) as e:
            messages.error(request, f"Error: {e}")
            return redirect("submit_fee")

        FeePayment.objects.create(student=student, amount=amount, payment_method=payment_method)
        messages.success(request, "Fee submitted successfully!")
        return redirect("submit_fee")

    students = Student.objects.all()
    return render(request, "fees/submit_fee.html", {"students": students})
