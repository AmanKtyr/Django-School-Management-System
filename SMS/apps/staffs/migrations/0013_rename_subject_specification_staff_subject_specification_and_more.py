# Generated by Django 5.1.6 on 2025-03-05 10:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0012_alter_staff_registration_number'),
    ]

    operations = [
        migrations.RenameField(
            model_name='staff',
            old_name='Subject_specification',
            new_name='subject_specification',
        ),
        migrations.AlterField(
            model_name='staff',
            name='date_of_birth',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='staff',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator(message="Entered mobile number isn't in the correct format!", regex='^\\d{10,15}$')]),
        ),
    ]
