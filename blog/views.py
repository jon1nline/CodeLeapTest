from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from users.models import Users
from users.utils.jwt_utils import verificar_token_cookies

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

    def get_queryset(self):
        return Posts.objects.filter(
            is_active=True,
        ).order_by("created_dateTime")

    def perform_create(self, serializer):
        payload, error = check_login(self.request)
        if error:
            return Response(
                {"error": "user not logged-in"}, status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            user_id = payload.get("id")
            user = Users.objects.get(id=user_id)
            author_ip_address = get_author_ip(self.request)
            time_post = timezone.now()
            if not user_id:
                return Response(
                    {"error": "username not found in token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            serializer.save(
                username=user, author_ip=author_ip_address, created_dateTime=time_post
            )  # save the post with the username_id, author_ip and shows the username
        except Users.DoesNotExist:
            # Se o usuário do token não existe mais no banco, levanta uma exceção (resposta 400).
            raise ValidationError(
                "O usuário associado a este token não foi encontrado."
            )
        except Exception as e:
            # Captura outros erros inesperados.
            raise ValidationError(f"Ocorreu um erro inesperado: {str(e)}")

    def list(self, request, *args, **kwargs):
        payload, error = check_login(request)
        if error:
            return Response(
                {"error": "username not found in token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        queryset = self.filter_queryset(self.get_queryset())
        # retorna os posts paginados.
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        payload, error = check_login(request)
        if error:
            return Response(
                {"error": "user not logged-in"}, status=status.HTTP_401_UNAUTHORIZED
            )

        instance = self.get_object()
        logged_user_id = payload.get("id")

        logged_user = self.get_object()
        if not logged_user:
            return Response(
                {"error": "username not found in token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if instance.username.id != logged_user_id:
            return Response(
                {"error": "You can only update your own posts"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().patch(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # delete the post(soft delete)
        payload, error = check_login(request)
        if error:
            return Response(
                {"error": "user not logged-in"}, status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            post = self.get_object()
        except post.DoesNotExist:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        instance = self.get_object()
        logged_user_id = payload.get("id")
        if instance.username.id != logged_user_id:
            return Response(
                {"error": "You can only delete your own posts"},
                status=status.HTTP_403_FORBIDDEN,
            )
        post.is_active = False
        post.save()
        return Response({"message": "Post deleted "}, status=status.HTTP_204_NO_CONTENT)
