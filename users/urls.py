from django.urls import path
from .views import UserRegister, UserLogin

urlpatterns = [
   # path('users/', UserRegister.as_view(), name='users-list-create'),
    path('register/', UserRegister.as_view()),
    path('login/', UserLogin.as_view()),

]