import pytest
from accounts.api.v1.serializers import RegistrationSerializer


# Test successful user registration with valid data
@pytest.mark.django_db
def test_registration_serializer_valid_data():
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "StrongPass123!",
        "password1": "StrongPass123!",
    }

    serializer = RegistrationSerializer(data=data)

    assert serializer.is_valid(), serializer.errors

    user = serializer.save()

    assert user.email == data["email"]
    assert user.username == data["username"]
    assert user.check_password(data["password"])



# Test that registration fails when passwords do not match
@pytest.mark.django_db
def test_registration_serializer_password_mismatch():
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "StrongPass123!",
        "password1": "DifferentPass123!",
    }

    serializer = RegistrationSerializer(data=data)

    assert not serializer.is_valid()
    assert "detail" in serializer.errors



# Test that registration fails when password is weak
@pytest.mark.django_db
def test_registration_serializer_weak_password():
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "123",
        "password1": "123",
    }

    serializer = RegistrationSerializer(data=data)

    assert not serializer.is_valid()
    assert "password" in serializer.errors



from accounts.api.v1.serializers import CustomAuthTokenSerializer


# Test successful authentication with valid credentials
@pytest.mark.django_db
def test_auth_token_serializer_valid_credentials():
    from django.contrib.auth import get_user_model

    User = get_user_model()

    User.objects.create_user(
        email="login@example.com",
        username="loginuser",
        password="StrongPass123!",
        is_verified=True,
    )

    data = {
        "email": "login@example.com",
        "password": "StrongPass123!",
    }

    serializer = CustomAuthTokenSerializer(data=data)

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["user"].email == "login@example.com"



# Test that unverified users cannot authenticate
@pytest.mark.django_db
def test_auth_token_serializer_unverified_user():
    from django.contrib.auth import get_user_model

    User = get_user_model()

    User.objects.create_user(
        email="unverified@example.com",
        username="unverified",
        password="StrongPass123!",
        is_verified=False,
    )

    data = {
        "email": "unverified@example.com",
        "password": "StrongPass123!",
    }

    serializer = CustomAuthTokenSerializer(data=data)

    assert not serializer.is_valid()
    assert "detail" in serializer.errors



# Test that users cannot authenticate with an incorrect password
@pytest.mark.django_db
def test_auth_token_serializer_invalid_password():
    from django.contrib.auth import get_user_model

    User = get_user_model()

    User.objects.create_user(
        email="wrongpass@example.com",
        username="wrongpass",
        password="StrongPass123!",
        is_verified=True,
    )

    data = {
        "email": "wrongpass@example.com",
        "password": "WrongPass123!",
    }

    serializer = CustomAuthTokenSerializer(data=data)

    assert not serializer.is_valid()



from accounts.api.v1.serializers import CustomTokenObtainPairSerializer


# Test JWT token generation for verified users
@pytest.mark.django_db
def test_custom_token_obtain_pair_serializer_verified_user():
    from django.contrib.auth import get_user_model

    User = get_user_model()

    user = User.objects.create_user(
        email="jwt@example.com",
        username="jwtuser",
        password="StrongPass123!",
        is_verified=True,
    )

    serializer = CustomTokenObtainPairSerializer(
        data={
            "email": user.email,
            "password": "StrongPass123!",
        }
    )

    assert serializer.is_valid(), serializer.errors
    assert "access" in serializer.validated_data
    assert "refresh" in serializer.validated_data
    assert serializer.validated_data["email"] == user.email
    assert serializer.validated_data["user_id"] == user.id



# Test that unverified users cannot obtain JWT tokens
@pytest.mark.django_db
def test_custom_token_obtain_pair_serializer_unverified_user():
    from django.contrib.auth import get_user_model
    from rest_framework.exceptions import ValidationError

    User = get_user_model()

    user = User.objects.create_user(
        email="unverified_jwt@example.com",
        username="unverified_jwt",
        password="StrongPass123!",
        is_verified=False,
    )

    serializer = CustomTokenObtainPairSerializer(
        data={
            "email": user.email,
            "password": "StrongPass123!",
        }
    )

    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)



