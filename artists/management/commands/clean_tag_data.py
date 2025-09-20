from django.core.management.base import BaseCommand
from artists.models import ArtistProfile
import json

class Command(BaseCommand):
    help = 'Clean up invalid tag data before migration'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up tag data...')

        updated_count = 0
        for artist in ArtistProfile.objects.all():
            if artist.tag:
                try:
                    # Try to parse as JSON first
                    if isinstance(artist.tag, str):
                        # Handle common invalid JSON cases
                        if artist.tag.strip() == '' or artist.tag.lower() in ['null', 'none', 'invalid', 'invalid value.']:
                            artist.tag = []
                            artist.save()
                            updated_count += 1
                        else:
                            try:
                                # Try to parse as JSON
                                parsed = json.loads(artist.tag)
                                if isinstance(parsed, list):
                                    artist.tag = parsed
                                else:
                                    # It's a string that looks like JSON but isn't an array
                                    artist.tag = [artist.tag.strip()]
                                artist.save()
                                updated_count += 1
                            except (json.JSONDecodeError, TypeError):
                                # It's a plain string
                                artist.tag = [artist.tag.strip()]
                                artist.save()
                                updated_count += 1
                except Exception as e:
                    self.stdout.write(f'Error processing artist {artist.id}: {e}')
                    artist.tag = []
                    artist.save()
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleaned up {updated_count} artist tag records')
        )
