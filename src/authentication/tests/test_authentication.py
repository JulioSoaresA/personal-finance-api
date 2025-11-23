from django.contrib.auth import authenticate
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.factories import UserFactory, SuperUserFactory
from authentication.tests.helpers import login_payload, configure_api_client


class AuthenticationUserTest(APITestCase):
    def setUp(self) -> None:
        super().setUp()

        configure_api_client(self.client)
        self.user = SuperUserFactory(username='admin', password='admin')

    def test_user_authentication_success(self):
        url = reverse("authentication:login")
        
        return self.client.post(url, login_payload('admin', 'admin'), format='json')

    def test_user_authentication_failure(self):
        user = authenticate(username='admin', password='wrongpassword')
        self.assertFalse((user is not None) and user.is_authenticated)


class JWTAuthenticationTest(APITestCase):
    def setUp(self):
        self.user = UserFactory(username='testuser', password='password')
        self.token_url = '/api/auth/login/'

    def test_login_success(self):
        data = login_payload('testuser', 'password')

        response = self.client.post(self.token_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        
        self.assertIn('access_token', response.cookies)
        self.assertTrue(response.cookies['access_token'].value)

    def test_login_invalid_credentials(self):
        data = login_payload('testuser', 'wrongpassword')

        response = self.client.post(self.token_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data)

    def test_login_cookie_settings(self):
        data = login_payload('testuser', 'password')

        response = self.client.post(self.token_url, data, format='json')
        
        cookie = response.cookies.get('access_token')
        self.assertIsNotNone(cookie)
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['samesite'], 'None')
        self.assertTrue(cookie['secure'])
        self.assertEqual(cookie['path'], '/')


class JWTProtectedRouteTest(APITestCase):
    def setUp(self):
        self.user = UserFactory(username='testuser', password='password', email='testuser@example.com')
        self.login_url = '/api/auth/login/'  
        
        self.protected_url = '/api/posts/feed/'

    def authenticate(self):
        data = login_payload('testuser', 'password')
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.cookies['access_token'].value  # Obtém o token do cookie
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def test_access_protected_route_without_authentication(self):
        response = self.client.get(self.protected_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