from accounts.api.v1.serializers import ChangePasswordSerializer


# Test that password mismatch is rejected
def test_change_password_serializer_password_mismatch():
    data = {
        "old_password": "OldPass123!",
        "new_password": "NewPass123!",
        "new_password1": "DifferentPass123!",
    }

    serializer = ChangePasswordSerializer(data=data)

    assert not serializer.is_valid()
    assert "detail" in serializer.errors



# Test that weak new passwords are rejected
def test_change_password_serializer_weak_password():
    data = {
        "old_password": "OldPass123!",
        "new_password": "123",
        "new_password1": "123",
    }

    serializer = ChangePasswordSerializer(data=data)

    assert not serializer.is_valid()
    assert "new_password" in serializer.errors



# Test that profile data can be updated while email remains read-only
@pytest.mark.django_db
def test_profile_serializer_update():
    from django.contrib.auth import get_user_model
    from accounts.api.v1.serializers import ProfileSerializer
    from accounts.models import Profile

    User = get_user_model()
    user = User.objects.create_user(
        email="profile@example.com",
        username="profileuser",
        password="StrongPass123!",
    )

    profile = Profile.objects.get(user=user)

    serializer = ProfileSerializer(
        instance=profile,
        data={
            "email": "changed@example.com",
            "first_name": "Ilya",
            "last_name": "Sharifi",
            "description": "Backend Developer",
        },
        partial=True,
    )

    assert serializer.is_valid(), serializer.errors
    updated_profile = serializer.save()

    assert updated_profile.first_name == "Ilya"
    assert updated_profile.last_name == "Sharifi"
    assert updated_profile.description == "Backend Developer"
    assert updated_profile.user.email == "profile@example.com"



# Test that password mismatch is rejected
def test_set_new_password_serializer_password_mismatch():
    from accounts.api.v1.serializers import SetNewPasswordSerializer

    data = {
        "new_password": "NewPass123!",
        "new_password1": "DifferentPass123!",
    }

    serializer = SetNewPasswordSerializer(data=data)

    assert not serializer.is_valid()
    assert "detail" in serializer.errors



# Test that weak new passwords are rejected
def test_set_new_password_serializer_weak_password():
    from accounts.api.v1.serializers import SetNewPasswordSerializer

    data = {
        "new_password": "123",
        "new_password1": "123",
    }

    serializer = SetNewPasswordSerializer(data=data)

    assert not serializer.is_valid()
    assert "new_password" in serializer.errors


# Test that activation resend serializer accepts an unverified user
@pytest.mark.django_db
def test_activation_resend_serializer_valid_user():
    from django.contrib.auth import get_user_model
    from accounts.api.v1.serializers import ActivationResendSerializer

    User = get_user_model()
    User.objects.create_user(
        email="activation@example.com",
        username="activationuser",
        password="StrongPass123!",
        is_verified=False,
    )

    serializer = ActivationResendSerializer(
        data={"email": "activation@example.com"}
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["user"].email == "activation@example.com"



# Test that activation resend is rejected for verified users
@pytest.mark.django_db
def test_activation_resend_serializer_verified_user():
    from django.contrib.auth import get_user_model
    from accounts.api.v1.serializers import ActivationResendSerializer

    User = get_user_model()
    User.objects.create_user(
        email="verified@example.com",
        username="verifieduser",
        password="StrongPass123!",
        is_verified=True,
    )

    serializer = ActivationResendSerializer(
        data={"email": "verified@example.com"}
    )

    assert not serializer.is_valid()
    assert "detail" in serializer.errors



# Test that password reset request accepts an existing user's email
@pytest.mark.django_db
def test_password_reset_request_serializer_valid_email():
    from django.contrib.auth import get_user_model
    from accounts.api.v1.serializers import PasswordResetRequestSerializer

    User = get_user_model()
    User.objects.create_user(
        email="reset@example.com",
        username="resetuser",
        password="StrongPass123!",
    )

    serializer = PasswordResetRequestSerializer(
        data={"email": "reset@example.com"}
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["user"].email == "reset@example.com"