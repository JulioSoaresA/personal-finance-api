from django.urls import path
from authentication.views import (
    LoginView, CustomRefreshTokenView, logout, RegisterView
)

app_name = 'authentication'


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout, name='logout'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
]