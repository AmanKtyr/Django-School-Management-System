# Generated by Django 4.1.2 on 2025-03-20 05:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("students", "0022_alter_student_options_and_more"),
        ("attendance", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attendance",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Present", "Present"),
                            ("Absent", "Absent"),
                            ("Leave", "Leave"),
                        ],
                        default="Absent",
                        max_length=10,
                    ),
                ),
                ("date", models.DateField(auto_now_add=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attendance",
                        to="students.student",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StudentAttendance",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "registration_number",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="Registration Number"
                    ),
                ),
                (
                    "fullname",
                    models.CharField(max_length=100, verbose_name="Full Name"),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[("Male", "Male"), ("Female", "Female")],
                        max_length=10,
                        verbose_name="Gender",
                    ),
                ),
                (
                    "parent_number",
                    models.CharField(
                        max_length=15, verbose_name="Parent's Contact Number"
                    ),
                ),
                ("address", models.TextField(verbose_name="Address")),
                (
                    "current_class",
                    models.CharField(max_length=50, verbose_name="Current Class"),
                ),
                ("section", models.CharField(max_length=10, verbose_name="Section")),
                (
                    "attendance_status",
                    models.CharField(
                        choices=[("Present", "Present"), ("Absent", "Absent")],
                        default="Absent",
                        max_length=10,
                        verbose_name="Attendance Status",
                    ),
                ),
                ("date", models.DateField(auto_now_add=True, verbose_name="Date")),
            ],
        ),
        migrations.DeleteModel(
            name="Student",
        ),
        migrations.DeleteModel(
            name="StudentBulkUpload",
        ),
    ]
