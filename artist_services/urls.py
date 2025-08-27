from django.urls import path
from .views import (
    ArtistServiceCreateView, 
    ArtistServiceListView,
    ArtistServiceDetailView,
    ArtistServiceDeleteView
)

app_name = 'artist_services'

urlpatterns = [
    # Artist endpoints
    path('services/get/', ArtistServiceListView.as_view(), name='artist-service-list'),
    path('services/create/', ArtistServiceCreateView.as_view(), name='artist-service-create'),
    path('services/<int:id>/', ArtistServiceDetailView.as_view(), name='service-detail'),
    path('services/<int:id>/delete/', ArtistServiceDeleteView.as_view(), name='service-delete'),
]