from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username_field = get_user_model().USERNAME_FIELD
        self.fields[self.username_field].required = False

    def validate(self, attrs):
        if attrs.get("username") and not attrs.get(self.username_field):
            attrs[self.username_field] = attrs.pop("username")

        if not attrs.get(self.username_field):
            raise serializers.ValidationError(
                {self.username_field: _("Este campo é obrigatório.")}
            )

        return super().validate(attrs)
