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
            # missing value
            "date": "2026-05-01",
            "account_id": self.acc.id,
            "type": "EXPENSE",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("value", response.data)

    def test_create_transaction_invalid_date_fails(self):
        data = {
            "description": "Invalid Date",
            "value": "100.00",
            "date": "INVALID-DATE",
            "account_id": self.acc.id,
            "type": "EXPENSE",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("date", response.data)
