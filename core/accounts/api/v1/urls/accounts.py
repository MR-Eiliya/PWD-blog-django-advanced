from django.urls import path
from .. import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    # Registration
    path("registration/", views.RegistrationAPIView.as_view(), name="registration"),
    # Activation
    path(
        "activation/confirm/<str:token>",
        views.ActivationAPIView.as_view(),
        name="activation",
    ),
    # Resend Activision
    path(
        "activation/resend/",
        views.ActivationResendAPIView.as_view(),
        name="activision-resend",
    ),
    # Password Changing
    path(
        "change-password/",
        views.ChangePasswordAPIView.as_view(),
        name="change-password",
    ),
    # Password reset
    path(
        "password-reset/",
        views.PasswordResetRequestAPIView.as_view(),
        name="password-reset",
    ),
    path(
        "password-reset/confirm/<str:token>/",
        views.SetNewPasswordAPIView.as_view(),
        name="password-reset-confirm",
    ),
    # Login Token
    path("token/login", views.CustomObtainAuthToken.as_view(), name="token-login"),
    path("token/logout", views.CustomDiscardAuthToken.as_view(), name="token-logout"),
    # JWT Login
    path("jwt/create/", views.CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),

]




