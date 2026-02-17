from django.views.generic.base import TemplateView
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Post
from .forms import PostForm


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
