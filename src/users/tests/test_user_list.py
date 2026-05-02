from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from authentication.tests.helpers import sample_user, sample_superuser

User = get_user_model()


class UserListTest(APITestCase):
    def setUp(self):
        # Admin user
        self.admin = sample_superuser(
            username="adminuser",
            email="admin@test.com",
            password="AdminPassword123!",
        )
        # Regular user
        self.regular_user = sample_user(
            username="regularuser",
            email="regular@test.com",
            password="UserPassword123!",
        )
        # Another user to see in the list
        self.other_user = sample_user(
            username="otheruser",
            email="other@test.com",
        )

        self.url = reverse("users:user_list")

    def authenticate(self, email, password):
        login_url = reverse("authentication:login")
        response = self.client.post(
            login_url,
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.cookies["access_token"].value
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    def test_user_list_admin_success(self):
        self.authenticate("admin@test.com", "AdminPassword123!")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results might be in "results" if paginated, or direct list
        results = response.data.get("results", response.data)
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) >= 2)  # Should see regular_user and other_user

    def test_user_list_admin_excludes_self(self):
        self.authenticate("admin@test.com", "AdminPassword123!")
        response = self.client.get(self.url)

        results = response.data.get("results", response.data)
        emails = [u["email"] for u in results]
        self.assertNotIn("admin@test.com", emails)

    def test_user_list_regular_user_forbidden(self):
        self.authenticate("regular@test.com", "UserPassword123!")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_list_search(self):
        self.authenticate("admin@test.com", "AdminPassword123!")

        # Search for "other"
        response = self.client.get(f"{self.url}?search=other")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["username"], "otheruser")
