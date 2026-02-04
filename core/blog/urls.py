from django.urls import path, include
from . import views

app_name = "blog"

urlpatterns = [
    path("posts", views.PostListView.as_view(), name="post-list"),
    # api
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("post/create/", views.PostCreateView.as_view(), name="post-create"),
    path("post/<int:pk>/edit/", views.PostEditView.as_view(), name="post-edit"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post-delete"),
]
