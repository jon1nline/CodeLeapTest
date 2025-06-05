from django.urls import path
from .views import UsersListCreate, UsersRetrieveUpdateDestroy

urlpatterns = [
    path('users/', UsersListCreate.as_view(), name='users-list-create'),
]