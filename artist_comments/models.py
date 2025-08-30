from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from artists.models import ArtistProfile


class CommentAndRating(models.Model):
    """
    A model to store public comments and ratings for artists.
    """
    artist = models.ForeignKey(
        ArtistProfile,
        on_delete=models.CASCADE,
        related_name='comments_and_ratings'
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.name} on {self.artist.first_name}'s profile"

    class Meta:
        verbose_name_plural = "Comments and Ratings"
        ordering = ['-created_at']
