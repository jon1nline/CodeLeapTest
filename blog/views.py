from django.shortcuts import render
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from .models import Posts
from .serializers import PostsSerializer, PostUpdateSerializer
from drf_yasg import openapi

class PostsListCreate(generics.ListCreateAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer

class PostsRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Posts.objects.all()
    http_method_names = ['patch', 'delete']  
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return PostUpdateSerializer
        return PostsSerializer  

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'content'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'content': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={200: PostUpdateSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)