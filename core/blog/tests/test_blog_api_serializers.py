import pytest
from blog.models import Category
from accounts.models import CustomUser
from blog.api.v1.serializers import CategorySerializer
from django.utils import timezone



# Test category serializer representation
@pytest.mark.django_db
def test_category_serializer():
    category = Category.objects.create(name="Python")

    serializer = CategorySerializer(category)

    assert serializer.data["name"] == "Python"
    assert serializer.data["id"] == category.id



from rest_framework.test import APIRequestFactory
from blog.models import Post, Category
from blog.api.v1.serializers import PostSerializer


# Test post serializer list representation
@pytest.mark.django_db
def test_post_serializer_list():
    user = CustomUser.objects.create_user(
    username="testuser",
    email="test@example.com",
    password="testpass123"
    )
    
    post = Post.objects.create(
        author=user.profile,
        title="Django Testing",
        content="Learn Django REST Framework",
        status=True,
        published_date=timezone.now(),
    )

    request = APIRequestFactory().get("/blog/api/v1/posts/")
    request.parser_context = {"kwargs": {}}

    serializer = PostSerializer(
        post,
        context={"request": request}
    )

    assert serializer.data["title"] == "Django Testing"
    assert serializer.data["snippet"] == "Learn"
    assert "content" not in serializer.data


# Test post serializer detail representation
@pytest.mark.django_db
def test_post_serializer_detail():
    user = CustomUser.objects.create_user(
        username="detailuser",
        email="detail@example.com",
        password="testpass123"
    )
    post = Post.objects.create(
        author=user.profile,
        title="Django Testing",
        content="Learn Django REST Framework",
        status=True,
        published_date=timezone.now(),
    )

    request = APIRequestFactory().get(f"/blog/api/v1/posts/{post.pk}/")
    request.parser_context = {"kwargs": {"pk": post.pk}}

    serializer = PostSerializer(
        post,
        context={"request": request}
    )

    assert serializer.data["content"] == "Learn Django REST Framework"
    assert "snippet" not in serializer.data
    assert "relative_url" not in serializer.data
    assert "absolute_url" not in serializer.data