from typing import Any, Optional, Dict
from rest_framework.test import APIClient
import base64
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

try:
    from constance import config
except Exception:
    config = None

from django.contrib.auth import get_user_model

UserModel = get_user_model()


def login_payload(username: str = "testuser", password: str = "password") -> Dict[str, str]:
    return {"username": username, "password": password}


def user_data(username: str = "testuser", email: Optional[str] = None, password: str = "password") -> Dict[str, str]:
    return {"username": username, "email": email or f"{username}@example.com", "password": password}


_DEFAULT_API_VERSION: Optional[str]
if config is not None:
    try:
        _DEFAULT_API_VERSION = str(getattr(config, "ALLOWED_VERSIONS", "")).split()[0] or None
    except Exception:
        _DEFAULT_API_VERSION = None
else:
    _DEFAULT_API_VERSION = None


def configure_api_client(
    client: APIClient,
    set_header_version: bool = True,
    basic_auth: bool = False,
    access_token: Optional[str] = None,
    user: Optional[Any] = None,
    user_email: Optional[str] = None,
    password: Optional[str] = None,
    version: Optional[str] = None,
    **kwargs,
) -> APIClient:
    headers: Dict[str, str] = {}

    if set_header_version:
        ver = version or _DEFAULT_API_VERSION or "1"
        headers["HTTP_ACCEPT"] = f"application/json; version={ver}"

    if access_token is None:
        access_token = kwargs.get("access_token")

    if access_token and not basic_auth:
        headers["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
    elif user and not basic_auth:
        token = TokenObtainPairSerializer.get_token(user)
        headers["HTTP_AUTHORIZATION"] = f"Bearer {str(token.access_token)}"

    if basic_auth:
        email = user_email or (getattr(user, "email", None) if user is not None else None) or kwargs.get("user_email")
        pwd = password or kwargs.get("password")
        if not email or not pwd:
            raise ValueError("basic_auth requires `user_email` (or `user.email`) and `password`")
        basic_token = base64.b64encode(f"{email}:{pwd}".encode()).decode("iso-8859-1")
        headers["HTTP_AUTHORIZATION"] = f"Basic {basic_token}"

    if headers:
        client.credentials(**headers)
    else:
        client.credentials()

    return client


def sample_user(username: str = "testuser", email: Optional[str] = None, password: str = "password", **extra) -> Any:
    email = email or f"{username}@example.com"
    return UserModel.objects.create_user(username=username, email=email, password=password, **extra)


def sample_superuser(username: str = "admin", email: Optional[str] = None, password: str = "admin", **extra) -> Any:
    email = email or f"{username}@example.com"
    return UserModel.objects.create_superuser(username=username, email=email, password=password, **extra)
