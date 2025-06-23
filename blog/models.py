from django.db import models

class Posts(models.Model):
    username = models.ForeignKey(
        'users.Users',
        on_delete=models.CASCADE)
    created_dateTime = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=100, null=False)
    content = models.CharField(max_length=5000, null=False)
    author_ip = models.CharField(max_length=20)
    likes = models.IntegerField(null=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.title
    
    
    
