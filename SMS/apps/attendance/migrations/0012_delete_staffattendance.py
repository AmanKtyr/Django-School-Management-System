# Generated by Django 5.2 on 2025-05-01 09:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0011_staffattendance"),
    ]

    operations = [
        migrations.DeleteModel(
            name="StaffAttendance",
        ),
    ]
