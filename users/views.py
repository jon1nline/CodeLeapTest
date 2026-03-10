from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Users
from .serializers import UserSerializer


class UserRegister(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer


class UserLogin(TokenObtainPairView):
    pass
