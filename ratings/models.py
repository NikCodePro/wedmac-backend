from django.db import models

from artists.models.models import ArtistProfile


class Rating(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField()  # 1 to 5
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.artist.name} - {self.rating} ⭐"
