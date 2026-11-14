from celery import shared_task
from .models import Post


@shared_task
def test_background_task():
    return "Background task executed successfully!"


@shared_task
def delete_latest_posts():
    latest_post_ids = list(
        Post.objects.order_by("-created_date")
        .values_list("id", flat=True)[:2]
    )

    deleted_count, _ = Post.objects.filter(
        id__in=latest_post_ids
    ).delete()

    return f"{deleted_count} objects deleted successfully."