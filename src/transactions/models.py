from django.db import models
from django.conf import settings
from core.models import BaseModel


class Category(BaseModel):
    class TypeChoices(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSE = "EXPENSE", "Expense"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="categories"
    )
    name = models.CharField(max_length=50)
    icon = models.CharField(
        max_length=50, blank=True, help_text="Slug do ícone (ex: 'mdi-home')"
    )
    color = models.CharField(max_length=7, default="#000000", help_text="HEX Color")
    type = models.CharField(max_length=7, choices=TypeChoices.choices)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
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
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="accounts"
    )
    name = models.CharField(max_length=50, verbose_name="Nome da Conta")
    account_type = models.CharField(
        max_length=20, choices=AccountType.choices, default=AccountType.CHECKING
    )
    initial_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, verbose_name="Saldo Inicial"
    )

    closing_day = models.PositiveSmallIntegerField(verbose_name="Dia Fechamento")
    due_day = models.PositiveSmallIntegerField(verbose_name="Dia Vencimento")

    class Meta:
        verbose_name = "Conta/Carteira"

    def __str__(self):
        return f"{self.name} - {self.get_account_type_display()}"


class Transaction(BaseModel):
    class TransactionType(models.TextChoices):
        INCOME = "INCOME", "Receita"
        EXPENSE = "EXPENSE", "Despesa"
        TRANSFER = "TRANSFER", "Transferência"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    account = models.ForeignKey(
        "transactions.Account", on_delete=models.PROTECT, related_name="transactions"
    )
    category = models.ForeignKey(
        "transactions.Category",
        on_delete=models.SET_NULL,
        null=True,
        related_name="transactions",
    )

    description = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(verbose_name="Data da Competência")
    paid = models.BooleanField(default=True, verbose_name="Efetivado")
    type = models.CharField(max_length=10, choices=TransactionType.choices)

    installment_group_id = models.UUIDField(
        null=True, blank=True, help_text="ID que agrupa parcelas da mesma compra"
    )
    installment_current = models.PositiveIntegerField(
        null=True, blank=True, help_text="Número da parcela atual (ex: 1)"
    )
    installment_total = models.PositiveIntegerField(
        null=True, blank=True, help_text="Total de parcelas (ex: 12)"
    )

    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["installment_group_id"]),
        ]

    def __str__(self):
        return f"{self.description} - {self.value}"
