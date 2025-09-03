from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("The username must be set")
        if not email:
            raise ValueError("The Email must be set")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Hashes the password
        user.save(using=self._db)
        return user


class Users(AbstractUser):
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=200)
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ["email", "password"]

    objects = UserManager()

    def __str__(self):
        return self.email
