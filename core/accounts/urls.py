from django.urls import path, include
from .views import AuthView, CustomLogoutView, profile_view, edit_profile_view
app_name = "accounts"

urlpatterns = [
    # Website Authentication
    path("auth/", AuthView.as_view(), name="auth"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", edit_profile_view, name="edit-profile"),
    # Accounts API V1
    path("api/v1/", include("accounts.api.v1.urls")),
]
