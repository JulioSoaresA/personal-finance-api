from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.errors import (
    UsernameAlreadyExistsError,
    EmailAlreadyExistsError,
    FirstNameRequiredError,
    LastNameRequiredError,
    PasswordsDoNotMatchError,
)

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            "default_currency",
        )

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise UsernameAlreadyExistsError
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise EmailAlreadyExistsError
        return value

    def validate_first_name(self, value):
        if not value:
            raise FirstNameRequiredError
        return value

    def validate_last_name(self, value):
        if not value:
            raise LastNameRequiredError
        return value

    def validate(self, data):
        if data.get("password") != data.get("password2"):
            raise PasswordsDoNotMatchError

        validate_password(data.get("password"))

        return data

    def create(self, validated_data):
        validated_data.pop("password2", None)
        username = validated_data.pop("username")
        email = validated_data.pop("email", None)
        first_name = validated_data.pop("first_name", None)
        last_name = validated_data.pop("last_name", None)
        password = validated_data.pop("password")
        default_currency = validated_data.pop("default_currency", None)

        username_norm = username.lower()
        email_norm = email.lower() if email else email

        if default_currency:
            user = User.objects.create_user(
                username_norm,
                email_norm,
                password,
                first_name=first_name,
                last_name=last_name,
                default_currency=default_currency,
            )
        else:
            user = User.objects.create_user(
                username_norm,
                email_norm,
                password,
                first_name=first_name,
                last_name=last_name,
            )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "default_currency",
        )
