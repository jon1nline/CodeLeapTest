import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Users
from .serializers import LoginSerializer, UserSerializer
from .utils.jwt_utils import criar_token


class UserRegister(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer


class UserLogin(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LoginSerializer
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response(
                {"detail": "incorrect username or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = criar_token(user)

        response = JsonResponse({"message": "Usuário conectado."})

        response.set_cookie(
            "access_token",
            token["access"],
            httponly=True,
            secure=False,
            samesite="Strict",
        )

        response.set_cookie(
            "refresh_token",
            token["refresh"],
            httponly=True,
            secure=False,
            samesite="Strict",
            max_age=604800,  # dura 7 dias
        )

        return response


class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("O usuário precisa entrar na conta")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("O usuário precisa entrar na conta")

        user = Users.objects.filter(id=payload["id"]).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)
