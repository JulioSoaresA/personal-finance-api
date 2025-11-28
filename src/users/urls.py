from django.urls import path

from users.views import UserListView, UserProfileView

app_name = "users"


urlpatterns = [
    path("user_list/", UserListView.as_view({"get": "list"}), name="user_list"),
    path("profile/", UserProfileView.as_view({"get": "retrieve"}), name="user_profile"),
]
