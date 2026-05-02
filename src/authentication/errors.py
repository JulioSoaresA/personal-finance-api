from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _


class InvalidCredentialsError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "invalid_credentials"
    default_detail = _("Invalid credentials provided.")


class LogoutFailedError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "logout_failed"
    default_detail = _("An error occurred during logout.")
