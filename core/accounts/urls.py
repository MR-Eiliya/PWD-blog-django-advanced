from django.urls import path, include
from .views import AuthView, CustomLogoutView

app_name = "accounts"

urlpatterns = [
    # Website Authentication
    path("auth/", AuthView.as_view(), name="auth"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),

    # Accounts API V1
    path("api/v1/", include("accounts.api.v1.urls")),
]