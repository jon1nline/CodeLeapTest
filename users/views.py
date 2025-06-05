from django.shortcuts import render
from rest_framework import generics
from .models import Users
from .serializers import UsersSerializer

class UsersListCreate(generics.ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

class UsersRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer