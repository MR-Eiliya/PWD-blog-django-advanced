from django.views.generic.base import TemplateView
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.views import View
from .models import Post, Category, Comment
from accounts.models import Profile
from .forms import PostForm, CommentForm, CommentReplyForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.mixins import (
    UserPassesTestMixin, LoginRequiredMixin
)

from django.urls import reverse

from django.http import JsonResponse
from django.template.loader import render_to_string



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
        form.instance.author = self.request.user.profile
        return super().form_valid(form)
    

class PostEditView(UpdateView, LoginRequiredMixin, UserPassesTestMixin):
    model = Post
    success_url = "/blog/post"
    form_class = PostForm


class PostDeleteView(DeleteView, LoginRequiredMixin, UserPassesTestMixin):
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
    form_class = CommentReplyForm
    template_name = "blog/comment_reply.html"


    def test_func(self):
        return self.request.user.is_staff
    

    def get_parent_comment(self):
        return get_object_or_404(Comment, pk=self.kwargs['parent_pk'])
    
    
    def get_post(self):
        return get_object_or_404(Post, pk=self.kwargs['post_pk'])
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        parent_comment = self.get_parent_comment()
        
        if 'initial' not in kwargs:
            kwargs['initial'] = {}
        
        kwargs['initial']['post'] = parent_comment.post
        kwargs['initial']['parent'] = parent_comment
        return kwargs
    

    def form_valid(self, form):
        parent_comment = self.get_parent_comment()
        post = self.get_post()
        
        form.instance.post = post
        form.instance.parent = parent_comment
        
        form.instance.name = self.request.user.username
        form.instance.email = self.request.user.email
        
        #form.instance.user = self.request.user
        
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':

            new_comment_data = {
                'pk': form.instance.pk,
                'name': form.instance.name,
                'text': form.instance.message,
                'created_date': form.instance.created_date.strftime('%Y-%m-%d %H:%M:%S'),
                'parent_pk': parent_comment.pk,
                'post_pk': post.pk,
                'is_reply': True,
                'user_pk': self.request.user.pk
            }
            empty_form = CommentForm(initial={'post': post, 'parent': parent_comment}) # Set initial values for empty form
            form_html = render_to_string("blog/comment_reply.html",
                                         {'form': empty_form,
                                          'parent_comment': parent_comment,
                                          'post': post},
                                           request=self.request)
            
            return JsonResponse({
                'success': True,
                'new_comment': new_comment_data,
                'form_html': form_html,
                'parent_pk': parent_comment.pk,
            })
        
        else:
            return redirect(self.get_success_url())
        
    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            parent_comment = self.get_parent_comment()
            post = self.get_post()
            form_html = render_to_string("blog/comment_reply.html",
                                         {'form': form,
                                          'parent_comment': parent_comment,
                                          'post': post},
                                         request=self.request)
            return JsonResponse({'success': False, 'errors': form.errors, 'form_html': form_html})
        
        else:
            return super().form_invalid(form)
 

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        parent_comment = self.get_parent_comment()
        post = self.get_post()
        context['parent_comment'] = parent_comment
        context['post'] = post
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if 'form' not in context:
                context['form'] = kwargs.get('form') or self.get_form()
        return context
    
    def get_success_url(self):
        post_pk = self.kwargs['post_pk']
        return reverse("blog:post-detail", kwargs={"pk":post_pk})
    

class CommentDeleteView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_staff
    
    def get(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.delete()

        return redirect(
            request.META.get(
                "HTTP_REFERER",
                reverse("blog:home")
            )
        )




    