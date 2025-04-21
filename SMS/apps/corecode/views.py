from django.contrib import messages
from django.contrib.auth import logout, get_user_model
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404, HttpResponse
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from datetime import datetime
from apps.students.models import Student
from apps.fees.models import PendingFee

User = get_user_model()

from .filters import ClassSectionFilterForm

from .forms import (
    AcademicSessionForm,
    AcademicTermForm,
    CurrentSessionForm,
    SiteConfigForm,
    StudentClassForm,
    SubjectForm,
    SiteConfigFormSet,
    CollegeProfileForm
)
from .models import (
    AcademicSession,
    AcademicTerm,
    SiteConfig,
    StudentClass,
    Subject,
    CollegeProfile,
    FeeSettings,
    FeeStructure,
    ClassSubject,
    ClassTeacher
)


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get student data
        from apps.students.models import Student
        total_students = Student.objects.filter(current_status='active').count()

        # Get staff data
        from apps.staffs.models import Staff
        total_teachers = Staff.objects.filter(current_status='active').count()

        # Get non-teaching staff data
        from apps.NonTeachingStaffs.models import NonTeachingStaff
        total_non_teaching = NonTeachingStaff.objects.filter(current_status='active').count()

        # Get fee data
        from apps.fees.models import FeePayment, PendingFee
        from django.db.models import Sum
        from django.utils import timezone
        import datetime

        # Calculate fees collected this month
        current_month = timezone.now().month
        current_year = timezone.now().year
        fees_collected_month = FeePayment.objects.filter(
            date__month=current_month,
            date__year=current_year,
            status='Paid'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Calculate total pending fees
        total_pending = PendingFee.objects.filter(paid=False).aggregate(
            total=Sum('amount'))['total'] or 0

        # Get recent payments
        recent_payments = FeePayment.objects.select_related('student').order_by('-date')[:5]

        # Get recent students
        recent_students = Student.objects.order_by('-date_of_admission')[:5]

        # Get monthly fee collection data for chart
        months = []
        fee_data = []

        # Get data for the last 6 months
        for i in range(5, -1, -1):
            # Calculate the month and year
            month_date = timezone.now() - datetime.timedelta(days=30*i)
            month_name = month_date.strftime('%b')
            months.append(month_name)

            # Get fee collection for this month
            month_fees = FeePayment.objects.filter(
                date__month=month_date.month,
                date__year=month_date.year,
                status='Paid'
            ).aggregate(total=Sum('amount'))['total'] or 0

            # Convert Decimal to float for JSON serialization
            fee_data.append(float(month_fees))

        # Get attendance data if available
        try:
            from apps.attendance.models import Attendance
            from django.db.models import Count, Case, When, IntegerField

            # Get attendance data for the last 6 months
            attendance_months = []
            attendance_data = []

            for i in range(5, -1, -1):
                month_date = timezone.now() - datetime.timedelta(days=30*i)
                attendance_months.append(month_date.strftime('%b'))

                # Calculate attendance percentage for this month
                month_attendance = Attendance.objects.filter(
                    date__month=month_date.month,
                    date__year=month_date.year
                ).aggregate(
                    present_count=Count(Case(
                        When(status='Present', then=1),
                        output_field=IntegerField()
                    )),
                    total_count=Count('id')
                )

                if month_attendance['total_count'] > 0:
                    attendance_percentage = (month_attendance['present_count'] / month_attendance['total_count']) * 100
                else:
                    attendance_percentage = 0

                attendance_data.append(round(attendance_percentage, 1))
        except:
            # If attendance app is not available or there's an error
            attendance_months = months
            attendance_data = [90, 85, 88, 92, 95, 89]  # Default data

        # Get class distribution data
        class_labels = []
        class_data = []

        # Get all classes
        classes = StudentClass.objects.all()

        # For each class, count the number of students
        for student_class in classes:
            class_labels.append(str(student_class.name))
            class_count = Student.objects.filter(
                current_class=student_class,
                current_status='active'
            ).count()
            class_data.append(int(class_count))

        # If there are more than 5 classes, combine the rest into 'Others'
        if len(class_labels) > 5:
            others_count = sum(class_data[5:])
            class_labels = class_labels[:5]
            class_data = class_data[:5]
            class_labels.append('Others')
            class_data.append(others_count)

        context.update({
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_non_teaching': total_non_teaching,
            'fees_collected_month': fees_collected_month,
            'total_pending': total_pending,
            'recent_payments': recent_payments,
            'recent_students': recent_students,
            'months': months,
            'fee_data': fee_data,
            'attendance_months': attendance_months,
            'attendance_data': attendance_data,
            'class_labels': class_labels,
            'class_data': class_data,
        })

        return context




def site_config_view(request):
    profile = CollegeProfile.objects.first()
    if request.method == 'POST':
        form = CollegeProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('college_profile')
    else:
        form = CollegeProfileForm(instance=profile)
    return render(request, 'corecode/siteconfig.html', {'form': form, 'title': 'Site Configuration'})


class SessionListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = AcademicSession
    template_name = "corecode/session_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AcademicSessionForm()
        return context


class SessionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("sessions")
    success_message = "New session successfully added"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new session"
        return context


# SessionUpdateView removed - now using AJAX update


class SessionDeleteView(LoginRequiredMixin, DeleteView):
    model = AcademicSession
    success_url = reverse_lazy("sessions")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The session {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.current == True:
            messages.warning(request, "Cannot delete session as it is set to current")
            return redirect("sessions")
        messages.success(self.request, self.success_message.format(obj.name))
        return super(SessionDeleteView, self).delete(request, *args, **kwargs)


class TermListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = AcademicTerm
    template_name = "corecode/term_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AcademicTermForm()
        return context


class TermCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("terms")
    success_message = "New term successfully added"


# TermUpdateView removed - now using AJAX update


class TermDeleteView(LoginRequiredMixin, DeleteView):
    model = AcademicTerm
    success_url = reverse_lazy("terms")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The term {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.current == True:
            messages.warning(request, "Cannot delete term as it is set to current")
            return redirect("terms")
        messages.success(self.request, self.success_message.format(obj.name))
        return super(TermDeleteView, self).delete(request, *args, **kwargs)


class ClassListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = StudentClass
    template_name = "corecode/class_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = StudentClassForm()
        return context


class ClassCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = StudentClass
    form_class = StudentClassForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("classes")
    success_message = "New class successfully added"


# ClassUpdateView removed - now using AJAX update


class ClassDeleteView(LoginRequiredMixin, DeleteView):
    model = StudentClass
    success_url = reverse_lazy("classes")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The class {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        print(obj.name)
        messages.success(self.request, self.success_message.format(obj.name))
        return super(ClassDeleteView, self).delete(request, *args, **kwargs)


class SubjectListView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    model = Subject
    template_name = "corecode/subject_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SubjectForm()
        return context


class SubjectCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("subjects")
    success_message = "New subject successfully added"


class SubjectUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Subject
    fields = ["name"]
    success_url = reverse_lazy("subjects")
    success_message = "Subject successfully updated."
    template_name = "corecode/mgt_form.html"


class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Subject
    success_url = reverse_lazy("subjects")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The subject {} has been deleted with all its attached content"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message.format(obj.name))
        return super(SubjectDeleteView, self).delete(request, *args, **kwargs)


class CurrentSessionAndTermView(LoginRequiredMixin, View):
    """Current SEssion and Term"""

    form_class = CurrentSessionForm
    template_name = "corecode/current_session.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            initial={
                "current_session": AcademicSession.objects.get(current=True),
                "current_term": AcademicTerm.objects.get(current=True),
            }
        )
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_Class(request.POST)
        if form.is_valid():
            session = form.cleaned_data["current_session"]
            term = form.cleaned_data["current_term"]
            AcademicSession.objects.filter(name=session).update(current=True)
            AcademicSession.objects.exclude(name=session).update(current=False)
            AcademicTerm.objects.filter(name=term).update(current=True)

        return render(request, self.template_name, {"form": form})


def college_profile_view(request):
    profile = get_object_or_404(CollegeProfile)
    return render(request, 'corecode/college_profile.html', {'profile': profile})


@login_required
def custom_logout_view(request):
    """Custom logout view that shows a goodbye page"""
    logout(request)
    return render(request, 'registration/logout.html')





@login_required
def general_settings(request):
    """General Settings view"""
    profile = get_object_or_404(CollegeProfile)
    if request.method == 'POST':
        form = CollegeProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "General settings updated successfully.")
            return redirect('general_settings')
    else:
        form = CollegeProfileForm(instance=profile)

    context = {
        'active_tab': 'general',
        'form': form
    }
    return render(request, 'corecode/general_settings.html', context)


@login_required
def academic_settings(request):
    """Academic Settings view"""
    if request.method == 'POST':
        form = CurrentSessionForm(request.POST)
        if form.is_valid():
            session = form.cleaned_data["current_session"]
            term = form.cleaned_data["current_term"]
            AcademicSession.objects.filter(name=session).update(current=True)
            AcademicSession.objects.exclude(name=session).update(current=False)
            AcademicTerm.objects.filter(name=term).update(current=True)
            AcademicTerm.objects.exclude(name=term).update(current=False)
            messages.success(request, "Current session and term updated successfully.")
            return redirect('academic_settings')
    else:
        form = CurrentSessionForm()

    sessions = AcademicSession.objects.all().order_by('-name')
    terms = AcademicTerm.objects.all()

    context = {
        'active_tab': 'academic',
        'form': form,
        'sessions': sessions,
        'terms': terms
    }
    return render(request, 'corecode/academic_settings.html', context)


@login_required
def database_management(request):
    """Database Management view"""
    context = {
        'active_tab': 'database',
        'db_size': '12.4 MB',
        'last_optimized': '2023-04-10 09:15 AM',
        'total_tables': 32,
        'total_records': 5842
    }
    return render(request, 'corecode/database_management.html', context)


@login_required
def backup_restore(request):
    """Backup & Restore view"""
    context = {
        'active_tab': 'backup',
        'current_date': datetime.now().strftime('%Y_%m_%d')
    }
    return render(request, 'corecode/backup_restore.html', context)


@login_required
def user_permissions(request):
    """User Permissions view"""
    context = {
        'active_tab': 'permissions',
        'users': User.objects.all().order_by('username')
    }
    return render(request, 'corecode/user_permissions.html', context)


@login_required
def security_logs(request):
    """Security & Logs view"""
    context = {
        'active_tab': 'security'
    }
    return render(request, 'corecode/security_logs.html', context)


@login_required
def system_settings_dashboard(request):
    """System Settings Dashboard"""
    context = {
        'active_tab': 'dashboard',
        'system_version': '2.5.1',
        'last_updated': '2023-04-10',
        'uptime': '7 days, 14 hours',
        'last_backup': '2023-04-15 08:30 AM',
        'storage_usage': 45
    }
    return render(request, 'corecode/system_settings_dashboard.html', context)


@login_required
def general_settings(request):
    """General Settings Page"""
    profile = CollegeProfile.objects.first()
    if request.method == 'POST':
        form = CollegeProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "General settings updated successfully.")
            return redirect('general_settings')
    else:
        form = CollegeProfileForm(instance=profile)

    context = {
        'active_tab': 'general',
        'form': form
    }
    return render(request, 'corecode/general_settings.html', context)


