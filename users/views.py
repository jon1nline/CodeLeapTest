from rest_framework import generics, throttling
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Users
from .serializers import UserSerializer


class UserRegister(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = "auth_register"


class UserLogin(TokenObtainPairView):
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = "auth_login"


class UserTokenRefresh(TokenRefreshView):
    throttle_classes = [throttling.ScopedRateThrottle]
    throttle_scope = "auth_refresh"
