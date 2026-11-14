from .serializers import PostSerializer, CategorySerializer, TechnologyNewsSerializer
from ...models import Post, Category
from rest_framework import viewsets

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .pagination import DefaultPagination
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from ...news_service import get_technology_news

from rest_framework.views import APIView
from rest_framework.response import Response


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



class TechnologyNewsAPIView(APIView):

    def get(self, request):
        news = get_technology_news()
        serializer = TechnologyNewsSerializer(news, many=True)

        return Response(serializer.data)