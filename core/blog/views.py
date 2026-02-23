from django.views.generic.base import TemplateView
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Post, Category
from accounts.models import Profile
from .forms import PostForm
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class PostListView(ListView):
    model = Post
    context_object_name = "posts"
    paginate_by = 4
    ordering = "published_date"
    template_name = "blog/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hero_blog"] = (
            "A blog for ideas, experiments, and real experiences shaped along the way. It’s where thoughts turn into structure, and details actually matter. Some posts dive deep, some stay simple but all of them come from doing the work."
        )

        return context


class PostDetailView(DetailView):
    model = Post
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context
    

# api

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    success_url = "/blog/post"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    

class PostEditView(UpdateView):
    model = Post
    success_url = "/blog/post"


class PostDeleteView(DeleteView):
    model = Post
    success_url = "/blog/post"


class CategoryPostListView(ListView):
    model = Post
    template_name = "blog/home.html"
    context_object_name = "posts"

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs["category_slug"]
        )
        return Post.objects.filter(category=self.category, status=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context
    

class AuthorPostListView(ListView):
    model = Post
    template_name = "blog/home.html"
    context_object_name = "posts"

    def get_queryset(self):
        self.author = get_object_or_404(Profile, id=self.kwargs["author_id"])
        return Post.objects.filter(author=self.author, status=True)
    

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context["author"] = self.author
        context["categories"] = Category.objects.all()
        return context
    
class PostSearchListView(ListView):
    model = Post
    template_name = "blog/home.html"
    context_object_name = "posts"
    paginate_by = 4

    def get_queryset(self):
        query = self.request.GET.get("q")

        queryset = Post.objects.filter(status=True).order_by("-published_date")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            )

        return queryset