from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2", "default_currency")

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with that username already exists.",
            )
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, data):
        if data.get("password") != data.get("password2"):
            raise serializers.ValidationError("Passwords do not match")

        validate_password(data.get("password"))

        return data

    def create(self, validated_data):
        validated_data.pop("password2", None)
        username = validated_data.pop("username")
        email = validated_data.pop("email", None)
        password = validated_data.pop("password")
        default_currency = validated_data.pop("default_currency", None)

        username_norm = username.lower()
        email_norm = email.lower() if email else email

        # pass default_currency if provided
        if default_currency:
            user = User.objects.create_user(
                username_norm, email_norm, password, default_currency=default_currency
            )
        else:
            user = User.objects.create_user(username_norm, email_norm, password)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "date_joined", "default_currency")
