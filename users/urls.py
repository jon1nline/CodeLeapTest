from django.urls import path
from .views import UsersListCreate, UsersRetrieveUpdateDestroy

urlpatterns = [
    path('users/', UsersListCreate.as_view(), name='users-list-create'),
   # path('employees/<int:pk>/', UsersRetrieveUpdateDestroy.as_view(), name='employees-retrieve-update-destroy'),
]