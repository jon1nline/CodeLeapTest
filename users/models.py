from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('username is required.')
        email = self.normalize_email(email)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class Users(AbstractUser):
    username = models.CharField(unique=True, max_length=50) 
    password = models.CharField(max_length=200)
    email = models.EmailField(unique=True)  
      
    REQUIRED_FIELDS = ['email', 'password']  
    
    objects = UserManager()

    def __str__(self):
        return self.email

