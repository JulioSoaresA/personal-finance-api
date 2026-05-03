from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from transactions.models import Account, Category
from transactions.tests.helpers import create_user, authenticate_user


class PaymentMethodTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="paymentuser", email="payment@test.com")
        self.acc = Account.objects.create(
            user=self.user,
            name="Main Acc",
            account_type="CHECKING",
            initial_balance=1000,
        )
        self.cat = Category.objects.create(
            user=self.user, name="Misc", type="EXPENSE", color="#000000"
        )
        self.client = authenticate_user(self.client, self.user)
        self.url = reverse("transactions:transactions-list")

    def test_create_transaction_with_debit_success(self):
        data = {
            "description": "Debit Purchase",
            "value": "50.00",
            "date": "2026-05-03",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
            "payment_method": "DEBIT",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["payment_method"], "DEBIT")

    def test_create_transaction_with_credit_requires_installments(self):
        data = {
            "description": "Credit Purchase Fail",
            "value": "100.00",
            "date": "2026-05-03",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
            "payment_method": "CREDIT",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("installment_total", response.data)

    def test_create_transaction_with_credit_and_installments_success(self):
        data = {
            "description": "Credit Purchase Success",
            "value": "100.00",
            "date": "2026-05-03",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
            "payment_method": "CREDIT",
            "installment_total": 2,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["payment_method"], "CREDIT")
        self.assertEqual(response.data["installment_total"], 2)

    def test_create_transaction_with_pix_success(self):
        data = {
            "description": "Pix Purchase",
            "value": "30.00",
            "date": "2026-05-03",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
            "payment_method": "PIX",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["payment_method"], "PIX")

    def test_create_transaction_with_cash_success(self):
        data = {
            "description": "Cash Purchase",
            "value": "20.00",
            "date": "2026-05-03",
            "account_id": self.acc.id,
            "category_id": self.cat.id,
            "type": "EXPENSE",
            "payment_method": "CASH",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["payment_method"], "CASH")