@login_required
def academic_settings(request):
    """Academic Settings Page"""
    if request.method == 'POST':
        form = CurrentSessionForm(request.POST)
        if form.is_valid():
            session = form.cleaned_data["current_session"]
            term = form.cleaned_data["current_term"]
            AcademicSession.objects.filter(name=session).update(current=True)
            AcademicSession.objects.exclude(name=session).update(current=False)
            AcademicTerm.objects.filter(name=term).update(current=True)
            AcademicTerm.objects.exclude(name=term).update(current=False)
            messages.success(request, "Current session and term updated successfully.")
            return redirect('academic_settings')
    else:
        form = CurrentSessionForm()

    sessions = AcademicSession.objects.all().order_by('-name')
    terms = AcademicTerm.objects.all()

    context = {
        'active_tab': 'academic',
        'form': form,
        'sessions': sessions,
        'terms': terms
    }
    return render(request, 'corecode/academic_settings.html', context)


@login_required
def database_management(request):
    """Database Management Page"""
    context = {
        'active_tab': 'database',
        'db_size': '12.4 MB',
        'last_optimized': '2023-04-10 09:15 AM',
        'total_tables': 32,
        'total_records': 5842
    }
    return render(request, 'corecode/database_management.html', context)


@login_required
def backup_restore(request):
    """Backup & Restore Page"""
    context = {
        'active_tab': 'backup',
        'current_date': datetime.now().strftime('%Y_%m_%d')
    }
    return render(request, 'corecode/backup_restore.html', context)


