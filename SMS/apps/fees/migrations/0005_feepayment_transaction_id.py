# Generated by Django 5.2 on 2025-04-11 12:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("fees", "0004_pendingfee"),
    ]

    operations = [
        migrations.AddField(
            model_name="feepayment",
            name="transaction_id",
            field=models.CharField(
                blank=True,
                help_text="Required for online or bank transfers",
                max_length=100,
                null=True,
            ),
        ),
    ]
