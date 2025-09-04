from django.utils import timezone
from rest_framework import permissions, viewsets

from utils.jwt_utils import verificar_token_cookies
from utils.permissions import IsOwnerOrReadOnly

from .models import Posts
from .serializers import PostSerializer


def check_login(request):
    payload, error_response = verificar_token_cookies(request)
    if error_response:
        return None, error_response
    return payload, None


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
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]

    def get_queryset(self):
        return Posts.objects.filter(
            is_active=True,
        ).order_by("created_dateTime")

    def perform_create(self, serializer):
        user = self.request.user
        author_ip_address = get_author_ip(self.request)
        time_post = timezone.now()

        serializer.save(
            username=user, author_ip=author_ip_address, created_dateTime=time_post
        )

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        # Implementa o soft delete.
        instance.is_active = False
        instance.save()
