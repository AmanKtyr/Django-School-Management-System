# Generated by Django 5.1.6 on 2025-03-05 08:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0014_remove_student_registration_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='Father_name',
            new_name='father_name',
        ),
        migrations.RenameField(
            model_name='student',
            old_name='Mother_name',
            new_name='mother_name',
        ),
        migrations.RemoveField(
            model_name='student',
            name='Father_aadhar',
        ),
        migrations.RemoveField(
            model_name='student',
            name='Father_mobile_number',
        ),
        migrations.AddField(
            model_name='student',
            name='barcode_image',
            field=models.ImageField(blank=True, null=True, upload_to='students/barcodes/'),
        ),
        migrations.AddField(
            model_name='student',
            name='registration_number',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='aadhar',
            field=models.CharField(blank=True, max_length=12, validators=[django.core.validators.RegexValidator(message='Aadhaar number must be exactly 12 digits.', regex='^\\d{12}$')]),
        ),
        migrations.AlterField(
            model_name='student',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=13, validators=[django.core.validators.RegexValidator(message='Invalid mobile number format!', regex='^[0-9]{10,15}$')]),
        ),
        migrations.AddField(
            model_name='student',
            name='father_aadhar',
            field=models.CharField(blank=True, max_length=12, validators=[django.core.validators.RegexValidator(message='Aadhaar number must be exactly 12 digits.', regex='^\\d{12}$')]),
        ),
        migrations.AddField(
            model_name='student',
            name='father_mobile_number',
            field=models.CharField(default='0000000000', max_length=15, validators=[django.core.validators.RegexValidator(message='Invalid mobile number format!', regex='^[0-9]{10,15}$')]),
        ),
    ]
