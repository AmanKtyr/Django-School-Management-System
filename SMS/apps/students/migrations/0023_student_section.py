# Generated by Django 4.1.2 on 2025-03-24 07:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0022_alter_student_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="section",
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
