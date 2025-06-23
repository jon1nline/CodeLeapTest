from django.urls import path
from .views import PostsListCreate, PostsUpdateDestroy

urlpatterns = [
    path('post/', PostsListCreate.as_view(), name='posts-list-create'),
   path('post/<int:pk>/', PostsUpdateDestroy.as_view(), name='posts-retrieve-update-destroy'),
]