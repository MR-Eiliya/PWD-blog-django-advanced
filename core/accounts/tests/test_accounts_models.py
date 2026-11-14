import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from accounts.models import Profile

User = get_user_model()



# Test successful user creation with valid credentials
@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        email="example@example.com",
        username="testuser",
        password="StrongPass123!",
    )

    assert user.email == "example@example.com"
    assert user.username == "testuser"
    assert user.check_password("StrongPass123!")



# Test that creating a user without an email raises ValueError
@pytest.mark.django_db
def test_create_user_without_email():
    with pytest.raises(ValueError, match="The Email must be set"):
        User.objects.create_user(
            email="",
            username="testuser",
            password="StrongPass123!",
        )



# Test that creating a user without a username raises ValueError
@pytest.mark.django_db
def test_create_user_without_username():
    with pytest.raises(ValueError, match="The Username must be set"):
        User.objects.create_user(
            email="test@example.com",
            username="",
            password="StrongPass123!",
        )



# Test successful superuser creation with required permissions
@pytest.mark.django_db
def test_create_superuser():
    admin = User.objects.create_superuser(
        email="admin@example.com",
        username="admin",
        password="StrongPass123!",
    )

    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.is_active is True
    assert admin.is_verified is True
    assert admin.check_password("StrongPass123!")



# Test that duplicate email addresses are not allowed
@pytest.mark.django_db
def test_create_user_with_duplicate_email():
    User.objects.create_user(
        email="example@example.com",
        username="user1",
        password="StrongPass123!",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            User.objects.create_user(
                email="example@example.com",
                username="user2",
                password="StrongPass123!",
            )


# Test that duplicate usernames are not allowed
@pytest.mark.django_db
def test_create_user_with_duplicate_username():
    User.objects.create_user(
        email="first@example.com",
        username="testuser",
        password="StrongPass123!",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            User.objects.create_user(
                email="second@example.com",
                username="testuser",
                password="StrongPass123!",
            )


# Test that the string representation of a user returns their email
@pytest.mark.django_db
def test_user_str():
    user = User.objects.create_user(
        email="example@example.com",
        username="testuser",
        password="StrongPass123!",
    )

    assert str(user) == "example@example.com"




# Test that a profile is automatically created when a user is created
@pytest.mark.django_db
def test_profile_created_automatically():
    user = User.objects.create_user(
        email="profile@example.com",
        username="profileuser",
        password="StrongPass123!",
    )

    assert hasattr(user, "profile")
    assert user.profile.user == user



# Test that a user cannot have more than one profile
@pytest.mark.django_db
def test_user_cannot_have_multiple_profiles():
    user = User.objects.create_user(
        email="profile@example.com",
        username="profileuser",
        password="StrongPass123!",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Profile.objects.create(user=user)



# Test that the string representation of a profile returns the user's email
@pytest.mark.django_db
def test_profile_str():
    user = User.objects.create_user(
        email="profile@example.com",
        username="profileuser",
        password="StrongPass123!",
    )

    assert str(user.profile) == "profile@example.com"