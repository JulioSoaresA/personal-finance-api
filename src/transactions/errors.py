from rest_framework.exceptions import ValidationError, APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _

# Serializer Validation Errors


class InvalidColorFormatError(ValidationError):
    default_code = "invalid_color_format"
    default_detail = _("Color should be in the format HEX (#RRGGBB). Example: #FF5733")


class CategoryAlreadyExistsError(ValidationError):
    default_code = "category_exists"

    def __init__(self):
        super().__init__(
            {"name": _("You already have a category with this name and type.")},
            code=self.default_code,
        )


class InvalidCategoryError(ValidationError):
    default_code = "invalid_category"

    def __init__(self):
        super().__init__(
            {"category_id": _("Invalid category.")}, code=self.default_code
        )


class InvalidAccountError(ValidationError):
    default_code = "invalid_account"

    def __init__(self):
        super().__init__({"account_id": _("Invalid account.")}, code=self.default_code)


class InvalidCategoryTypeError(ValidationError):
    default_code = "invalid_category_type"
    default_detail = _("Invalid category type. Only 'income' or 'expense' are allowed.")


class TransferCategoryError(ValidationError):
    default_code = "transfer_category_invalid"
    default_detail = _("Transfer categories are only for transfers.")


class MissingInstallmentsTotalError(ValidationError):
    default_code = "missing_installments"

    def __init__(self):
        super().__init__(
            {
                "installment_total": _(
                    "Necessary to inform the number of installments when the installment value is fixed."
                )
            },
            code=self.default_code,
        )


class MissingTransactionValueError(ValidationError):
    default_code = "missing_transaction_value"
    default_detail = _("Inform the 'value' (total) or 'installment_value'")


class CreditCardDatesRequiredError(ValidationError):
    default_code = "credit_card_dates_required"

    def __init__(self):
        super().__init__(
            {"error": _("For Credit Card, closing and due days are required.")},
            code=self.default_code,
        )


class CreditPaymentInstallmentsRequiredError(ValidationError):
    default_code = "credit_installments_required"

    def __init__(self):
        super().__init__(
            {"installment_total": _("Installments are required for credit payments.")},
            code=self.default_code,
        )


class InvalidRecurrenceUpdateError(ValidationError):
    default_code = "invalid_recurrence_update"
    default_detail = _(
        "To update recurrence, you must choose either all following transactions or only this one."
    )


# View & Service Errors


class CategoryHasTransactionsError(ValidationError):
    default_code = "category_has_transactions"

    def __init__(self):
        super().__init__(
            {
                "error": _(
                    "It is not possible to delete a category that has associated transactions."
                )
            },
            code=self.default_code,
        )


class AccountHasTransactionsError(ValidationError):
    default_code = "account_has_transactions"

    def __init__(self):
        super().__init__(
            {
                "error": _(
                    "It is not possible to delete an account that has transactions. Archive it or delete the transactions first."
                )
            },
            code=self.default_code,
        )


class NotInPaymentPlanError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "not_in_payment_plan"

    def __init__(self):
        super().__init__(
            {"error": _("This transaction is not part of a payment plan.")},
            code=self.default_code,
        )


class InvalidDateUpdateError(ValidationError):
    default_code = "invalid_date_update"
    default_detail = _(
        "For updating this or following transactions, date must not be changed."
    )


class TransactionCreationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "transaction_creation_failed"

    def __init__(self, original_error):
        super().__init__({"error": str(original_error)}, code=self.default_code)
