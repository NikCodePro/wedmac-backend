from django.db import models
from artists.models import ArtistProfile

class Service(models.Model):
    artist = models.ForeignKey(
        ArtistProfile, 
        on_delete=models.CASCADE, 
        related_name='services_offered'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Artist Service'
        verbose_name_plural = 'Artist Services'
    
    def __str__(self):
        return f"{self.name} - {self.artist.first_name} {self.artist.last_name}"