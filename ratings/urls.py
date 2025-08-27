from django.urls import path
from .views import CreateRatingAPIView, ArtistRatingsAPIView

urlpatterns = [
    path('rate/', CreateRatingAPIView.as_view(), name='add-rating'),
    path('artist/<int:id>/ratings/', ArtistRatingsAPIView.as_view(), name='get-artist-ratings'),
]
