from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "hard"
        SOFT = "soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=255, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField(unique=True)
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
