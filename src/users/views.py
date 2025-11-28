from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.throttling import UserRateThrottle

from users.serializers import UserSerializer


class UserListView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerializer
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["username", "email"]

    def get_queryset(self):
        queryset = User.objects.all().exclude(pk=self.request.user.id)

        return queryset


class UserProfileView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerializer
    throttle_classes = [UserRateThrottle]

    def get_object(self):
        return self.request.user
