# Generated by Django 5.2 on 2025-04-08 05:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("fees", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="feepayment",
            name="fee_category",
            field=models.CharField(default="Regular", max_length=50),
        ),
        migrations.AddField(
            model_name="feepayment",
            name="status",
            field=models.CharField(
                choices=[("Paid", "Paid"), ("Pending", "Pending")],
                default="Pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="student",
            name="roll_number",
            field=models.CharField(blank=True, default="NA", max_length=50),
        ),
        migrations.AddField(
            model_name="student",
            name="section",
            field=models.CharField(blank=True, default="A", max_length=10),
        ),
        migrations.AlterField(
            model_name="student",
            name="class_name",
            field=models.CharField(blank=True, default="NA", max_length=50),
        ),
    ]
