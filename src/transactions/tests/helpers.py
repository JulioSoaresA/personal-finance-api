from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def create_user(username="testuser", email=None, password="testpass123"):
    email = email or f"{username}@example.com"
    return User.objects.create_user(username=username, email=email, password=password)


def authenticate_user(client: APIClient, user):
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return client


def category_data(
    name="Test Category", icon="mdi-home", color="#FF5733", category_type="EXPENSE"
):
    return {"name": name, "icon": icon, "color": color, "type": category_type}