@login_required
def user_permissions(request):
    """User Permissions Page"""
    User = get_user_model()
    users = User.objects.all().order_by('username')
    context = {
        'active_tab': 'permissions',
        'users': users
    }
    return render(request, 'corecode/user_permissions.html', context)


@login_required
def security_logs(request):
    """Security & Logs Page"""
    context = {
        'active_tab': 'security'
    }
    return render(request, 'corecode/security_logs.html', context)


def site_config(request):
    try:
        profile = CollegeProfile.objects.first()
    except CollegeProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = CollegeProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "College profile updated successfully.")
            return redirect('college-profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CollegeProfileForm(instance=profile)

    return render(request, 'corecode/siteconfig.html', {'form': form, 'title': 'Site Configuration'})


def fee_settings(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        section = request.POST.get('section', '')  # Optional section
        frequency = request.POST.get('frequency')

        if class_id:
            # Create or update fee settings
            fee_settings, created = FeeSettings.objects.get_or_create(
                class_name_id=class_id,
                section=section
            )

            fee_settings.frequency = frequency
            fee_settings.save()

            # Clear existing fees
            fee_settings.fees.all().delete()

            # Add new fees
            fee_types = request.POST.getlist('fee_type[]')
            amounts = request.POST.getlist('amount[]')
            # Get the single due date from the form
            due_date = request.POST.get('due_date')

            # If due date is not provided, use today's date
            if not due_date:
                from django.utils import timezone
                due_date = timezone.now().date()

            late_fees = request.POST.getlist('late_fee[]')
            discounts = request.POST.getlist('discount[]')

            # Create fee structures
            fee_structures = []
            for i in range(len(fee_types)):
                # Handle empty values for decimal fields
                amount = amounts[i] if amounts[i] else 0
                late_fee = late_fees[i] if i < len(late_fees) and late_fees[i] else 0
                discount = discounts[i] if i < len(discounts) and discounts[i] else 0

                fee_structure = FeeStructure.objects.create(
                    fee_settings=fee_settings,
                    fee_type=fee_types[i],
                    amount=amount,
                    due_date=due_date,  # Use the single due date for all fees
                    late_fee=late_fee,
                    discount=discount
                )
                fee_structures.append(fee_structure)

            # Create pending fees for all students in this class
            students = Student.objects.filter(current_class_id=class_id, section=section, current_status='active')

            # If no students found with specific section, try without section filter
            if not students.exists() and section:
                students = Student.objects.filter(current_class_id=class_id, current_status='active')

            # Create pending fees for each student
            for student in students:
                # Delete any existing pending fees for this student that match the fee types
                PendingFee.objects.filter(
                    student=student,
                    fee_type__in=[fs.fee_type for fs in fee_structures],
                    paid=False
                ).delete()

                # Create new pending fees
                for fs in fee_structures:
                    # Ensure all decimal values are valid
                    amount = fs.amount if fs.amount else 0
                    late_fee = fs.late_fee if fs.late_fee else 0
                    discount = fs.discount if fs.discount else 0

                    PendingFee.objects.create(
                        student=student,
                        fee_type=fs.fee_type,
                        amount=amount,
                        due_date=fs.due_date,  # This now uses the single due date
                        late_fee=late_fee,
                        discount=discount
                    )

            messages.success(request, f'Fee settings saved successfully! Pending fees created for {students.count()} students.')
            return redirect('fee_settings')

    # Get selected class and section from GET parameters
    selected_class_id = request.GET.get('class_name')
    selected_section = request.GET.get('section', '')

    filter_form = ClassSectionFilterForm(request.GET)

    context = {
        'filter_form': filter_form,
        'selected_class': None,
        'selected_section': selected_section,
        'existing_fees': None
    }

    if selected_class_id:
        try:
            selected_class = StudentClass.objects.get(id=selected_class_id)
            context['selected_class'] = selected_class

            # Try to get existing fee settings
            try:
                fee_settings = FeeSettings.objects.get(
                    class_name=selected_class,
                    section=selected_section
                )
                context['existing_fees'] = fee_settings.fees.all()
                context['fee_settings'] = fee_settings
            except FeeSettings.DoesNotExist:
                # If no settings exist with section, try without section
                if selected_section:
                    try:
                        fee_settings = FeeSettings.objects.get(
                            class_name=selected_class,
                            section=''
                        )
                        context['existing_fees'] = fee_settings.fees.all()
                        context['fee_settings'] = fee_settings
                    except FeeSettings.DoesNotExist:
                        pass
        except StudentClass.DoesNotExist:
            messages.error(request, 'Invalid class selected')
            return redirect('fee_settings')

    return render(request, 'corecode/fee_settings.html', context)

def get_fee_settings(request, class_id, section):
    try:
        fee_settings = FeeSettings.objects.get(class_name_id=class_id, section=section)
        fees = fee_settings.fees.all().values(
            'fee_type', 'amount', 'due_date', 'late_fee', 'discount'
        )
        return JsonResponse({
            'settings': {
                'frequency': fee_settings.frequency,
                'fees': list(fees)
            }
        })
    except FeeSettings.DoesNotExist:
        return JsonResponse({'settings': None})


def get_sections_by_class(request, class_id):
    """API endpoint to get sections for a specific class"""
    from apps.students.models import Student

    # Get all unique sections for students in this class
    sections = Student.objects.filter(
        current_class_id=class_id,
        current_status='active'
    ).values_list('section', flat=True).distinct()

    # Format the sections for the response
    section_data = [{'id': section, 'name': section} for section in sections if section]

    # Sort sections alphabetically
    section_data = sorted(section_data, key=lambda x: x['name'])

    return JsonResponse({'sections': section_data})


@login_required
def get_class_data(request, class_id):
    """API endpoint to get data for a specific class"""
    from apps.students.models import Student
    from django.db.models import Count

    try:
        # Get the class
        student_class = StudentClass.objects.get(id=class_id)

        # Get student count
        student_count = Student.objects.filter(
            current_class=student_class,
            current_status='active'
        ).count()

        # Get sections
        sections = Student.objects.filter(
            current_class=student_class,
            current_status='active'
        ).values_list('section', flat=True).distinct()

        # Format sections
        sections_list = [section for section in sections if section]

        # Get subjects for this class (if available)
        try:
            from apps.exams.models import ExamSchedule
            subjects = ExamSchedule.objects.filter(
                student_class=student_class
            ).values_list('subject__name', flat=True).distinct()
            subjects_list = list(subjects)
        except:
            subjects_list = []

        return JsonResponse({
            'student_count': student_count,
            'sections': sections_list,
            'subjects': subjects_list
        })
    except StudentClass.DoesNotExist:
        return JsonResponse({'error': 'Class not found'}, status=404)


@login_required
def get_subject_data(request, subject_id):
    """API endpoint to get data for a specific subject"""
    try:
        # Get the subject
        subject = Subject.objects.get(id=subject_id)

        # Get classes where this subject is taught from ClassSubject model
        class_subjects = ClassSubject.objects.filter(subject=subject, is_active=True)
        classes_list = []
        for cs in class_subjects:
            section_str = f" ({cs.section})" if cs.section else ""
            classes_list.append(f"{cs.student_class.name}{section_str}")

        # Use the department field from the Subject model if available
        department = subject.department or determine_department(subject.name)

        # Get additional data
        try:
            from apps.exams.models import ExamSchedule
            exam_count = ExamSchedule.objects.filter(subject=subject).count()
        except:
            exam_count = 0

        return JsonResponse({
            'name': subject.name,
            'class_count': len(classes_list),
            'classes': classes_list,
            'department': department,
            'code': subject.code,
            'description': subject.description,
            'exam_count': exam_count
        })
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found'}, status=404)


@login_required
def update_subject_ajax(request, subject_id):
    """API endpoint to update a subject via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        subject = Subject.objects.get(id=subject_id)

        # Update subject fields
        subject.name = request.POST.get('name')
        subject.code = request.POST.get('code', '')
        subject.department = request.POST.get('department', '')
        subject.description = request.POST.get('description', '')
        subject.save()

        return JsonResponse({
            'success': True,
            'message': 'Subject updated successfully',
            'subject': {
                'id': subject.id,
                'name': subject.name,
                'code': subject.code,
                'department': subject.department,
                'description': subject.description
            }
        })
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_subject_exams(request, subject_id):
    """API endpoint to get exams for a specific subject"""
    try:
        # Get the subject
        subject = Subject.objects.get(id=subject_id)

        # Get exams for this subject (if available)
        try:
            from apps.exams.models import ExamSchedule
            exam_schedules = ExamSchedule.objects.filter(
                subject=subject
            ).select_related('exam', 'student_class').order_by('-date')[:5]  # Get the 5 most recent exams

            exams_list = [{
                'name': schedule.exam.name,
                'class': schedule.student_class.name,
                'date': schedule.date.strftime('%b %d, %Y') if schedule.date else 'N/A'
            } for schedule in exam_schedules]
        except Exception as e:
            print(f"Error getting exams: {e}")
            exams_list = []

        return JsonResponse({
            'exams': exams_list
        })
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found'}, status=404)


def determine_department(subject_name):
    """Helper function to determine department based on subject name"""
    subject_name = subject_name.lower()

    # Science subjects
    if any(keyword in subject_name for keyword in ['physics', 'chemistry', 'biology', 'science']):
        return 'Science'

    # Mathematics subjects
    elif any(keyword in subject_name for keyword in ['math', 'algebra', 'geometry', 'calculus']):
        return 'Mathematics'

    # Language subjects
    elif any(keyword in subject_name for keyword in ['english', 'hindi', 'sanskrit', 'language', 'literature']):
        return 'Languages'

    # Social Science subjects
    elif any(keyword in subject_name for keyword in ['history', 'geography', 'civics', 'social', 'economics', 'political']):
        return 'Social Sciences'

    # Commerce subjects
    elif any(keyword in subject_name for keyword in ['commerce', 'business', 'accounting', 'finance']):
        return 'Commerce'

    # Arts subjects
    elif any(keyword in subject_name for keyword in ['art', 'music', 'dance', 'drama', 'painting']):
        return 'Arts'

    # Computer subjects
    elif any(keyword in subject_name for keyword in ['computer', 'programming', 'it', 'information']):
        return 'Computer Science'

    # Default department
    else:
        return 'General'


# This function is now replaced by the more detailed version below


@login_required
def get_class_subjects(request, class_id):
    """API endpoint to get subjects for a specific class"""
    try:
        student_class = StudentClass.objects.get(id=class_id)
        class_subjects = ClassSubject.objects.filter(
            student_class=student_class,
            is_active=True
        ).select_related('subject')

        subjects_list = [{
            'id': cs.subject.id,
            'name': cs.subject.name,
            'section': cs.section or '',
            'class_subject_id': cs.id,
            'teacher': cs.teacher.fullname if cs.teacher else 'Not Assigned'
        } for cs in class_subjects]

        return JsonResponse({
            'class_name': student_class.name,
            'subjects': subjects_list
        })
    except StudentClass.DoesNotExist:
        return JsonResponse({'error': 'Class not found'}, status=404)


@login_required
def assign_subject_to_class(request):
    """API endpoint to assign a subject to a class"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        # Try to parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to get data from POST
            data = request.POST

        subject_id = data.get('subject_id')
        class_id = data.get('class_id')
        section = data.get('section', '')
        teacher_id = data.get('teacher_id')

        # Log the received data for debugging
        print(f"Received data: subject_id={subject_id}, class_id={class_id}, section={section}, teacher_id={teacher_id}")

        if not subject_id or not class_id:
            return JsonResponse({'error': 'Subject ID and Class ID are required'}, status=400)

        subject = Subject.objects.get(id=subject_id)
        student_class = StudentClass.objects.get(id=class_id)

        # Check if teacher exists if provided
        teacher = None
        if teacher_id:
            from apps.staffs.models import Staff
            teacher = Staff.objects.get(id=teacher_id)

        # Check if assignment already exists
        class_subject, created = ClassSubject.objects.get_or_create(
            subject=subject,
            student_class=student_class,
            section=section,
            defaults={
                'teacher': teacher,
                'is_active': True
            }
        )

        if not created:
            # Update existing assignment
            class_subject.teacher = teacher
            class_subject.is_active = True
            class_subject.save()
            message = 'Subject assignment updated successfully'
        else:
            message = 'Subject assigned to class successfully'

        return JsonResponse({
            'success': True,
            'message': message,
            'class_subject_id': class_subject.id
        })
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found'}, status=404)
    except StudentClass.DoesNotExist:
        return JsonResponse({'error': 'Class not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def remove_subject_from_class(request, class_subject_id):
    """API endpoint to remove a subject from a class"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        class_subject = ClassSubject.objects.get(id=class_subject_id)

        # Instead of deleting, mark as inactive
        class_subject.is_active = False
        class_subject.save()

        return JsonResponse({
            'success': True,
            'message': 'Subject removed from class successfully'
        })
    except ClassSubject.DoesNotExist:
        return JsonResponse({'error': 'Class-Subject assignment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_all_classes(request):
    """API endpoint to get all classes"""
    try:
        classes = StudentClass.objects.all().order_by('name')
        classes_list = [{
            'id': cls.id,
            'name': cls.name
        } for cls in classes]

        return JsonResponse(classes_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_all_teachers(request):
    """API endpoint to get all teachers"""
    try:
        from apps.staffs.models import Staff
        teachers = Staff.objects.filter(current_status='active').order_by('surname')
        teachers_list = [{
            'id': teacher.id,
            'name': teacher.fullname
        } for teacher in teachers]

        return JsonResponse(teachers_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_all_assignments(request):
    """API endpoint to get all subject-class assignments"""
    try:
        class_subjects = ClassSubject.objects.filter(is_active=True).select_related(
            'subject', 'student_class', 'teacher'
        )

        assignments_list = []
        for cs in class_subjects:
            assignments_list.append({
                'id': cs.id,
                'subject_id': cs.subject.id,
                'subject_name': cs.subject.name,
                'class_id': cs.student_class.id,
                'class_name': cs.student_class.name,
                'section': cs.section or '',
                'teacher_id': cs.teacher.id if cs.teacher else None,
                'teacher_name': cs.teacher.fullname if cs.teacher else None
            })

        return JsonResponse(assignments_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def fee_settings_list(request):
    fee_settings_list = FeeSettings.objects.all().order_by('class_name', 'section')

    # Calculate statistics
    total_classes = fee_settings_list.count()
    total_fees = sum(setting.get_total_fees() for setting in fee_settings_list)
    active_settings = fee_settings_list.count()  # Assuming all settings are active

    context = {
        'fee_settings_list': fee_settings_list,
        'total_classes': total_classes,
        'total_fees': total_fees,
        'active_settings': active_settings,
    }

    return render(request, 'corecode/fee_settings_list.html', context)


@login_required
def update_class_ajax(request, class_id):
    """API endpoint to update a class via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        student_class = StudentClass.objects.get(id=class_id)

        # Get the new name from POST data
        name = request.POST.get('name')

        if not name:
            return JsonResponse({'error': 'Class name is required'}, status=400)

        # Check if name already exists for another class
        if StudentClass.objects.filter(name=name).exclude(id=class_id).exists():
            return JsonResponse({'error': 'A class with this name already exists'}, status=400)

        # Update the class name
        student_class.name = name
        student_class.save()

        return JsonResponse({
            'success': True,
            'message': 'Class updated successfully',
            'class': {
                'id': student_class.id,
                'name': student_class.name
            }
        })
    except StudentClass.DoesNotExist:
        return JsonResponse({'error': 'Class not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def update_session_ajax(request, session_id):
    """API endpoint to update an academic session via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        session = AcademicSession.objects.get(id=session_id)

        # Get the data from POST
        name = request.POST.get('name')
        current = request.POST.get('current') == 'true'

        if not name:
            return JsonResponse({'error': 'Session name is required'}, status=400)

        # Check if name already exists for another session
        if AcademicSession.objects.filter(name=name).exclude(id=session_id).exists():
            return JsonResponse({'error': 'A session with this name already exists'}, status=400)

        # Update the session
        session.name = name

        # Handle current status
        if current:
            # Set all other sessions as not current
            AcademicSession.objects.all().update(current=False)
            session.current = True
        else:
            session.current = False

        session.save()

        return JsonResponse({
            'success': True,
            'message': 'Session updated successfully',
            'session': {
                'id': session.id,
                'name': session.name,
                'current': session.current
            }
        })
    except AcademicSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def update_term_ajax(request, term_id):
    """API endpoint to update an academic term via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        term = AcademicTerm.objects.get(id=term_id)

        # Get the data from POST
        name = request.POST.get('name')
        current = request.POST.get('current') == 'true'

        if not name:
            return JsonResponse({'error': 'Term name is required'}, status=400)

        # Check if name already exists for another term
        if AcademicTerm.objects.filter(name=name).exclude(id=term_id).exists():
            return JsonResponse({'error': 'A term with this name already exists'}, status=400)

        # Update the term
        term.name = name

        # Handle current status
        if current:
            # Set all other terms as not current
            AcademicTerm.objects.all().update(current=False)
            term.current = True
        else:
            term.current = False

        term.save()

        return JsonResponse({
            'success': True,
            'message': 'Term updated successfully',
            'term': {
                'id': term.id,
                'name': term.name,
                'current': term.current
            }
        })
    except AcademicTerm.DoesNotExist:
        return JsonResponse({'error': 'Term not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_class_teachers(request):
    """API endpoint to get all class teachers"""
    try:
        class_teachers = ClassTeacher.objects.filter(is_active=True).select_related(
            'student_class', 'teacher'
        )

        teachers_list = [{
            'id': ct.id,
            'class_id': ct.student_class.id,
            'class_name': ct.student_class.name,
            'section': ct.section or '',
            'teacher_id': ct.teacher.id,
            'teacher_name': ct.teacher.fullname
        } for ct in class_teachers]

        return JsonResponse(teachers_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_class_teacher(request, class_id, section=None):
    """API endpoint to get class teacher for a specific class and section"""
    try:
        # Get the class
        student_class = StudentClass.objects.get(id=class_id)

        # Get class teacher
        query = {
            'student_class': student_class,
            'is_active': True
        }

        if section:
            query['section'] = section

        class_teacher = ClassTeacher.objects.filter(**query).select_related('teacher').first()

        if class_teacher:
            teacher_data = {
                'id': class_teacher.id,
                'teacher_id': class_teacher.teacher.id,
                'teacher_name': class_teacher.teacher.fullname,
                'section': class_teacher.section or ''
            }
        else:
            teacher_data = None

        return JsonResponse({
            'class_name': student_class.name,
            'class_teacher': teacher_data
        })
    except StudentClass.DoesNotExist:
        return JsonResponse({'error': 'Class not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def assign_class_teacher(request):
    """API endpoint to assign a teacher to a class"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        # Parse JSON data
        data = json.loads(request.body)
        class_id = data.get('class_id')
        section = data.get('section', '')
        teacher_id = data.get('teacher_id')

        if not class_id:
            return JsonResponse({'error': 'Class ID is required'}, status=400)

        if not teacher_id:
            return JsonResponse({'error': 'Teacher ID is required'}, status=400)

        # Get the class and teacher
        student_class = StudentClass.objects.get(id=class_id)
        from apps.staffs.models import Staff
        teacher = Staff.objects.get(id=teacher_id)

        # Check if assignment already exists
        class_teacher, created = ClassTeacher.objects.get_or_create(
            student_class=student_class,
            section=section,
            defaults={
                'teacher': teacher,
                'is_active': True
            }
        )

        if not created:
            # Update existing assignment
            class_teacher.teacher = teacher
            class_teacher.is_active = True
            class_teacher.save()
            message = 'Class teacher updated successfully'
        else:
            message = 'Class teacher assigned successfully'

        return JsonResponse({
            'success': True,
            'message': message,
            'class_teacher_id': class_teacher.id
        })
    except StudentClass.DoesNotExist:
        return JsonResponse({'error': 'Class not found'}, status=404)
    except Staff.DoesNotExist:
        return JsonResponse({'error': 'Teacher not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def remove_class_teacher(request, class_teacher_id):
    """API endpoint to remove a class teacher"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        class_teacher = ClassTeacher.objects.get(id=class_teacher_id)

        # Instead of deleting, mark as inactive
        class_teacher.is_active = False
        class_teacher.save()

        return JsonResponse({
            'success': True,
            'message': 'Class teacher removed successfully'
        })
    except ClassTeacher.DoesNotExist:
        return JsonResponse({'error': 'Class teacher assignment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)