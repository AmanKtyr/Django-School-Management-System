import csv

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets, modelform_factory
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.finance.models import Invoice
from apps.corecode.filters import ClassSectionFilterForm

from .models import Student, StudentBulkUpload, StudentDocument
from .filters import StudentFilter

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "students/student_list.html"
    context_object_name = "students"

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter_form = ClassSectionFilterForm(self.request.GET)

        if self.filter_form.is_valid():
            if self.filter_form.cleaned_data['class_name']:
                queryset = queryset.filter(current_class=self.filter_form.cleaned_data['class_name'])
            if self.filter_form.cleaned_data['section']:
                queryset = queryset.filter(section=self.filter_form.cleaned_data['section'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = "students/student_detail.html"

    def get_context_data(self, **kwargs):
        context = super(StudentDetailView, self).get_context_data(**kwargs)
        context["payments"] = Invoice.objects.filter(student=self.object)

        # Get student documents if they exist
        context['documents'] = StudentDocument.objects.filter(student=self.object).first()

        return context



class StudentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Student
    fields = [f.name for f in Student._meta.fields if f.name != 'registration_number']
    success_message = "New student successfully added."

    def get_form(self):
        """add date picker in forms"""
        form = super(StudentCreateView, self).get_form()
        form.fields["aadhar"].widget=widgets.TextInput(attrs={"row":2})
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 2})
        form.fields["others"].widget = widgets.Textarea(attrs={"rows": 2})
        return form

    def get_success_url(self):
        # Redirect to the student detail page after successful creation
        return reverse_lazy('student-detail', kwargs={'pk': self.object.pk})


class StudentUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Student
    fields = [f.name for f in Student._meta.fields if f.name != 'registration_number']
    success_message = "Record successfully updated."

    def get_form(self):
        """add date picker in forms"""
        form = super(StudentUpdateView, self).get_form()
        form.fields["aadhar"].widget=widgets.TextInput(attrs={"row":2})
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_admission"].widget = widgets.DateInput(
            attrs={"type": "date"}
        )
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 2})
        form.fields["others"].widget = widgets.Textarea(attrs={"rows": 2})
        # form.fields['passport'].widget = widgets.FileInput()
        return form


class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    success_url = reverse_lazy("student-list")


class StudentBulkUploadView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = StudentBulkUpload
    template_name = "students/students_upload.html"
    fields = ["csv_file"]
    success_url = "/student/list"
    success_message = "Successfully uploaded students"


class DownloadCSVViewdownloadcsv(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="student_template.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "registration_number",
                "fullname",
                "gender",
                "parent_number",
                "address",
                "current_class",
            ]
        )

        return response


@login_required
def upload_student_documents(request, pk):
    """Upload documents with their numbers"""
    student = get_object_or_404(Student, pk=pk)

    # Get or create student document record
    student_doc, created = StudentDocument.objects.get_or_create(student=student)

    if request.method == 'POST':
        # Handle document numbers and file uploads

        # Aadhar Card
        if 'aadhar_card' in request.FILES:
            student_doc.aadhar_card = request.FILES.get('aadhar_card')
            if 'aadhar_card_number' in request.POST:
                student_doc.aadhar_card_number = request.POST.get('aadhar_card_number')

        # Parent Photo
        if 'parent_photo' in request.FILES:
            student_doc.parent_photo = request.FILES.get('parent_photo')
            if 'parent_photo_number' in request.POST:
                student_doc.parent_photo_number = request.POST.get('parent_photo_number')

        # Parent ID Proof
        if 'parent_id_proof' in request.FILES:
            student_doc.parent_id_proof = request.FILES.get('parent_id_proof')
            if 'parent_id_proof_number' in request.POST:
                student_doc.parent_id_proof_number = request.POST.get('parent_id_proof_number')

        # Previous Marksheet
        if 'previous_marksheet' in request.FILES:
            student_doc.previous_marksheet = request.FILES.get('previous_marksheet')
            if 'previous_marksheet_number' in request.POST:
                student_doc.previous_marksheet_number = request.POST.get('previous_marksheet_number')

        # Transfer Certificate
        if 'transfer_certificate' in request.FILES:
            student_doc.transfer_certificate = request.FILES.get('transfer_certificate')
            if 'transfer_certificate_number' in request.POST:
                student_doc.transfer_certificate_number = request.POST.get('transfer_certificate_number')

        # Character Certificate
        if 'character_certificate' in request.FILES:
            student_doc.character_certificate = request.FILES.get('character_certificate')
            if 'character_certificate_number' in request.POST:
                student_doc.character_certificate_number = request.POST.get('character_certificate_number')

        # Caste Certificate
        if 'caste_certificate' in request.FILES:
            student_doc.caste_certificate = request.FILES.get('caste_certificate')
            if 'caste_certificate_number' in request.POST:
                student_doc.caste_certificate_number = request.POST.get('caste_certificate_number')

        # Medical Certificate
        if 'medical_certificate' in request.FILES:
            student_doc.medical_certificate = request.FILES.get('medical_certificate')
            if 'medical_certificate_number' in request.POST:
                student_doc.medical_certificate_number = request.POST.get('medical_certificate_number')

        # Other Document
        if 'other_document' in request.FILES:
            student_doc.other_document = request.FILES.get('other_document')
            if 'other_document_number' in request.POST:
                student_doc.other_document_number = request.POST.get('other_document_number')

        # Save the document record
        student_doc.save()

        messages.success(request, 'Documents uploaded successfully!')
        return redirect('student-detail', pk=student.pk)

    context = {
        'student': student,
        'documents': student_doc,
    }

    return render(request, 'students/upload_documents.html', context)

