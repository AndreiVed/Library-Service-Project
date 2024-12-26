from django.core.validators import MinValueValidator
from django.db import models

class Book(models.Model):
    COVER_CHOICES = {
        "SOFT": "soft",
        "HARD": "hard"
    }

    title = models.CharField(max_length=63)
    author = models.CharField(max_length=63)
    cover = models.CharField(
        choices=COVER_CHOICES,
        max_length=4,
    )
    inventory = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
)
    daily_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )

    def __str__(self):
        return f"Title: {self.title}, Author: {self.author}"

    class Meta:
        ordering = ["title"]
