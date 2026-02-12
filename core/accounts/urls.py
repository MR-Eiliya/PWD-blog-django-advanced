from django.urls import path
from .views import AuthView, CustomLogoutView

app_name = "accounts"

urlpatterns = [
    path("auth/", AuthView.as_view(), name="auth"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
]