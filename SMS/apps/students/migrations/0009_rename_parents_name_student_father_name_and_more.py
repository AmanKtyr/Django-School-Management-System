# Generated by Django 5.1.6 on 2025-03-04 11:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0008_alter_student_parents_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='Parents_name',
            new_name='Father_name',
        ),
        migrations.RemoveField(
            model_name='student',
            name='parent_mobile_number',
        ),
        migrations.AddField(
            model_name='student',
            name='Father_aadhar',
            field=models.CharField(blank=True, max_length=12, validators=[django.core.validators.RegexValidator(code='invalid_aadhar', message='Aadhaar number must be exactly 12 digits.', regex='^\\d{12}$')]),
        ),
        migrations.AddField(
            model_name='student',
            name='Father_mobile_number',
            field=models.CharField(default='0000000000', max_length=15, validators=[django.core.validators.RegexValidator(message="Entered mobile number isn't in a right format!", regex='^[0-9]{10,15}$')]),
        ),
        migrations.AddField(
            model_name='student',
            name='Mother_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
