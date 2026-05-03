from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from transactions.models import Transaction, Account, Category
from transactions.tests.helpers import create_user, authenticate_user


class TransactionRegressionsTest(APITestCase):
    def setUp(self):
        self.user1 = create_user(username="user1", email="user1@test.com")
        self.user2 = create_user(username="user2", email="user2@test.com")

        self.acc1 = Account.objects.create(
            user=self.user1, name="Acc 1", account_type="CHECKING", initial_balance=1000
        )
        self.acc2 = Account.objects.create(
            user=self.user2, name="Acc 2", account_type="CHECKING", initial_balance=1000
        )

        self.cat1 = Category.objects.create(
            user=self.user1, name="Cat 1", type="EXPENSE", color="#FF0000"
        )
        self.cat2 = Category.objects.create(
            user=self.user2, name="Cat 2", type="EXPENSE", color="#00FF00"
        )

        self.transaction = Transaction.objects.create(
            user=self.user1,
            account=self.acc1,
            category=self.cat1,
            description="Base Transaction",
            value=100,
            date="2024-01-01",
            type="EXPENSE",
        )

        self.client = authenticate_user(self.client, self.user1)

    def test_update_transaction_with_other_user_account_fails_idor(self):
        url = reverse("transactions:transactions-detail", args=[self.transaction.id])
        data = {"account_id": self.acc2.id}  # Acc 2 belongs to user2

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("account_id", response.data)

        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.account, self.acc1)

    def test_update_transaction_with_other_user_category_fails_idor(self):
        url = reverse("transactions:transactions-detail", args=[self.transaction.id])
        data = {"category_id": self.cat2.id}  # Cat 2 belongs to user2

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category_id", response.data)

    def test_create_transaction_with_other_user_account_fails_idor(self):
        url = reverse("transactions:transactions-list")
        data = {
            "description": "Hacked",
            "value": 50,
            "date": "2024-01-01",
            "account_id": self.acc2.id,
            "type": "EXPENSE",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_update_other_users_transaction(self):
        other_transaction = Transaction.objects.create(
            user=self.user2,
            account=self.acc2,
            category=self.cat2,
            description="User2 Transaction",
            value=50,
            date="2024-01-01",
            type="EXPENSE",
        )

        url = reverse("transactions:transactions-detail", args=[other_transaction.id])
        data = {"description": "Updated by user1"}

        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_series_regression(self):
        from transactions.services import TransactionService
        from datetime import date

        series_data = {
            "account": self.acc1,
            "category": self.cat1,
            "description": "Series",
            "value": 300,
            "date": date(2024, 1, 1),
            "type": "EXPENSE",
            "installment_total": 3,
        }
        transactions = TransactionService.create_transaction(self.user1, series_data)
        self.assertEqual(len(transactions), 3)

        group_id = transactions[0].installment_group_id
        url = reverse(
            "transactions:transactions-delete-series", args=[transactions[0].id]
        )

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            Transaction.objects.filter(installment_group_id=group_id).exists()
        )


class TransactionCreationTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="transuser", email="trans@test.com")
        self.acc = Account.objects.create(
            user=self.user,
            name="Main Acc",
            account_type="CHECKING",
            initial_balance=1000,
        )
        self.cat = Category.objects.create(
            user=self.user, name="Food", type="EXPENSE", color="#FF0000"
        )
        self.client = authenticate_user(self.client, self.user)
        self.url = reverse("transactions:transactions-list")

    def test_create_single_transaction_success(self):
        data = {
            "description": "Grocery shopping",
            "value": "250.00",
            "date": "2026-05-01",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
            "paid": True,
            "notes": "Weekly groceries",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["description"], "Grocery shopping")
        self.assertEqual(float(response.data["value"]), 250.00)

    def test_create_transaction_missing_fields_fails(self):
        data = {
            "description": "Missing Value",
            "date": "2026-05-01",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            isinstance(response.data, list) or "non_field_errors" in response.data
        )

    def test_create_transaction_invalid_date_fails(self):
        data = {
            "description": "Invalid Date",
            "value": "100.00",
            "date": "INVALID-DATE",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.data)

    def test_create_transaction_with_other_user_account_fails(self):
        other_user = create_user(username="otheruser", email="other@test.com")
        other_acc = Account.objects.create(
            user=other_user, name="Other Acc", account_type="CASH"
        )
        data = {
            "description": "IDOR",
            "value": "10.00",
            "date": "2026-05-01",
            "account_id": other_acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("account_id", response.data)

    def test_create_transaction_missing_both_values_fails(self):
        data = {
            "description": "No Value",
            "date": "2026-05-01",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            isinstance(response.data, list) or "non_field_errors" in response.data
        )


class TransactionInstallmentTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="instuser", email="inst@test.com")
        self.acc = Account.objects.create(
            user=self.user,
            name="Main Acc",
            account_type="CHECKING",
            initial_balance=10000,
        )
        self.cat = Category.objects.create(
            user=self.user, name="Electronics", type="EXPENSE", color="#0000FF"
        )
        self.client = authenticate_user(self.client, self.user)
        self.url = reverse("transactions:transactions-list")

    def test_create_installments_from_total_value_success(self):
        data = {
            "description": "New Laptop",
            "value": "6000.00",
            "date": "2026-05-01",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
            "installment_total": 12,
            "notes": "12x installments",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["installment_total"], 12)
        self.assertIsNotNone(response.data["installment_group_id"])

        self.assertEqual(
            Transaction.objects.filter(
                installment_group_id=response.data["installment_group_id"]
            ).count(),
            12,
        )

        first_trans = Transaction.objects.get(id=response.data["id"])
        self.assertEqual(float(first_trans.value), 500.00)

    def test_create_installments_from_fixed_installment_value_success(self):
        data = {
            "description": "Subscription",
            "installment_value": "100.00",
            "date": "2026-05-01",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
            "installment_total": 5,
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["installment_total"], 5)

        first_trans = Transaction.objects.get(id=response.data["id"])
        self.assertEqual(float(first_trans.value), 100.00)

        self.assertEqual(
            Transaction.objects.filter(
                installment_group_id=response.data["installment_group_id"]
            ).count(),
            5,
        )

    def test_create_installments_missing_total_fails(self):
        data = {
            "description": "Invalid",
            "installment_value": "100.00",
            "date": "2026-05-01",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("installment_total", response.data)

    def test_delete_installment_series_success(self):
        data = {
            "description": "Series to Delete",
            "value": "300.00",
            "date": "2026-05-01",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
            "installment_total": 3,
        }
        res = self.client.post(self.url, data, format="json")
        group_id = res.data["installment_group_id"]
        trans_id = res.data["id"]

        delete_url = reverse(
            "transactions:transactions-delete-series", kwargs={"pk": trans_id}
        )
        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")  # Verify no body

        self.assertEqual(
            Transaction.objects.filter(installment_group_id=group_id).count(), 0
        )

    def test_delete_non_series_fails(self):
        data = {
            "description": "Single",
            "value": "100.00",
            "date": "2026-05-01",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
        }
        res = self.client.post(self.url, data, format="json")
        trans_id = res.data["id"]

        delete_url = reverse(
            "transactions:transactions-delete-series", kwargs={"pk": trans_id}
        )
        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_delete_series_other_user_fails(self):
        other_user = create_user(username="otherinst", email="otherinst@test.com")
        other_acc = Account.objects.create(
            user=other_user, name="Other", account_type="CASH"
        )
        other_cat = Category.objects.create(
            user=other_user, name="Other", type="EXPENSE"
        )

        from decimal import Decimal
        from transactions.services import TransactionService

        other_trans = TransactionService.create_transaction(
            user=other_user,
            data={
                "description": "Other Series",
                "value": Decimal("100.00"),
                "date": date(2026, 5, 1),
                "account": other_acc,
                "category": other_cat,
                "type": "EXPENSE",
                "installment_total": 2,
            },
        )[0]

        delete_url = reverse(
            "transactions:transactions-delete-series", kwargs={"pk": other_trans.id}
        )
        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
