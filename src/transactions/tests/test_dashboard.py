from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from transactions.models import Transaction, Account, Category
from transactions.tests.helpers import create_user, authenticate_user
from datetime import date
from decimal import Decimal


class DashboardTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="dashuser", email="dash@test.com")
        self.acc = Account.objects.create(
            user=self.user,
            name="Checking",
            account_type="CHECKING",
            initial_balance=1000,
        )
        self.cat_income = Category.objects.create(
            user=self.user, name="Salary", type="INCOME", color="#00FF00"
        )
        self.cat_expense = Category.objects.create(
            user=self.user, name="Food", type="EXPENSE", color="#FF0000"
        )

        Transaction.objects.create(
            user=self.user,
            account=self.acc,
            category=self.cat_income,
            type="INCOME",
            value=Decimal("5000.00"),
            date=date(2026, 5, 10),
            description="Salary May",
        )
        Transaction.objects.create(
            user=self.user,
            account=self.acc,
            category=self.cat_expense,
            type="EXPENSE",
            value=Decimal("1200.00"),
            date=date(2026, 5, 15),
            description="Supermarket",
        )
        Transaction.objects.create(
            user=self.user,
            account=self.acc,
            category=self.cat_expense,
            type="EXPENSE",
            value=Decimal("500.00"),
            date=date(2026, 6, 1),
            description="Future expense",
        )

        self.client = authenticate_user(self.client, self.user)
        self.url = reverse("transactions:dashboard")

    def test_dashboard_summary_success(self):
        response = self.client.get(
            f"{self.url}?start_date=2026-05-01&end_date=2026-05-31"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["total_income"]), 5000.00)
        self.assertEqual(float(response.data["total_expense"]), 1200.00)
        self.assertEqual(float(response.data["balance"]), 3800.00)

        self.assertEqual(len(response.data["expense_by_category"]), 1)
        self.assertEqual(
            response.data["expense_by_category"][0]["category_name"], "Food"
        )
        self.assertEqual(
            float(response.data["expense_by_category"][0]["total"]), 1200.00
        )

    def test_dashboard_unauthenticated_fails(self):
        self.client.credentials()  # Remove auth
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
