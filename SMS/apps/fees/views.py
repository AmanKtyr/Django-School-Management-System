from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import FeePayment
from apps.corecode.filters import ClassSectionFilterForm
from apps.students.models import Student

@login_required
def fee_list(request):
    # Initialize the filter form
    filter_form = ClassSectionFilterForm(request.GET)
    
    # Start with all students
    students = Student.objects.filter(current_status='active')
    payments = FeePayment.objects.all().order_by('-date')

    # Apply filters if form is valid
    if filter_form.is_valid():
        if filter_form.cleaned_data['class_name']:
            students = students.filter(current_class=filter_form.cleaned_data['class_name'])
            
        if filter_form.cleaned_data['section']:
            students = students.filter(section=filter_form.cleaned_data['section'])
        
    # Handle search
    search = request.GET.get('search')
    if search:
        students = students.filter(
            Q(fullname__icontains=search) |
            Q(registration_number__icontains=search)
        )

    context = {
        'filter_form': filter_form,
        'students': students,
        'recent_payments': payments.filter(student__in=students)[:10]  # Show only last 10 payments
    }
    return render(request, 'fees/fee_list.html', context)

@login_required
def submit_fee(request):
    # Your submit_fee view implementation
    pass
