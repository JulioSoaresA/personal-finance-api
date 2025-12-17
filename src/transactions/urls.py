from django.urls import include, path
from rest_framework import routers

from transactions.views import (
    TransactionViewSet,
    AccountViewSet,
    CategoryViewSet,
    DashboardView,
)

app_name = "transactions"

router = routers.DefaultRouter()

router.register(r"transactions", TransactionViewSet, basename="transactions")
router.register(r"accounts", AccountViewSet, basename="accounts")
router.register(r"categories", CategoryViewSet, basename="categories")

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard", DashboardView.as_view(), name="dashboard"),
]
