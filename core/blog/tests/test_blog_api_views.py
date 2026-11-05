import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from accounts.models import CustomUser
from blog.models import Post, Category
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO


# Test listing published posts
@pytest.mark.django_db
def test_post_list_api():
    user = CustomUser.objects.create_user(
        username="author",
        email="author@example.com",
        password="testpass123"
    )

    Post.objects.create(
        author=user.profile,
        title="Published Post",
        content="Published content",
        status=True,
        published_date=timezone.now()
    )

    Post.objects.create(
        author=user.profile,
        title="Draft Post",
        content="Draft content",
        status=False,
        published_date=timezone.now()
    )

    client = APIClient()
    response = client.get("/blog/api/v1/posts/")

    assert response.status_code == 200
    assert response.data["total_objects"] == 1
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["title"] == "Published Post"



# Test creating a post by a staff user
@pytest.mark.django_db
def test_create_post_api():
    user = CustomUser.objects.create_user(
        username="staffuser",
        email="staff@example.com",
        password="testpass123",
        is_staff=True
    )

    image_file = BytesIO()
    Image.new("RGB", (100, 100)).save(image_file, format="JPEG")
    image_file.seek(0)

    image = SimpleUploadedFile(
        "test.jpg",
        image_file.read(),
        content_type="image/jpeg"
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/blog/api/v1/posts/",
        {
            "title": "New API Post",
            "content": "Post created through API",
            "status": True,
            "published_date": timezone.now().isoformat(),
            "image": image,
        },
        format="multipart"
    )

    assert response.status_code == 201
    assert Post.objects.filter(title="New API Post").exists()
    assert Post.objects.get(title="New API Post").author == user.profile



# Test preventing non-owner from updating a post
@pytest.mark.django_db
def test_non_owner_cannot_update_post():
    author = CustomUser.objects.create_user(
        username="author",
        email="author@example.com",
        password="testpass123"
    )

    other_user = CustomUser.objects.create_user(
        username="other",
        email="other@example.com",
        password="testpass123"
    )

    post = Post.objects.create(
        author=author.profile,
        title="Original Title",
        content="Original Content",
        status=True,
        published_date=timezone.now()
    )

    client = APIClient()
    client.force_authenticate(user=other_user)

    response = client.patch(
        f"/blog/api/v1/posts/{post.pk}/",
        {"title": "Updated Title"},
        format="json"
    )

    post.refresh_from_db()

    assert response.status_code == 403
    assert post.title == "Original Title"



# Test preventing non-admin users from creating categories
@pytest.mark.django_db
def test_non_admin_cannot_create_category():
    user = CustomUser.objects.create_user(
        username="normaluser",
        email="normal@example.com",
        password="testpass123"
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/blog/api/v1/categories/",
        {"name": "New Category"},
        format="json"
    )

    assert response.status_code == 403
    assert not Category.objects.filter(name="New Category").exists()



# Test allowing the owner to update their post
@pytest.mark.django_db
def test_owner_can_update_post():
    user = CustomUser.objects.create_user(
        username="owner",
        email="owner@example.com",
        password="testpass123"
    )

    post = Post.objects.create(
        author=user.profile,
        title="Original Title",
        content="Original Content",
        status=True,
        published_date=timezone.now()
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.patch(
        f"/blog/api/v1/posts/{post.pk}/",
        {"title": "Updated Title"},
        format="json"
    )

    post.refresh_from_db()

    assert response.status_code == 200
    assert post.title == "Updated Title"



# Test allowing the owner to delete their post
@pytest.mark.django_db
def test_owner_can_delete_post():
    user = CustomUser.objects.create_user(
        username="deleteowner",
        email="delete@example.com",
        password="testpass123"
    )

    post = Post.objects.create(
        author=user.profile,
        title="Post to Delete",
        content="This post will be deleted",
        status=True,
        published_date=timezone.now()
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.delete(
        f"/blog/api/v1/posts/{post.pk}/"
    )

    assert response.status_code == 204
    assert not Post.objects.filter(pk=post.pk).exists()



# Test preventing non-staff users from creating posts
@pytest.mark.django_db
def test_non_staff_cannot_create_post():
    user = CustomUser.objects.create_user(
        username="normaluser",
        email="normal@example.com",
        password="testpass123"
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/blog/api/v1/posts/",
        {
            "title": "Unauthorized Post",
            "content": "This post should not be created",
            "status": True,
            "published_date": timezone.now().isoformat(),
        },
        format="json"
    )

    assert response.status_code == 403
    assert not Post.objects.filter(title="Unauthorized Post").exists()