# Generated by Django 5.2 on 2025-04-08 06:04

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("fees", "0002_feepayment_fee_category_feepayment_status_and_more"),
        ("students", "0024_alter_student_father_mobile_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feepayment",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="students.student"
            ),
        ),
        migrations.AlterField(
            model_name="feepayment",
            name="date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.DeleteModel(
            name="Student",
        ),
    ]
