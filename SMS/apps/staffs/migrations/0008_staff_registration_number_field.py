# Generated by Django 5.1.6 on 2025-03-05 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0007_rename_date_of_reg_staff_date_of_registration'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='registration_number_field',
            field=models.CharField(blank=True, max_length=200, unique=True),
        ),
    ]
