from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    tag = models.CharField(max_length=155, blank=True, null=True)

    def __str__(self):
        return self.title