# filters.py
from django import forms
from .models import Student, StudentClass

class StudentFilter(forms.Form):
    class_choices = StudentClass.objects.all()
    section_choices = Student.objects.values_list('section', flat=True).distinct()

    current_class = forms.ModelChoiceField(queryset=class_choices, required=False)
    section = forms.ChoiceField(choices=[(section, section) for section in section_choices], required=False)
