# Generated by Django 5.1.6 on 2025-03-05 08:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0018_student_barcode_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='barcode_image',
        ),
    ]
