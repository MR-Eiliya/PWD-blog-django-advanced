from django.urls import path, include
from . import views

app_name = "blog"

urlpatterns = [
    path("",name="index"),
    path("post", name="post-list"),
    # api

    path("post/<int:pk>/", name="post-detail"),
    path("post/create/", name="post-create"),
    path("post/<int:pk>/edit/", name="post-edit"),
    path("post/<int:pk>/delete/", name="post-delete"),
    

]
