from django.db import models
from artists.models.models import ArtistProfile

class SelectedArtist(models.Model):
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.artist.first_name} {self.artist.last_name} ({'Active' if self.is_active else 'Inactive'})"