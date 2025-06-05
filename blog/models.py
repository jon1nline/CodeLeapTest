from django.db import models

class Posts(models.Model):
    username = models.CharField(max_length=50, null=False)
    created_time = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=100, null=False)
    content = models.CharField(max_length=5000, null=False)


    def __str__(self):
        return self.name
