from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, F, DecimalField, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import FeePayment, PendingFee
from apps.corecode.filters import ClassSectionFilterForm
from apps.students.models import Student
from apps.corecode.models import FeeSettings, FeeStructure

@login_required
def fee_list(request):
    filter_form = ClassSectionFilterForm(request.GET)

    # Start with all students
    students = Student.objects.filter(current_status='active')

    # Apply filters first
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

    # Now calculate pending fees for the filtered students
    for student in students:
        # Get total from pending fees
        pending_fees = PendingFee.objects.filter(student=student, paid=False)
        student.total_pending = sum(fee.get_discounted_amount() for fee in pending_fees)

        # Get total from fee settings (for reference)
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

        # Use pending fees for due fee calculation
        student.due_fee = student.total_pending

    recent_payments = FeePayment.objects.select_related('student').order_by('-date')[:10]

    context = {
        'filter_form': filter_form,
        'students': students,
        'recent_payments': recent_payments,
        'today': timezone.now()
    }
    return render(request, 'fees/fee_list.html', context)

@login_required
def add_fee_payment(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Get pending fees for this student
    pending_fees = PendingFee.objects.filter(student=student, paid=False).order_by('due_date')
    total_pending = sum(fee.get_discounted_amount() for fee in pending_fees)

    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            payment_method = request.POST.get('payment_method')
            fee_category = request.POST.get('fee_category')
            fee_type = request.POST.get('fee_type')

            # Create new fee payment
            FeePayment.objects.create(
                student=student,
                amount=amount,
                payment_method=payment_method,
                fee_category=fee_category,
                status='Paid'
            )

            # Mark pending fees as paid
            if fee_type and fee_type != 'all':
                # If a specific fee type was selected, mark only that one as paid
                try:
                    pending_fee = PendingFee.objects.get(id=fee_type, student=student, paid=False)
                    pending_fee.paid = True
                    pending_fee.save()
                    messages.success(request, f'Payment for {pending_fee.fee_type} recorded successfully!')
                except PendingFee.DoesNotExist:
                    messages.warning(request, 'Selected fee not found or already paid.')
            else:
                # Mark pending fees as paid in order of due date until the amount is exhausted
                remaining_amount = amount
                fees_paid = []

                for fee in pending_fees:
                    fee_amount = fee.get_discounted_amount()
                    if remaining_amount >= fee_amount:
                        fee.paid = True
                        fee.save()
                        fees_paid.append(fee.fee_type)
                        remaining_amount -= fee_amount
                    else:
                        # If we can't pay the full fee, we don't mark it as paid
                        # but we could create a partial payment record in the future
                        break

                if fees_paid:
                    messages.success(request, f'Payment recorded successfully! Paid: {", ".join(fees_paid)}')
                else:
                    messages.info(request, 'Payment recorded, but no specific fees were fully covered.')

            return redirect('student-detail', pk=student.id)

        except ValueError:
            messages.error(request, 'Please enter a valid amount')

    context = {
        'student': student,
        'payment_methods': FeePayment.PAYMENT_METHODS,
        'pending_fees': pending_fees,
        'total_pending': total_pending
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


@login_required
def generate_receipt(request, payment_id):
    payment = get_object_or_404(FeePayment, id=payment_id)

    # For HTML view (preview)
    if request.GET.get('format') == 'html':
        context = {
            'payment': payment
        }
        return render(request, 'fees/receipt.html', context)

    # For PDF generation
    template = get_template('fees/receipt.html')
    context = {
        'payment': payment
    }
    html = template.render(context)

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    filename = f"Receipt_{payment.student.fullname}_{payment.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Return PDF response if successful
    if pisa_status.err:
        return HttpResponse('PDF generation error', status=500)

    return response
