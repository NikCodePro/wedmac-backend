# content_management/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField


class Review(models.Model):
    """
    A model to store client reviews.
    """
    description = models.TextField(
        help_text="The client's review description."
    )
    client_name = models.CharField(
        max_length=100,
        help_text="The name of the client."
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="The client's location."
    )
    used_service = models.CharField(
        max_length=200,
        help_text="The name of the service used by the client."
    )
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1), 
            MaxValueValidator(5)
        ],
        help_text="Rating out of 5 stars."
    )
    # New field to store the image URL uploaded to Cloudinary
    images = CloudinaryField(
        'images', 
        blank=True, 
        null=True, 
        help_text="An image associated with the review."
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Review by {self.client_name}"

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-created_at']

class VideoReview(models.Model):
    """
    A model to store client video reviews.
    """
    comment = models.TextField(
        help_text="The client's video review comment."
    )
    client_name = models.CharField(
        max_length=100,
        help_text="The name of the client."
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="The client's location."
    )
    used_service = models.CharField(
        max_length=200,
        help_text="The name of the service used by the client."
    )
    # Field to store the video URL uploaded to Cloudinary
    video = CloudinaryField(
        'video', 
        blank=True, 
        null=True, 
        help_text="A video associated with the review."
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Video Review by {self.client_name}"

    class Meta:
        verbose_name = "Video Review"
        verbose_name_plural = "Video Reviews"
        ordering = ['-created_at']