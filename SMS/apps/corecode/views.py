from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404, HttpResponse
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from apps.students.models import Student
from apps.fees.models import PendingFee

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
    FeeStructure
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


class SessionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    success_url = reverse_lazy("sessions")
    success_message = "Session successfully updated."
    template_name = "corecode/mgt_form.html"

    def form_valid(self, form):
        obj = self.object
        if obj.current == False:
            terms = (
                AcademicSession.objects.filter(current=True)
                .exclude(name=obj.name)
                .exists()
            )
            if not terms:
                messages.warning(self.request, "You must set a session to current.")
                return redirect("session-list")
        return super().form_valid(form)


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


class TermUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    success_url = reverse_lazy("terms")
    success_message = "Term successfully updated."
    template_name = "corecode/mgt_form.html"

    def form_valid(self, form):
        obj = self.object
        if obj.current == False:
            terms = (
                AcademicTerm.objects.filter(current=True)
                .exclude(name=obj.name)
                .exists()
            )
            if not terms:
                messages.warning(self.request, "You must set a term to current.")
                return redirect("term")
        return super().form_valid(form)


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


class ClassUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = StudentClass
    fields = ["name"]
    success_url = reverse_lazy("classes")
    success_message = "class successfully updated."
    template_name = "corecode/mgt_form.html"


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
                fee_structure = FeeStructure.objects.create(
                    fee_settings=fee_settings,
                    fee_type=fee_types[i],
                    amount=amounts[i],
                    due_date=due_date,  # Use the single due date for all fees
                    late_fee=late_fees[i] if i < len(late_fees) else 0,
                    discount=discounts[i] if i < len(discounts) else 0
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
                    PendingFee.objects.create(
                        student=student,
                        fee_type=fs.fee_type,
                        amount=fs.amount,
                        due_date=fs.due_date,  # This now uses the single due date
                        late_fee=fs.late_fee,
                        discount=fs.discount
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

    return JsonResponse({'sections': section_data})

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
