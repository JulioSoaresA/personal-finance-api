from decimal import Decimal
import uuid
from transactions.models import Transaction
from dateutil.relativedelta import relativedelta


class TransactionService:
    @staticmethod
    def create_transaction(user, data: dict) -> list[Transaction]:
        installment_total = data.get("installment_total")

        if installment_total and installment_total > 1:
            return TransactionService._create_installment_series(
                user=user, data=data, total_count=installment_total
            )

        transaction = Transaction.objects.create(
            user=user,
            account=data.get("account"),
            category=data.get("category"),
            type=data.get("type"),
            paid=data.get("paid", True),
            description=data.get("description"),
            value=data.get("value"),
            date=data.get("date"),
            notes=data.get("notes", ""),
        )
        return [transaction]

    @staticmethod
    def _create_installment_series(
        user, data: dict, total_count: int
    ) -> list[Transaction]:
        base_description = data.get("description")
        start_date = data.get("date")
        group_id = uuid.uuid4()

        transactions_to_create = []

        if "installment_value" in data and data["installment_value"]:
            installment_value = data["installment_value"]
            has_remainder = False

        else:
            original_value = data.get("value")
            installment_value = (original_value / Decimal(total_count)).quantize(
                Decimal("0.01")
            )
            total_calculated = installment_value * total_count
            remainder = original_value - total_calculated
            has_remainder = True

        for i in range(total_count):
            current_installment_number = i + 1
            due_date = start_date + relativedelta(months=i)

            final_value = installment_value

            if i == 0 and has_remainder:
                final_value += remainder

            transaction = Transaction(
                user=user,
                account=data.get("account"),
                category=data.get("category"),
                type=data.get("type"),
                paid=False,
                description=f"{base_description} ({current_installment_number}/{total_count})",
                value=final_value,
                date=due_date,
                installment_group_id=group_id,
                installment_current=current_installment_number,
                installment_total=total_count,
            )
            transactions_to_create.append(transaction)

        return Transaction.objects.bulk_create(transactions_to_create)

    @staticmethod
    def delete_installment_series(transaction_instance) -> int:
        group_id = transaction_instance.installment_group_id

        if not group_id:
            transaction_instance.delete()
            return 1

        count, _ = Transaction.objects.filter(installment_group_id=group_id).delete()

        return count
