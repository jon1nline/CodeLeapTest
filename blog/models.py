from django.db import models
from django.conf import settings

class Posts(models.Model):
    username = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_dateTime = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, null=False)
    content = models.CharField(max_length=5000, null=False)
    author_ip = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.title
    
    
    
