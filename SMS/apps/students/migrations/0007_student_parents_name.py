# Generated by Django 5.1.6 on 2025-03-04 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0006_student_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='Parents_name',
            field=models.CharField(default='Unknown', max_length=255),
        ),
    ]
