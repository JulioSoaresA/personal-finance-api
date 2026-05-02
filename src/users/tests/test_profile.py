from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from authentication.tests.helpers import sample_user

User = get_user_model()


class UserProfileTest(APITestCase):
    def setUp(self):
        self.user = sample_user(
            username="testprofile",
            email="profile@test.com",
            password="Password123!",
            first_name="Profile",
            last_name="User",
            default_currency="BRL",
        )
        self.url = reverse("users:user_profile")

    def authenticate(self):
        login_url = reverse("authentication:login")
        response = self.client.post(
            login_url,
            {"email": "profile@test.com", "password": "Password123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.cookies["access_token"].value
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_get_profile_authenticated(self):
        self.authenticate()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testprofile")
        self.assertEqual(response.data["email"], "profile@test.com")
        self.assertEqual(response.data["default_currency"], "BRL")

    def test_get_profile_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_success(self):
        self.authenticate()
        data = {"first_name": "Julio Updated", "default_currency": "EUR"}
        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Julio Updated")
        self.assertEqual(response.data["default_currency"], "EUR")

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Julio Updated")
        self.assertEqual(self.user.default_currency, "EUR")

    def test_update_profile_unauthenticated(self):
        data = {"first_name": "New Name"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_invalid_currency(self):
        self.authenticate()
        data = {"default_currency": "XYZ"}
        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("default_currency", response.data)
