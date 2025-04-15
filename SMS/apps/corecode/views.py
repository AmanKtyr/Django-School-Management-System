from django.contrib import messages
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
