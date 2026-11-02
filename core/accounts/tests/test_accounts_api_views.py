import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


# Test successful user registration
@pytest.mark.django_db
@patch("accounts.api.v1.views.EmailThread.start")
def test_registration_api_success(mock_email):
    client = APIClient()

    response = client.post(
    "/accounts/api/v1/registration/",
    {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "StrongPass123!",
        "password1": "StrongPass123!",
    },
    format="json",
)

    assert response.status_code == 201
    assert response.data["email"] == "newuser@example.com"
    assert User.objects.filter(email="newuser@example.com").exists()
    mock_email.assert_called_once()




# Test that registration fails when email already exists
@pytest.mark.django_db
def test_registration_api_duplicate_email():
    User.objects.create_user(
        email="existing@example.com",
        username="existinguser",
        password="StrongPass123!",
    )

    client = APIClient()

    response = client.post(
        "/accounts/api/v1/registration/",
        {
            "email": "existing@example.com",
            "username": "newuser",
            "password": "StrongPass123!",
            "password1": "StrongPass123!",
        },
        format="json",
    )

    assert response.status_code == 400
    assert not User.objects.filter(username="newuser").exists()



# Test that registration fails when passwords do not match
@pytest.mark.django_db
def test_registration_api_password_mismatch():
    client = APIClient()

    response = client.post(
        "/accounts/api/v1/registration/",
        {
            "email": "mismatch@example.com",
            "username": "mismatchuser",
            "password": "StrongPass123!",
            "password1": "DifferentPass123!",
        },
        format="json",
    )

    assert response.status_code == 400
    assert not User.objects.filter(email="mismatch@example.com").exists()




# Test successful token login
@pytest.mark.django_db
def test_token_login_api_success():
    User.objects.create_user(
        email="login@example.com",
        username="loginuser",
        password="StrongPass123!",
        is_verified=True,
    )

    client = APIClient()

    response = client.post(
        "/accounts/api/v1/token/login",
        {
            "email": "login@example.com",
            "password": "StrongPass123!",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "token" in response.data
    assert response.data["email"] == "login@example.com"



# Test that unverified users cannot log in
@pytest.mark.django_db
def test_token_login_api_unverified_user():
    User.objects.create_user(
        email="unverified@example.com",
        username="unverifieduser",
        password="StrongPass123!",
        is_verified=False,
    )

    client = APIClient()

    response = client.post(
        "/accounts/api/v1/token/login",
        {
            "email": "unverified@example.com",
            "password": "StrongPass123!",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "token" not in response.data




# Test that login fails with an incorrect password
@pytest.mark.django_db
def test_token_login_api_invalid_password():
    User.objects.create_user(
        email="wrongpass@example.com",
        username="wrongpassuser",
        password="StrongPass123!",
        is_verified=True,
    )

    client = APIClient()

    response = client.post(
        "/accounts/api/v1/token/login",
        {
            "email": "wrongpass@example.com",
            "password": "WrongPass123!",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "token" not in response.data


# Test successful token logout
@pytest.mark.django_db
def test_token_logout_api_success():
    user = User.objects.create_user(
        email="logout@example.com",
        username="logoutuser",
        password="StrongPass123!",
        is_verified=True,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=user)

    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    response = client.post("/accounts/api/v1/token/logout")

    assert response.status_code == 204
    assert not Token.objects.filter(user=user).exists()



# Test that unauthenticated users cannot log out
@pytest.mark.django_db
def test_token_logout_api_unauthenticated():
    client = APIClient()

    response = client.post("/accounts/api/v1/token/logout")

    assert response.status_code in [401, 403]


# Test successful password change
@pytest.mark.django_db
def test_change_password_api_success():
    user = User.objects.create_user(
        email="change@example.com",
        username="changeuser",
        password="OldPass123!",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.put(
        "/accounts/api/v1/change-password/",
        {
            "old_password": "OldPass123!",
            "new_password": "NewPass123!",
            "new_password1": "NewPass123!",
        },
        format="json",
    )

    user.refresh_from_db()

    assert response.status_code == 200
    assert user.check_password("NewPass123!")




# Test password change with an incorrect old password
@pytest.mark.django_db
def test_change_password_api_invalid_old_password():
    user = User.objects.create_user(
        email="wrongold@example.com",
        username="wrongolduser",
        password="OldPass123!",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.put(
        "/accounts/api/v1/change-password/",
        {
            "old_password": "WrongOldPass123!",
            "new_password": "NewPass123!",
            "new_password1": "NewPass123!",
        },
        format="json",
    )

    user.refresh_from_db()

    assert response.status_code == 400
    assert user.check_password("OldPass123!")



# Test retrieving the authenticated user's profile
@pytest.mark.django_db
def test_profile_api_get_success():
    user = User.objects.create_user(
        email="profile@example.com",
        username="profileuser",
        password="Pass123!",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/accounts/api/v1/profile/")

    assert response.status_code == 200
    assert response.data["email"] == user.email



# Test updating the authenticated user's profile
@pytest.mark.django_db
def test_profile_api_update_success():
    user = User.objects.create_user(
        email="update@example.com",
        username="updateuser",
        password="Pass123!",
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        "/accounts/api/v1/profile/",
        {
            "first_name": "Ilya",
            "last_name": "Sharifi",
            "description": "Python Developer",
        },
        format="json",
    )

    user.profile.refresh_from_db()

    assert response.status_code == 200
    assert user.profile.first_name == "Ilya"
    assert user.profile.last_name == "Sharifi"



# Test successful account activation
@pytest.mark.django_db
def test_activation_api_success():
    import jwt
    from django.conf import settings
    from rest_framework_simplejwt.tokens import RefreshToken

    user = User.objects.create_user(
        email="activation@example.com",
        username="activationuser",
        password="Pass123!",
    )

    token = str(RefreshToken.for_user(user).access_token)

    client = APIClient()
    response = client.get(
        f"/accounts/api/v1/activation/confirm/{token}"
    )

    user.refresh_from_db()

    assert response.status_code == 200
    assert user.is_verified is True


# Test successful password reset request
@pytest.mark.django_db
@patch("accounts.api.v1.views.EmailThread.start")
def test_password_reset_request_api_success(mock_email):
    user = User.objects.create_user(
        email="reset@example.com",
        username="resetuser",
        password="Pass123!",
    )

    client = APIClient()
    response = client.post(
        "/accounts/api/v1/password-reset/",
        {"email": user.email},
        format="json",
    )

    assert response.status_code == 200
    mock_email.assert_called_once()



    
# Test successful password reset confirmation
@pytest.mark.django_db
def test_set_new_password_api_success():
    import jwt
    from django.conf import settings
    from django.utils import timezone
    from datetime import timedelta

    user = User.objects.create_user(
        email="newpass@example.com",
        username="newpassuser",
        password="OldPass123!",
    )

    payload = {
        "user_id": user.pk,
        "password_reset_at": None,
        "exp": timezone.now() + timedelta(minutes=15),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    client = APIClient()
    response = client.post(
        f"/accounts/api/v1/password-reset/confirm/{token}/",
        {
            "new_password": "NewPass123!",
            "new_password1": "NewPass123!",
        },
        format="json",
    )

    user.refresh_from_db()

    assert response.status_code == 200
    assert user.check_password("NewPass123!")