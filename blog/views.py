from django.db.models import Q
from rest_framework import filters, permissions, viewsets
from utils.permissions import IsOwnerOrReadOnly

from .models import Posts
from .serializers import PostSerializer


def get_author_ip(request):

    # Check for the X-Forwarded-For header first
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        # Fallback to REMOTE_ADDR if X-Forwarded-For is not present
        ip = request.META.get("REMOTE_ADDR")

    return ip


class PostViewSet(viewsets.ModelViewSet):
    queryset = Posts.objects.all()
    serializer_class = PostSerializer
    http_method_names = ["get", "patch", "post", "delete"]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_dateTime", "title"]
    search_fields = ["title", "content"]
    ordering = ["-created_dateTime"]
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]

    def get_queryset(self):
        queryset = Posts.objects.filter(
            is_active=True,
        ).select_related("username")

        author = self.request.query_params.get("author")
        if author:
            queryset = queryset.filter(username__username__icontains=author)

        query = self.request.query_params.get("query")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        author_ip_address = get_author_ip(self.request)
        serializer.save(username=user, author_ip=author_ip_address)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        # Implementa o soft delete.
        instance.is_active = False
        instance.save()
