from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from transactions.models import Transaction, Account, Category
from django.db.models import F, Q, Value
from django.db.models.functions import Coalesce
from django.db.models.fields import DecimalField
from transactions.serializers import (
    TransactionSerializer,
    TransactionCreateSerializer,
    DashboardSerializer,
    AccountListSerializer,
    AccountWriteSerializer,
    CategorySerializer,
    CategoryWriteSerializer,
)
from transactions.services import TransactionService
from django.utils.translation import gettext_lazy as _
from datetime import date
from rest_framework.views import APIView


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["type"]
    search_fields = ["name"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CategoryWriteSerializer
        return CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.transactions.exists():
            raise ValidationError(
                {
                    "error": _(
                        "It is not possible to delete a category that has associated transactions."
                    )
                }
            )
        instance.delete()


class TransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["account", "category", "type", "paid"]
    search_fields = ["description"]
    ordering = ["-date"]

    def get_serializer_class(self):
        if self.action == "create":
            return TransactionCreateSerializer
        if self.action == "summary":
            return DashboardSerializer
        return TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.filter(user=user)

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            transactions = TransactionService.create_transaction(
                user=request.user, data=data
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = TransactionSerializer(transactions[0])
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        queryset = self.get_queryset()

        income = (
            queryset.filter(type="INCOME").aggregate(Sum("value"))["value__sum"] or 0
        )
        expense = (
            queryset.filter(type="EXPENSE").aggregate(Sum("value"))["value__sum"] or 0
        )

        data = {
            "total_income": income,
            "total_expense": expense,
            "balance": income - expense,
        }

        return Response(data)

    @action(detail=True, methods=["delete"], url_path="delete-series")
    def delete_series(self, request, pk=None):
        transaction = self.get_object()

        if not transaction.installment_group_id:
            return Response(
                {"error": _("This transaction is not part of a payment plan.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": _("The installments were successfully removed.")},
            status=status.HTTP_204_NO_CONTENT,
        )


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        start_date = request.query_params.get("start_date", today.replace(day=1))
        end_date = request.query_params.get("end_date", today)

        queryset = Transaction.objects.filter(
            user=request.user, date__range=[start_date, end_date]
        )

        summary = queryset.aggregate(
            income=Coalesce(
                Sum("value", filter=Q(type="INCOME")),
                Value(0, output_field=DecimalField()),
            )
        )

        category_data = (
            queryset.filter(type="EXPENSE")
            .values("category")
            .annotate(total=Sum("value"))
            .order_by("-total")
        )

        data = {
            "total_income": summary["income"],
            "total_expense": summary["expense"],
            "balance": summary["income"] - summary["expense"],
            "expense_by_category": category_data,
        }

        serializer = DashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AccountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return AccountListSerializer
        return AccountWriteSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Account.objects.filter(user=user)

        sum_income = Coalesce(
            Sum(
                "transactions__value",
                filter=Q(transactions__type="INCOME", transactions__paid=True),
            ),
            Value(0, output_field=DecimalField()),
        )

        sum_expense = Coalesce(
            Sum(
                "transactions__value",
                filter=Q(
                    transactions__type__in=["EXPENSE", "TRANSFER"],
                    transactions__paid=True,
                ),
            ),
            Value(0, output_field=DecimalField()),
        )

        queryset = queryset.annotate(
            current_balance=F("initial_balance") + sum_income - sum_expense
        )

        return queryset.order_by("name")

    def perform_destroy(self, instance):
        if instance.transactions.exists():
            raise ValidationError(
                {
                    "error": _(
                        "It is not possible to delete an account that has transactions. Archive it or delete the transactions first."
                    )
                }
            )

        instance.delete()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
