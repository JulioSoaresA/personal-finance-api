from django.urls import include, path
from rest_framework import routers

from transactions.views import TransactionViewSet, AccountViewSet

app_name = "transactions"

router = routers.DefaultRouter()

router.register(r"transactions", TransactionViewSet, basename="transactions")
router.register(r"accounts", AccountViewSet, basename="accounts")

urlpatterns = [
    path("", include(router.urls)),
]
