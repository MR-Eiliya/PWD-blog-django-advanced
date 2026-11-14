import pytest
from django.utils import timezone
from accounts.models import CustomUser
from blog.models import Post, Category, Comment


# Test successful post creation
@pytest.mark.django_db
def test_post_creation():
    user = CustomUser.objects.create_user(
        email="post@example.com",
        username="postuser",
        password="Pass123!",
    )

    post = Post.objects.create(
        author=user.profile,
        title="Test Post",
        content="This is a test content",
        status=True,
        published_date=timezone.now(),
    )

    assert post.title == "Test Post"
    assert post.author == user.profile
    assert str(post) == "Test Post"



# Test post snippet generation
@pytest.mark.django_db
def test_post_get_snippet():
    user = CustomUser.objects.create_user(
        email="snippet@example.com",
        username="snippetuser",
        password="Pass123!",
    )

    post = Post.objects.create(
        author=user.profile,
        title="Snippet Test",
        content="Hello World",
        status=True,
        published_date=timezone.now(),
    )

    assert post.get_snippet() == "Hello"



# Test automatic category slug generation
@pytest.mark.django_db
def test_category_slug_generation():
    category = Category.objects.create(name="Web Development")

    assert category.slug == "web-development"
    assert str(category) == "Web Development"



# Test category URL generation for a post
@pytest.mark.django_db
def test_post_category_url():
    user = CustomUser.objects.create_user(
        email="category@example.com",
        username="categoryuser",
        password="Pass123!",
    )

    category = Category.objects.create(name="Python")

    post = Post.objects.create(
        author=user.profile,
        title="Python Tutorial",
        content="Python content",
        status=True,
        category=category,
        published_date=timezone.now(),
    )

    assert post.category_url() == f"/blog/category/{category.slug}/"




# Test comment and reply relationship
@pytest.mark.django_db
def test_comment_reply_relationship():
    user = CustomUser.objects.create_user(
        email="comment@example.com",
        username="commentuser",
        password="Pass123!",
    )

    post = Post.objects.create(
        author=user.profile,
        title="Comment Test",
        content="Post content",
        status=True,
        published_date=timezone.now(),
    )

    comment = Comment.objects.create(
        post=post,
        name="Parent Comment",
        email="parent@example.com",
        message="This is a parent comment",
    )

    reply = Comment.objects.create(
        post=post,
        name="Reply",
        email="reply@example.com",
        message="This is a reply",
        parent=comment,
    )

    assert reply.parent == comment
    assert comment.replies.first() == reply



# Test cascading deletion of post and its comments
@pytest.mark.django_db
def test_post_cascade_delete():
    user = CustomUser.objects.create_user(
        email="cascade@example.com",
        username="cascadeuser",
        password="Pass123!",
    )

    post = Post.objects.create(
        author=user.profile,
        title="Cascade Test",
        content="Post content",
        status=True,
        published_date=timezone.now(),
    )

    comment = Comment.objects.create(
        post=post,
        name="Test Comment",
        email="comment@example.com",
        message="Comment content",
    )

    post.delete()

    assert not Post.objects.filter(pk=post.pk).exists()
    assert not Comment.objects.filter(pk=comment.pk).exists()