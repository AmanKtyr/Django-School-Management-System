# Generated by Django 5.1.6 on 2025-03-05 05:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0009_rename_parents_name_student_father_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='registration_number',
        ),
    ]
