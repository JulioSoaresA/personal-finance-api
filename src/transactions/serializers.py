from rest_framework import serializers
from transactions.models import Transaction, Category, Account


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "icon", "color", "type"]


class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "icon", "color", "type"]
        read_only_fields = ["id"]

    def validate_color(self, value):
        import re

        if not re.match(r"^#[0-9A-Fa-f]{6}$", value):
            raise serializers.ValidationError(
                "Cor deve estar no formato HEX (#RRGGBB). Exemplo: #FF5733"
            )
        return value

    def validate(self, data):
        user = self.context["request"].user
        name = data.get("name")
        category_type = data.get("type")

        queryset = Category.objects.filter(user=user, name=name, type=category_type)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                {
                    "name": f"Você já possui uma categoria '{name}' do tipo {category_type}."
                }
            )

        return data


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "account_type"]


class TransactionCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    account_id = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(), source="account", write_only=True
    )
    installment_total = serializers.IntegerField(
        required=False, min_value=2, write_only=True
    )
    installment_value = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        write_only=True,
        help_text="Informe se já souber o valor exato da parcela (com juros)",
    )

    class Meta:
        model = Transaction
        fields = [
            "description",
            "value",
            "date",
            "account",
            "account_id",
            "category",
            "category_id",
            "type",
            "paid",
            "installment_total",
            "installment_value",
            "notes",
        ]

    def validate(self, data):
        user = self.context["request"].user
        if data.get("category") and data["category"].user != user:
            raise serializers.ValidationError({"category_id": "Categoria inválida."})
        if data["account"].user != user:
            raise serializers.ValidationError({"account_id": "Conta inválida."})

        installments = data.get("installment_total")
        inst_value = data.get("installment_value")
        total_value = data.get("value")

        if inst_value and not installments:
            raise serializers.ValidationError(
                {
                    "installment_total": "Necessário informar o número de parcelas quando o valor da parcela é fixado."
                }
            )

        if not total_value and not inst_value:
            raise serializers.ValidationError(
                "Informe o 'value' (total) ou 'installment_value'."
            )

        return data


class TransactionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    account = AccountSerializer(read_only=True)

    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "description",
            "value",
            "date",
            "formatted_date",
            "paid",
            "type",
            "category",
            "account",
            "installment_current",
            "installment_total",
            "installment_group_id",
            "notes",
        ]

    def get_formatted_date(self, obj):
        return obj.date.strftime("%d/%m/%Y")


class CategoryChartDataSerializer(serializers.Serializer):
    category_name = serializers.CharField()
    color = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


class DashboardSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)

    chart_data = CategoryChartDataSerializer(many=True, required=False)


class AccountListSerializer(serializers.ModelSerializer):
    current_balance = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Account
        fields = [
            "id",
            "name",
            "account_type",
            "initial_balance",
            "current_balance",
            "closing_day",
            "due_day",
        ]


class AccountWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "name",
            "account_type",
            "initial_balance",
            "closing_day",
            "due_day",
        ]

    def validate(self, data):
        if data.get("account_type") == "CREDIT_CARD":
            if not data.get("closing_day") or not data.get("due_day"):
                raise serializers.ValidationError(
                    "Para Cartão de Crédito, os dias de fechamento e vencimento são obrigatórios."
                )
        return data
