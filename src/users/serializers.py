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
        password = validated_data.pop("password")

        validated_data["username"] = validated_data["username"].lower()
        if validated_data.get("email"):
            validated_data["email"] = validated_data["email"].lower()

        return User.objects.create_user(password=password, **validated_data)


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
