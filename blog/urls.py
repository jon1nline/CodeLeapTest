from django.urls import path
from .views import PostsListCreate, PostsRetrieveUpdateDestroy

urlpatterns = [
    path('blog/', PostsListCreate.as_view(), name='posts-list-create'),
   path('blog/<int:pk>/', PostsRetrieveUpdateDestroy.as_view(), name='posts-retrieve-update-destroy'),
]