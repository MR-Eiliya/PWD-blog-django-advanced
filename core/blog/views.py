from django.views.generic.base import TemplateView
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DetailView,
)
from .models import Post
from .forms import PostForm


class IndexView(TemplateView):
