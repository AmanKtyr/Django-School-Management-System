# filters.py या forms.py
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
            'onchange': 'this.form.submit()',
            'id': 'class-filter'
        }),
    )
    
    section = forms.ChoiceField(
        choices=[],
        required=False,
        label="Select Section",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()',
            'id': 'section-filter'
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get unique sections from Student model
        sections = Student.objects.values_list('section', flat=True).distinct()
        section_choices = [('', '-- All Sections --')] + [(section, section) for section in sections if section]
        self.fields['section'].choices = section_choices

        if 'class_name' in self.data:
            try:
                class_id = int(self.data['class_name'])
                sections = Student.objects.filter(current_class_id=class_id).values_list('section', flat=True).distinct()
                section_choices = [('', '-- All Sections --')] + [(section, section) for section in sections if section]
                self.fields['section'].choices = section_choices
            except (ValueError, TypeError):
                pass
