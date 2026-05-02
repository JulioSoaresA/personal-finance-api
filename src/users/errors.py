from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class UsernameAlreadyExistsError(ValidationError):
    default_code = "username_exists"
    default_detail = _("A user with that username already exists.")

class EmailAlreadyExistsError(ValidationError):
    default_code = "email_exists"
    default_detail = _("A user with that email already exists.")

class FirstNameRequiredError(ValidationError):
    default_code = "first_name_required"
    default_detail = _("First name is required.")

class LastNameRequiredError(ValidationError):
    default_code = "last_name_required"
    default_detail = _("Last name is required.")

class PasswordsDoNotMatchError(ValidationError):
    default_code = "passwords_mismatch"
    default_detail = _("Passwords do not match")
