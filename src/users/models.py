from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import BaseModel
from django.utils.translation import gettext_lazy as _


class User(AbstractUser, BaseModel):
    CURRENCY_CHOICES = (
        ("USD", _("US Dollar")),
        ("BRL", _("Brazilian Real")),
        ("EUR", _("Euro")),
    )
    email = models.EmailField(_("email address"), unique=True)

    default_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="USD",
        verbose_name=_("default currency"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.email
