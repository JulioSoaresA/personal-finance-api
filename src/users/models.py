from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    CURRENCY_CHOICES = (
        ("USD", "US Dollar"),
        ("BRL", "Brazilian Real"),
        ("EUR", "Euro"),
    )

    default_currency = models.CharField(
        max_length=3, choices=CURRENCY_CHOICES, default="USD"
    )

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.username
