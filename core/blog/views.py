from django.views.generic.base import TemplateView
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Post, Category, Comment
from accounts.models import Profile
from .forms import PostForm, CommentForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.mixins import UserPassesTestMixin



User = get_user_model()

class PostListView(ListView):
    model = Post
    context_object_name = "posts"
    paginate_by = 6
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
        context["comments"] = self.object.comment_set.all()
        context["form"] = CommentForm()
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



class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/post_detail.html"


    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.post = post
        #form.instance.approved = False
        form.save()
        return redirect(self.get_success_url())
    

    def get_success_url(self):
        return reverse_lazy('blog:post-detail', kwargs={'pk': self.kwargs['pk']})
    

    def form_invalid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        #comments = post.comment_set.filter(approved=True)
        comments = post.comment_set.all()
        return render(self.request, self.template_name, {
            'post': post,
            'form': form,
            'comments': comments,
        })


class CommentReplyView(UserPassesTestMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/post_detail.html"


    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        parent_comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        form.instance.parent = parent_comment
        form.instance.post = parent_comment.post
        form.instance.name = self.request.user.username
        form.instance.email = self.request.user.email
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.post.get_absolute_url()
    