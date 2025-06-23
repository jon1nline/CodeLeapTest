from django.shortcuts import render
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .models import Posts
from .serializers import PostsSerializer, PostUpdateSerializer
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from users.utils.jwt_utils import verificar_token_cookies
from users.models import Users
from .serializers import PostsSerializer


def check_login( request):
    payload, error_response = verificar_token_cookies(request)
    if error_response:
        return None, error_response
    return payload, None


class PostsListCreate(generics.ListCreateAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer

    def perform_create(self, serializer):
        payload, error = check_login(self.request)
        if error:
            return error
        try:
            user_id = payload.get('id')
            user = Users.objects.get(id=user_id)
            if not user_id:
                return Response(
                {'error': 'username not found in token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            serializer.save(username=user)   #save the post with the username_id and shows the username  
        except Users.DoesNotExist:
            # Se o usuário do token não existe mais no banco, levanta uma exceção (resposta 400).
            raise ValidationError("O usuário associado a este token não foi encontrado.")
        except Exception as e:
            # Captura outros erros inesperados.
            raise ValidationError(f"Ocorreu um erro inesperado: {str(e)}")

class PostsUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostUpdateSerializer
    http_method_names = ['patch', 'delete']  

    def patch(self, request, *args, **kwargs):
        payload, error = check_login(request)
        if error:
            return error
             
        instance = self.get_object()
        logged_user_id = payload.get('id')

        logged_user = self.get_object()
        if not logged_user:
            return Response(
            {'error': 'username not found in token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if instance.username.id != logged_user_id:
            return Response(
                    {'error': 'You can only update your own posts'},
                    status=status.HTTP_403_FORBIDDEN
                )
        return super().patch(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        #delete the post(soft delete)
        payload, error = check_login(request)
        if error:
            return error    
        try:
            post = self.get_object()
        except post.DoesNotExist:
            return Response(
                {'error': 'Post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        instance = self.get_object()
        logged_user_id = payload.get('id')
        if instance.username.id != logged_user_id:
            return Response(
                    {'error': 'You can only delete your own posts'},
                    status=status.HTTP_403_FORBIDDEN
                )
        post.is_active = False
        post.save()
        return Response(
        {'message': 'Post deleted '},
        status=status.HTTP_200_OK
    )