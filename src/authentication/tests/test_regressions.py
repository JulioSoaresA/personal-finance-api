from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthRegressionsTest(APITestCase):
    def test_registration_missing_fields_returns_400(self):
        url = reverse("authentication:register")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "password2": "Password123!",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)

    def test_registration_success(self):
        url = reverse("authentication:register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123!",
            "password2": "Password123!",
            "first_name": "New",
            "last_name": "User",
            "default_currency": "BRL",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "newuser")
        self.assertEqual(response.data["default_currency"], "BRL")

    def test_registration_passwords_do_not_match(self):
        url = reverse("authentication:register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123!",
            "password2": "WrongPassword!",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_registration_duplicate_email(self):
        # Create an initial user
        User.objects.create_user(
            username="existinguser",
            email="duplicate@example.com",
            password="Password123!",
            first_name="Existing",
            last_name="User",
        )

        url = reverse("authentication:register")
        data = {
            "username": "newuser",
            "email": "duplicate@example.com",
            "password": "Password123!",
            "password2": "Password123!",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_weak_password(self):
        url = reverse("authentication:register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "123",
            "password2": "123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_login_empty_body(self):
        url = reverse("authentication:login")
        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)

    def test_login_wrong_password(self):
        User.objects.create_user(
            username="loginuser", email="login@test.com", password="SecureP@ss123"
        )
        url = reverse("authentication:login")
        data = {"email": "login@test.com", "password": "WrongPassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_login_non_existent_email(self):
        url = reverse("authentication:login")
        data = {"email": "nonexistent@test.com", "password": "SomePassword"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        User.objects.create_user(
            username="logoutuser", email="logout@example.com", password="password"
        )
        login_url = reverse("authentication:login")
        login_res = self.client.post(
            login_url,
            {"email": "logout@example.com", "password": "password"},
            format="json",
        )

        url = reverse("authentication:logout")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_res.cookies['access_token'].value}"
        )

        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("success", response.data)
        self.assertEqual(response.cookies["access_token"].value, "")

    def test_logout_no_auth_token(self):
        url = reverse("authentication:logout")
        # Ensure no auth token is provided
        self.client.credentials()
        if "access_token" in self.client.cookies:
            del self.client.cookies["access_token"]

        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_already_blacklisted_token(self):
        User.objects.create_user(
            username="blacklistuser", email="blacklist@test.com", password="password"
        )
        login_url = reverse("authentication:login")
        login_res = self.client.post(
            login_url,
            {"email": "blacklist@test.com", "password": "password"},
            format="json",
        )

        access_token = login_res.cookies["access_token"].value
        refresh_token = login_res.cookies["refresh_token"].value
        url = reverse("authentication:logout")

        # First logout (success)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        self.client.cookies["refresh_token"] = refresh_token
        res1 = self.client.post(url, {}, format="json")
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # Second logout with SAME token (already blacklisted)
        # Should return 200 OK as it is handled gracefully in views.py
        res2 = self.client.post(url, {}, format="json")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

    def test_refresh_token_success(self):
        User.objects.create_user(
            username="refreshuser", email="refresh@example.com", password="password"
        )
        login_url = reverse("authentication:login")
        login_res = self.client.post(
            login_url,
            {"email": "refresh@example.com", "password": "password"},
            format="json",
        )

        refresh_token = login_res.cookies["refresh_token"].value

        url = reverse("authentication:token_refresh")
        self.client.cookies["refresh_token"] = refresh_token

        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["refreshed"])
        self.assertIn("access_token", response.cookies)

    def test_refresh_token_no_cookie(self):
        url = reverse("authentication:token_refresh")
        # Ensure no refresh_token cookie is present
        if "refresh_token" in self.client.cookies:
            del self.client.cookies["refresh_token"]

        response = self.client.post(url, {}, format="json")

        # As noted by the user, currently returns 400 when cookie is missing
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token_reuse(self):
        User.objects.create_user(
            username="reuseuser", email="reuse@test.com", password="password"
        )
        login_url = reverse("authentication:login")
        login_res = self.client.post(
            login_url,
            {"email": "reuse@test.com", "password": "password"},
            format="json",
        )

        refresh_token = login_res.cookies["refresh_token"].value
        url = reverse("authentication:token_refresh")

        # First refresh (success)
        self.client.cookies["refresh_token"] = refresh_token
        res1 = self.client.post(url, {}, format="json")
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        # Second refresh with the SAME old token (should fail as it was rotated and blacklisted)
        self.client.cookies["refresh_token"] = refresh_token
        res2 = self.client.post(url, {}, format="json")

        self.assertEqual(res2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cookies_auth_with_invalid_header_falls_back_to_valid_cookie(self):
        User.objects.create_user(
            username="cookieuser", email="cookie@example.com", password="password"
        )
        login_url = reverse("authentication:login")
        login_res = self.client.post(
            login_url,
            {"email": "cookie@example.com", "password": "password"},
            format="json",
        )
        access_token = login_res.cookies["access_token"].value

        url = reverse("authentication:logout")

        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token")
        self.client.cookies["access_token"] = access_token
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cookies_auth_with_invalid_cookie_returns_none(self):
        url = reverse("authentication:logout")

        self.client.cookies["access_token"] = "invalid_token_in_cookie"
        self.client.credentials()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
