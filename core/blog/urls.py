from django.urls import path, include
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="home"),
    # api
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("post/create/", views.PostCreateView.as_view(), name="post-create"),
    path("post/<int:pk>/edit/", views.PostEditView.as_view(), name="post-edit"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post-delete"),
    path('category/<slug:category_slug>/', views.CategoryPostListView.as_view(), name='category-posts'),
    path('author/<int:author_id>/', views.AuthorPostListView.as_view(), name="author-posts"),
    path('post/search/', views.PostSearchListView.as_view(), name="post-search"),
    

]
