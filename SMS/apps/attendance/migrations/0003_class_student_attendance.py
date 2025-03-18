# Generated by Django 4.1.2 on 2025-03-18 05:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0002_rename_student_studentattendance"),
    ]

    operations = [
        migrations.CreateModel(
            name="Class",
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
                ("name", models.CharField(max_length=100)),
                ("teacher", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Student",
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
                ("name", models.CharField(max_length=100)),
                ("unique_id", models.CharField(max_length=50, unique=True)),
                ("father_name", models.CharField(max_length=100)),
                ("section", models.CharField(max_length=10)),
                (
                    "class_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="attendance.class",
                    ),
                ),
            ],
        ),
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
                ("status", models.CharField(max_length=10)),
                ("date", models.DateField(auto_now_add=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="attendance.student",
                    ),
                ),
            ],
        ),
    ]
