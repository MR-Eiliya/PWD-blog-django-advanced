from . import views
from rest_framework.routers import SimpleRouter
from django.urls import path

app_name = "api-v1"

router = SimpleRouter()
router.register("posts", 
                views.PostModelViewSet, 
                basename="post")

router.register("categories", 
                views.CategoryModelViewSet, 
                basename="category")

urlpatterns = router.urls + [
    path(
        "technology-news/",
        views.TechnologyNewsAPIView.as_view(),
        name="technology-news",
    ),
]