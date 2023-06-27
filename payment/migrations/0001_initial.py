# Generated by Django 4.2.2 on 2023-06-27 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("borrowings", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("paid", "Paid")],
                        max_length=255,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("payment", "Payment"), ("fine", "Fine")],
                        max_length=255,
                    ),
                ),
                ("session_url", models.URLField()),
                ("session_id", models.CharField(max_length=255)),
                ("money_to_pay", models.DecimalField(decimal_places=2, max_digits=5)),
                (
                    "borrowing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="borrowings.borrowing",
                    ),
                ),
            ],
        ),
    ]
