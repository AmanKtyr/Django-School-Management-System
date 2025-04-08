from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, F, DecimalField, Value
from django.db.models.functions import Coalesce
from .models import FeePayment
from apps.corecode.filters import ClassSectionFilterForm
from apps.students.models import Student
from apps.corecode.models import FeeSettings, FeeStructure

@login_required
def fee_list(request):
    filter_form = ClassSectionFilterForm(request.GET)
    
    # Start with all students
    students = Student.objects.filter(current_status='active')
    
    # Calculate actual paid fees
    students = students.annotate(
        paid_fee=Coalesce(
            Sum(
                'feepayment__amount',
                filter=Q(feepayment__status='Paid'),
                output_field=DecimalField()
            ),
            0,
            output_field=DecimalField()
        )
    )

    # Add total fees from fee settings
    for student in students:
        try:
            # First try to get fee settings with specific section
            fee_settings = FeeSettings.objects.get(
                class_name=student.current_class,
                section=student.section
            )
        except FeeSettings.DoesNotExist:
            try:
                # If not found, try to get fee settings without section
                fee_settings = FeeSettings.objects.get(
                    class_name=student.current_class,
                    section=''
                )
            except FeeSettings.DoesNotExist:
                fee_settings = None

        if fee_settings:
            student.total_fee = sum(fee.amount - fee.discount for fee in fee_settings.fees.all())
        else:
            student.total_fee = 0

        student.due_fee = student.total_fee - student.paid_fee

    if filter_form.is_valid():
        if filter_form.cleaned_data['class_name']:
            students = students.filter(current_class=filter_form.cleaned_data['class_name'])
            
        if filter_form.cleaned_data['section']:
            students = students.filter(section=filter_form.cleaned_data['section'])
    
    search = request.GET.get('search')
    if search:
        students = students.filter(
            Q(fullname__icontains=search) |
            Q(registration_number__icontains=search)
        )

    recent_payments = FeePayment.objects.select_related('student').order_by('-date')[:10]

    context = {
        'filter_form': filter_form,
        'students': students,
        'recent_payments': recent_payments
    }
    return render(request, 'fees/fee_list.html', context)

@login_required
def add_fee_payment(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            payment_method = request.POST.get('payment_method')
            fee_category = request.POST.get('fee_category')
            
            # Create new fee payment
            FeePayment.objects.create(
                student=student,
                amount=amount,
                payment_method=payment_method,
                fee_category=fee_category,
                status='Paid'
            )
            
            messages.success(request, 'Fee payment added successfully!')
            return redirect('fees:fee_list')
            
        except ValueError:
            messages.error(request, 'Please enter a valid amount')
    
    context = {
        'student': student,
        'payment_methods': FeePayment.PAYMENT_METHODS,
    }
    return render(request, 'fees/add_fee_payment.html', context)

@login_required
def student_fee_history(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    payments = FeePayment.objects.filter(student=student).order_by('-date')
    
    context = {
        'student': student,
        'payments': payments
    }
    return render(request, 'fees/student_fee_history.html', context)
