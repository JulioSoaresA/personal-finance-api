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
        # first_name and last_name are missing
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
            "default_currency": "BRL"
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
            "last_name": "User"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_login_missing_all_fields_shows_field_name_in_error(self):
        url = reverse("authentication:login")
        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_logout_success(self):
        # Create and login user to get cookies
        user = User.objects.create_user(username="logoutuser", email="logout@example.com", password="password")
        login_url = reverse("authentication:login")
        login_res = self.client.post(login_url, {"email": "logout@example.com", "password": "password"}, format="json")
        
        # Now logout
        url = reverse("authentication:logout")
        # Ensure we are authenticated (LogoutView requires IsAuthenticated)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_res.cookies["access_token"].value}')
        
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("success", response.data)
        # Cookies should be deleted (or set to empty)
        self.assertEqual(response.cookies["access_token"].value, "")

    def test_refresh_token_success(self):
        # Create and login user to get refresh cookie
        user = User.objects.create_user(username="refreshuser", email="refresh@example.com", password="password")
        login_url = reverse("authentication:login")
        login_res = self.client.post(login_url, {"email": "refresh@example.com", "password": "password"}, format="json")
        
        refresh_token = login_res.cookies["refresh_token"].value
        
        url = reverse("authentication:token_refresh")
        # The view expects refresh token in cookies
        self.client.cookies["refresh_token"] = refresh_token
        
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["refreshed"])
        self.assertIn("access_token", response.cookies)

    def test_cookies_auth_with_invalid_header_falls_back_to_valid_cookie(self):
        # Create and login user to get valid cookie
        user = User.objects.create_user(username="cookieuser", email="cookie@example.com", password="password")
        login_url = reverse("authentication:login")
        login_res = self.client.post(login_url, {"email": "cookie@example.com", "password": "password"}, format="json")
        access_token = login_res.cookies["access_token"].value
        
        # We'll hit a simple protected endpoint
        url = reverse("authentication:logout")
        
        # 1. Invalid header + Valid cookie -> Should succeed
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token")
        self.client.cookies["access_token"] = access_token
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cookies_auth_with_invalid_cookie_returns_none(self):
        url = reverse("authentication:logout")
        
        # 2. Invalid cookie -> Should fail
        self.client.cookies["access_token"] = "invalid_token_in_cookie"
        # Clear credentials just in case
        self.client.credentials()
        response = self.client.post(url)
        # It should return 401 because authentication returned None
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
