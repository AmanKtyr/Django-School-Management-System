from django import forms
from .models import StudentClass
from apps.students.models import Student

class ClassSectionFilterForm(forms.Form):
    class_name = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        required=False,
        empty_label="-- All Classes--",
        label="Select Class",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'class-filter'
        }),
    )

    section = forms.ChoiceField(
        choices=[],
        required=False,
        label="Select Section",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'section-filter'
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sections = Student.objects.values_list('section', flat=True).distinct()
        section_choices = [('', '-- All Sections --')] + [(section, section) for section in sections if section]
        self.fields['section'].choices = section_choices
