from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from authentication.tests.helpers import sample_user
from transactions.models import Account, Category, Transaction
from datetime import date

User = get_user_model()


class AccountTest(APITestCase):
    def setUp(self):
        self.user = sample_user(
            username="accountuser",
            email="account@test.com",
            password="Password123!",
        )
        self.url = reverse("transactions:accounts-list")

    def authenticate(self):
        login_url = reverse("authentication:login")
        response = self.client.post(
            login_url,
            {"email": "account@test.com", "password": "Password123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.cookies["access_token"].value
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_create_checking_account_success(self):
        self.authenticate()
        data = {
            "name": "Nubank Checking",
            "account_type": "CHECKING",
            "initial_balance": "5000.00",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Nubank Checking")
        self.assertEqual(response.data["account_type"], "CHECKING")

    def test_create_credit_card_missing_days_fails(self):
        self.authenticate()
        data = {
            "name": "Nubank Credit",
            "account_type": "CREDIT_CARD",
            "initial_balance": "0.00",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_create_credit_card_with_days_success(self):
        self.authenticate()
        data = {
            "name": "Nubank Credit",
            "account_type": "CREDIT_CARD",
            "initial_balance": "0.00",
            "closing_day": 5,
            "due_day": 15,
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["closing_day"], 5)
        self.assertEqual(response.data["due_day"], 15)

    def test_create_account_unauthenticated(self):
        data = {
            "name": "Anonymous Account",
            "account_type": "CASH",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_accounts_success(self):
        Account.objects.create(user=self.user, name="Acc 1", account_type="CASH")
        Account.objects.create(user=self.user, name="Acc 2", account_type="CHECKING")

        self.authenticate()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 2)

    def test_list_accounts_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_account_empty_success(self):
        acc = Account.objects.create(
            user=self.user, name="To Delete", account_type="CASH"
        )
        url = reverse("transactions:accounts-detail", kwargs={"pk": acc.pk})

        self.authenticate()
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Account.objects.filter(pk=acc.pk).exists())

    def test_delete_account_with_transactions_fails(self):
        acc = Account.objects.create(
            user=self.user, name="With Trans", account_type="CASH"
        )
        cat = Category.objects.create(user=self.user, name="Food", type="EXPENSE")
        Transaction.objects.create(
            user=self.user,
            account=acc,
            category=cat,
            description="Buy bread",
            value=10.00,
            date=date.today(),
            type="EXPENSE",
        )
        url = reverse("transactions:accounts-detail", kwargs={"pk": acc.pk})

        self.authenticate()
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertTrue(Account.objects.filter(pk=acc.pk).exists())

    def test_delete_other_user_account_fails(self):
        other_user = sample_user(username="other", email="other@user.com")
        acc = Account.objects.create(
            user=other_user, name="Other Acc", account_type="CASH"
        )
        url = reverse("transactions:accounts-detail", kwargs={"pk": acc.pk})

        self.authenticate()  # as self.user
        response = self.client.delete(url)

        # Should be 404 because get_queryset filters by self.request.user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Account.objects.filter(pk=acc.pk).exists())
