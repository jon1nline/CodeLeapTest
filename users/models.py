from django.db import models

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, null=False)
    password = models.CharField(max_length=50, null=False)


    def __str__(self):
        return self.name
