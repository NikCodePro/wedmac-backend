from rest_framework import serializers
from leads.models.selected_artist import SelectedArtist
from artists.models.models import ArtistProfile

class SelectedArtistSerializer(serializers.ModelSerializer):
    artist_name = serializers.SerializerMethodField()
    artist_id = serializers.PrimaryKeyRelatedField(
        source='artist',
        queryset=ArtistProfile.objects.all()
    )

    class Meta:
        model = SelectedArtist
        fields = ['id', 'artist_id', 'artist_name', 'is_active', 'created_at']
        read_only_fields = ['created_at']

    def get_artist_name(self, obj):
        return f"{obj.artist.first_name} {obj.artist.last_name}"