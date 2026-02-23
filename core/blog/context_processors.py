from .models import Post

def recent_posts(request):
    return {
        "recent_sidebar": Post.objects.filter(status=True).order_by("-published_date")[:4]
    }