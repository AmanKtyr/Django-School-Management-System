# Generated by Django 5.1.6 on 2025-03-05 07:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0008_staff_registration_number_field'),
    ]

    operations = [
        migrations.RenameField(
            model_name='staff',
            old_name='registration_number_field',
            new_name='registration_number',
        ),
    ]
