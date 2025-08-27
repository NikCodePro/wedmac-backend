from django.db import models
from cloudinary.models import CloudinaryField
# Create your models here.

class Blog(models.Model):
    project_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    hashtags = models.CharField(max_length=255, help_text="Comma-separated hashtags")
    author_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title} ({self.project_id})"

# New Model for photos related to a blog
class Photo(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='photos')
    image = CloudinaryField('image')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.blog.title}"