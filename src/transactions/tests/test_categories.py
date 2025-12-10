from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from transactions.models import Category, Account, Transaction
from transactions.tests.helpers import create_user, authenticate_user, category_data


class CategoryCreationTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="testuser")
        self.client = authenticate_user(self.client, self.user)
        self.url = reverse("transactions:categories-list")

    def test_create_category_income_success(self):
        data = category_data(name="Salary", category_type="INCOME", color="#00FF00")
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Salary")
        self.assertEqual(response.data["type"], "INCOME")
        self.assertEqual(response.data["color"], "#00FF00")
        self.assertEqual(response.data["icon"], "mdi-home")

        # Verify it was saved in the database
        self.assertTrue(Category.objects.filter(user=self.user, name="Salary").exists())

    def test_create_category_expense_success(self):
        data = category_data(name="Food", category_type="EXPENSE", color="#FF0000")
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Food")
        self.assertEqual(response.data["type"], "EXPENSE")

    def test_create_category_with_custom_icon_and_color(self):
        data = category_data(name="Transport", icon="mdi-car", color="#0000FF")
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["icon"], "mdi-car")
        self.assertEqual(response.data["color"], "#0000FF")

    def test_create_category_without_authentication(self):
        self.client.credentials()
        data = category_data()
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_duplicate_category_same_type(self):
        data = category_data(name="Food", category_type="EXPENSE")

        response1 = self.client.post(self.url, data, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.client.post(self.url, data, format="json")
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response2.data)

    def test_create_duplicate_name_different_type(self):
        data_expense = category_data(name="Misc", category_type="EXPENSE")
        response1 = self.client.post(self.url, data_expense, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        data_income = category_data(name="Misc", category_type="INCOME")
        response2 = self.client.post(self.url, data_income, format="json")
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            Category.objects.filter(user=self.user, name="Misc").count(), 2
        )

    def test_create_category_invalid_color_format(self):
        invalid_colors = ["FF5733", "#FF57", "#GGGGGG", "red", "#FF57339"]

        for invalid_color in invalid_colors:
            data = category_data(color=invalid_color)
            response = self.client.post(self.url, data, format="json")
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"Color {invalid_color} should be rejected",
            )
            self.assertIn("color", response.data)

    def test_create_category_invalid_type(self):
        data = category_data()
        data["type"] = "INVALID_TYPE"
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)

    def test_create_category_auto_assigns_user(self):
        data = category_data(name="Auto User")
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        category = Category.objects.get(id=response.data["id"])
        self.assertEqual(category.user, self.user)

    def test_create_category_empty_icon_allowed(self):
        data = category_data(icon="")
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["icon"], "")

    def test_create_category_default_color(self):
        data = {"name": "Default Color", "type": "EXPENSE"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["color"], "#000000")


