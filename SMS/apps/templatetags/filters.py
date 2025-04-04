from django import template

from students.models import (
    Student,
    current_class,
    Section
)
register = template.Library()

@register.inclusion_tag('dropdown_filter.html')
def class_section_filter():
    classes = current_class.objects.all()  # Assuming you have a Class model
    sections = Section.objects.all()  # Assuming you have a Section model
    return {'classes': classes, 'sections': sections}
