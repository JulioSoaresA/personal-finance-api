from django.db import models
from django.conf import settings
from core.models import BaseModel
from django.utils.translation import gettext_lazy as _


class Category(BaseModel):
    class TypeChoices(models.TextChoices):
        INCOME = "INCOME", _("Income")
        EXPENSE = "EXPENSE", _("Expense")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="categories",
        verbose_name=_("User"),
    )
    name = models.CharField(max_length=50, verbose_name=_("Category Name"))
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Slug of the icon (ex: 'mdi-home')"),
        verbose_name=_("Icon"),
    )
    color = models.CharField(
        max_length=7,
        default="#000000",
        help_text=_("HEX Color"),
        verbose_name=_("Color"),
    )
    type = models.CharField(
        max_length=7, choices=TypeChoices.choices, verbose_name=_("Type")
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        unique_together = ("user", "name", "type")

    def __str__(self) -> str:
        return f"{self.name} ({self.get_type_display()})"


class Account(BaseModel):
    class AccountType(models.TextChoices):
        CASH = "CASH", "Dinheiro Físico"
        CHECKING = "CHECKING", "Conta Corrente"
        SAVINGS = "SAVINGS", "Poupança"
        INVESTMENT = "INVESTMENT", "Investimento"
        CREDIT_CARD = "CREDIT_CARD", "Cartão de Crédito"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="accounts",
        verbose_name=_("User"),
    )
    name = models.CharField(max_length=50, verbose_name=_("Account Name"))
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.CHECKING,
        verbose_name=_("Account Type"),
    )
    initial_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, verbose_name=_("Initial Balance")
    )

    closing_day = models.PositiveSmallIntegerField(verbose_name=_("Closing Day"))
    due_day = models.PositiveSmallIntegerField(verbose_name=_("Due Day"))

    class Meta:
        verbose_name = _("Account")

    def __str__(self):
        return f"{self.name} - {self.get_account_type_display()}"


class Transaction(BaseModel):
    class TransactionType(models.TextChoices):
        INCOME = "INCOME", _("Income")
        EXPENSE = "EXPENSE", _("Expense")
        TRANSFER = "TRANSFER", _("Transfer")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User")
    )

    account = models.ForeignKey(
        "transactions.Account",
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name=_("Account"),
    )
    category = models.ForeignKey(
        "transactions.Category",
        on_delete=models.SET_NULL,
        null=True,
        related_name="transactions",
        verbose_name=_("Category"),
    )

    description = models.CharField(max_length=255, verbose_name=_("Description"))
    value = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Value")
    )
    date = models.DateField(verbose_name=_("Competence Date"))
    paid = models.BooleanField(default=True, verbose_name=_("Paid"))
    type = models.CharField(
        max_length=10, choices=TransactionType.choices, verbose_name=_("Type")
    )

    installment_group_id = models.UUIDField(
        null=True,
        blank=True,
        help_text=_("ID that groups installments of the same purchase"),
        verbose_name=_("Installment Group ID"),
    )
    installment_current = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Current installment number (ex: 1)"),
        verbose_name=_("Installment Current"),
    )
    installment_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Total installments (ex: 12)"),
        verbose_name=_("Installment Total"),
    )

    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["installment_group_id"]),
        ]

    def __str__(self):
        return f"{self.description} - {self.value}"
