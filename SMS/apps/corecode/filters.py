# filters.py या forms.py
from django import forms
from .models import current_class, Section

class ClassSectionFilterForm(forms.Form):
    class_name = forms.ModelChoiceField(
        queryset=current_class.objects.all(),
        required=False,
        empty_label="-- सभी कक्षाएं --",
        label="कक्षा चुनें",
        widget=forms.Select(attrs={'current_class': 'form-select', 'onchange': 'this.form.submit()'}),
    )
    
    section = forms.ModelChoiceField(
        queryset=Section.objects.all(),
        required=False,
        empty_label="-- सभी सेक्शन --",
        label="सेक्शन चुनें",
        widget=forms.Select(attrs={'current_class': 'form-select', 'onchange': 'this.form.submit()'}),
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # यदि क्लास चुनी गई है तो सेक्शन क्वेरीसेट फिल्टर करें
        if 'class_name' in self.data and self.data['class_name']:
            try:
                class_id = int(self.data['class_name'])
                self.fields['section'].queryset = Section.objects.filter(class_name_id=class_id)
            except (ValueError, TypeError):
                pass