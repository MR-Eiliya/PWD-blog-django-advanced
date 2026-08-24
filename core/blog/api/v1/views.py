from rest_framework.permissions import (
    IsAuthenticated
)
from .serializers import PostSerializer, CategorySerializer
from ...models import Post, Category
from rest_framework import viewsets

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .pagination import DefaultPagination
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


class PostModelViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.filter(status=True)
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "author"]
    search_fields = ["title"]
    ordering_fields = ["published_date"]
    pagination_class = DefaultPagination



class CategoryModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
