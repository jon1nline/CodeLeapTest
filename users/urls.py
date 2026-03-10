from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserLogin, UserRegister

urlpatterns = [
    # path('users/', UserRegister.as_view(), name='users-list-create'),
    path("register/", UserRegister.as_view()),
    path("login/", UserLogin.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
]
