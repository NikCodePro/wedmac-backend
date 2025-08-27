from rest_framework import generics
from .models import Rating
from .serializers import RatingCreateSerializer
from artists.models.models import ArtistProfile
from django.db.models import Avg

class CreateRatingAPIView(generics.CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingCreateSerializer

    def perform_create(self, serializer):
        rating = serializer.save()
        artist = rating.artist

        # Update average rating and count
        ratings = artist.ratings.all()
        artist.average_rating = ratings.aggregate(avg=Avg('rating'))['avg'] or 0
        artist.total_ratings = ratings.count()
        artist.save()
