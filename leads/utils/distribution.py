from artists.models import ArtistProfile
from artists.models.models import ArtistSubscription
from leads.models.lead_distribution_rule import LeadDistributionConfig, LeadDistributionRule
from django.db import transaction

# ------------------------------
# ✅ Config Utilities
# ------------------------------

def get_config_value(key, default=None):
    try:
        return LeadDistributionConfig.objects.get(key=key).value
    except LeadDistributionConfig.DoesNotExist:
        return default

# ------------------------------
# ✅ Strategy Resolver
# ------------------------------

def get_active_distribution_strategy():
    active_rule = LeadDistributionRule.objects.filter(is_active=True).first()
    return active_rule.strategy if active_rule else None

# ------------------------------
# ✅ Round Robin Logic
# ------------------------------

def get_next_artist_round_robin():
    # Fetch all eligible artists
    artists = ArtistProfile.objects.filter(status='approved').order_by('id')

    if not artists.exists():
        return None

    # Get the last used pointer from config
    pointer = get_config_value("CURRENT_ARTIST_POINTER")
    pointer = int(pointer) if pointer and pointer.isdigit() else None

    artist_ids = list(artists.values_list('id', flat=True))

    try:
        current_index = artist_ids.index(pointer)
        next_index = (current_index + 1) % len(artist_ids)
    except ValueError:
        next_index = 0  # fallback to first artist if pointer is invalid

    next_artist_id = artist_ids[next_index]
    next_artist = ArtistProfile.objects.get(id=next_artist_id)

    # Update the pointer in config
    LeadDistributionConfig.objects.update_or_create(
        key="CURRENT_ARTIST_POINTER",
        defaults={"value": str(next_artist_id)}
    )

    return next_artist

# ------------------------------
# ✅ Main Assignment Function
# ------------------------------
from django.utils import timezone

def assign_lead_automatically(lead):
    with transaction.atomic():
        strategy = get_active_distribution_strategy()

        if not strategy:
            print("No active distribution strategy found. Skipping automatic assignment.")
            return None

        artist = None
        print(f"Active distribution strategy: {strategy}")

        if strategy == 'round_robin':
            artist = get_next_artist_round_robin()

        # Validate artist eligibility
        if artist:
            if artist.status != "approved":
                print(f"Artist {artist} is not approved.")
                artist = None
            elif artist.available_leads <= 0:
                print(f"Artist {artist} has no available leads.")
                artist = None

        if artist:
            # Assign the lead and deduct available lead
            lead.assigned_to = artist
            lead.status = "contacted"
            lead.save()

            # Deduct one lead from available_leads
            artist.available_leads = max(0, artist.available_leads - 1)
            artist.save()

            print(f"Lead assigned to artist: {artist}")
            return artist

        # ✅ Fallback artist if strategy is active but no eligible artist found
        default_artist_id = get_config_value("DEFAULT_ARTIST_ID")
        if default_artist_id:
            try:
                default_artist = ArtistProfile.objects.get(id=int(default_artist_id))
                if default_artist.status == "approved":
                    lead.assigned_to = default_artist
                    lead.status = "contacted"
                    lead.save()
                    return default_artist
            except ArtistProfile.DoesNotExist:
                return None

        return None
