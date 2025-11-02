from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='blog_image', blank=True, null=True)
    created_date = models.DateTimeField()
    published_date = models.DateTimeField()

    def __str__(self):
        return f"{self.title} ({self.pk})"