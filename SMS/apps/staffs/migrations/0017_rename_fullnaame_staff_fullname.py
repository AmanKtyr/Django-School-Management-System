# Generated by Django 4.1.2 on 2025-03-20 06:15

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("staffs", "0016_rename_firstname_staff_fullnaame_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="staff",
            old_name="fullnaame",
            new_name="fullname",
        ),
    ]