class CategoryListTests(APITestCase):
    def setUp(self):
        self.user1 = create_user(username="listuser1", email="listuser1@test.com")
        self.user2 = create_user(username="listuser2", email="listuser2@test.com")
        self.client = authenticate_user(self.client, self.user1)
        self.url = reverse("transactions:categories-list")

        Category.objects.create(
            user=self.user1, name="Food", type="EXPENSE", color="#FF0000"
        )
        Category.objects.create(
            user=self.user1, name="Salary", type="INCOME", color="#00FF00"
        )
        Category.objects.create(
            user=self.user1, name="Transport", type="EXPENSE", color="#0000FF"
        )

        Category.objects.create(
            user=self.user2, name="User2 Category", type="EXPENSE", color="#FFFFFF"
        )

    def test_list_only_own_categories(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 3)

        for category in results:
            self.assertNotEqual(category["name"], "User2 Category")

    def test_filter_by_type_income(self):
        response = self.client.get(self.url, {"type": "INCOME"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Salary")
        self.assertEqual(results[0]["type"], "INCOME")

    def test_filter_by_type_expense(self):
        response = self.client.get(self.url, {"type": "EXPENSE"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 2)

        names = [cat["name"] for cat in results]
        self.assertIn("Food", names)
        self.assertIn("Transport", names)

    def test_search_by_name(self):
        response = self.client.get(self.url, {"search": "Food"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Food")

    def test_user_isolation(self):
        self.client = authenticate_user(self.client, self.user2)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "User2 Category")

    def test_empty_list_for_new_user(self):
        new_user = create_user(username="newuser")
        self.client = authenticate_user(self.client, new_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 0)

    def test_ordering_by_name(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        names = [cat["name"] for cat in results]
        self.assertEqual(names, sorted(names))


class CategoryRetrieveTests(APITestCase):
    def setUp(self):
        self.user1 = create_user(
            username="retrieveuser1", email="retrieveuser1@test.com"
        )
        self.user2 = create_user(
            username="retrieveuser2", email="retrieveuser2@test.com"
        )
        self.client = authenticate_user(self.client, self.user1)

        self.category1 = Category.objects.create(
            user=self.user1, name="My Category", type="EXPENSE", color="#FF0000"
        )
        self.category2 = Category.objects.create(
            user=self.user2, name="Other Category", type="EXPENSE", color="#00FF00"
        )

    def test_retrieve_own_category(self):
        url = reverse("transactions:categories-detail", args=[self.category1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "My Category")
        self.assertEqual(response.data["color"], "#FF0000")

    def test_retrieve_other_user_category_fails(self):
        url = reverse("transactions:categories-detail", args=[self.category2.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CategoryUpdateTests(APITestCase):
    def setUp(self):
        self.user1 = create_user(username="updateuser1", email="updateuser1@test.com")
        self.user2 = create_user(username="updateuser2", email="updateuser2@test.com")
        self.client = authenticate_user(self.client, self.user1)

        self.category1 = Category.objects.create(
            user=self.user1,
            name="Old Name",
            type="EXPENSE",
            color="#FF0000",
            icon="mdi-old",
        )
        self.category2 = Category.objects.create(
            user=self.user2, name="Other Category", type="EXPENSE", color="#00FF00"
        )

    def test_update_category_name_icon_color(self):
        url = reverse("transactions:categories-detail", args=[self.category1.id])
        data = {
            "name": "New Name",
            "icon": "mdi-new",
            "color": "#0000FF",
            "type": "EXPENSE",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New Name")
        self.assertEqual(response.data["icon"], "mdi-new")
        self.assertEqual(response.data["color"], "#0000FF")

        # Verify in database
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, "New Name")

    def test_update_other_user_category_fails(self):
        url = reverse("transactions:categories-detail", args=[self.category2.id])
        data = {"name": "Hacked", "type": "EXPENSE", "color": "#000000"}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_to_duplicate_name_fails(self):
        Category.objects.create(
            user=self.user1, name="Existing", type="EXPENSE", color="#FFFFFF"
        )

        url = reverse("transactions:categories-detail", args=[self.category1.id])
        data = {"name": "Existing", "type": "EXPENSE", "color": "#FF0000"}
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_partial_update_patch(self):
        url = reverse("transactions:categories-detail", args=[self.category1.id])
        data = {"color": "#AABBCC"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["color"], "#AABBCC")
        self.assertEqual(response.data["name"], "Old Name")  # Name unchanged

    def test_full_update_put(self):
        url = reverse("transactions:categories-detail", args=[self.category1.id])
        data = {
            "name": "Completely New",
            "icon": "mdi-brand-new",
            "color": "#123456",
            "type": "INCOME",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Completely New")
        self.assertEqual(response.data["type"], "INCOME")


class CategoryDeleteTests(APITestCase):
    def setUp(self):
        self.user1 = create_user(username="deleteuser1", email="deleteuser1@test.com")
        self.user2 = create_user(username="deleteuser2", email="deleteuser2@test.com")
        self.client = authenticate_user(self.client, self.user1)

        self.category_no_transactions = Category.objects.create(
            user=self.user1, name="Empty Category", type="EXPENSE", color="#FF0000"
        )

        self.category_with_transactions = Category.objects.create(
            user=self.user1, name="Used Category", type="EXPENSE", color="#00FF00"
        )

        self.account = Account.objects.create(
            user=self.user1,
            name="Test Account",
            account_type="CHECKING",
            initial_balance=1000,
            closing_day=1,
            due_day=10,
        )

        Transaction.objects.create(
            user=self.user1,
            account=self.account,
            category=self.category_with_transactions,
            description="Test Transaction",
            value=100,
            date="2024-01-01",
            type="EXPENSE",
        )

        self.category_other_user = Category.objects.create(
            user=self.user2, name="Other User Category", type="EXPENSE", color="#0000FF"
        )

    def test_delete_category_without_transactions(self):
        url = reverse(
            "transactions:categories-detail", args=[self.category_no_transactions.id]
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Category.objects.filter(id=self.category_no_transactions.id).exists()
        )

    def test_delete_category_with_transactions_fails(self):
        url = reverse(
            "transactions:categories-detail", args=[self.category_with_transactions.id]
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

        self.assertTrue(
            Category.objects.filter(id=self.category_with_transactions.id).exists()
        )

    def test_delete_other_user_category_fails(self):
        url = reverse(
            "transactions:categories-detail", args=[self.category_other_user.id]
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(
            Category.objects.filter(id=self.category_other_user.id).exists()
        )


class CategoryEdgeCaseTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="testuser")
        self.client = authenticate_user(self.client, self.user)
        self.url = reverse("transactions:categories-list")

    def test_max_length_name_50_chars(self):
        data = category_data(name="A" * 50)
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = category_data(name="B" * 51)
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_max_length_icon_50_chars(self):
        data = category_data(icon="i" * 50)
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = category_data(name="Icon Test 2", icon="j" * 51)
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_color_exactly_7_chars(self):
        valid_colors = ["#000000", "#FFFFFF", "#AbCdEf", "#123456"]
        for idx, color in enumerate(valid_colors):
            data = category_data(name=f"Color Test {idx}", color=color)
            response = self.client.post(self.url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_empty_icon_allowed(self):
        data = category_data(icon="")
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_missing_required_fields(self):
        data = {"type": "EXPENSE", "color": "#FF0000"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

        data = {"name": "Test", "color": "#FF0000"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)
