# artists/serializers.py

from rest_framework import serializers
from adminpanel.models import MakeupType
from artists.models.models import ArtistProfile
from documents.models import Document


class DocumentURLSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ("id", "url")

    def get_url(self, obj):
        # robust getter for different possible Document field names
        if not obj:
            return None
        # common FileField on Document is usually `file` — try that first
        file_field = getattr(obj, "file", None)
        if file_field:
            try:
                return file_field.url
            except Exception:
                pass
        # fallback attribute names
        for attr in ("url", "file_url", "path", "file_path"):
            val = getattr(obj, attr, None)
            if isinstance(val, str) and val:
                return val
        return None


class ArtistCardSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    makeup_types = serializers.SerializerMethodField()
    profile_photo_url = serializers.SerializerMethodField()
    portfolio_photos = serializers.SerializerMethodField()
    price_range = serializers.CharField(allow_blank=True, allow_null=True)  # <-- Fixed line

    class Meta:
        model = ArtistProfile
        fields = [
            'id',
            'full_name',
            'profile_photo_url',
            'location',
            'average_rating',
            'total_ratings',
            'makeup_types',
            'portfolio_photos',
            'price_range',
            'tag',
        ]

    def get_full_name(self, obj):
        return f"{getattr(obj, 'first_name', '')} {getattr(obj, 'last_name', '')}".strip()

    def get_location(self, obj):
        loc = getattr(obj, "location", None)
        if not loc:
            return None
        return {
            "city": getattr(loc, "city", None),
            "state": getattr(loc, "state", None),
            "pincode": getattr(loc, "pincode", None),
        }

    def get_makeup_types(self, obj):
        # example: return list of names
        return [m.name for m in getattr(obj, "type_of_makeup").all()] if getattr(obj, "type_of_makeup", None) else []

    def get_profile_photo_url(self, obj):
        # get related Document instance (if any) from artist profile
        doc = getattr(obj, "profile_picture", None)
        # if profile_picture is an id or string, try to fetch Document
        if doc and not isinstance(doc, Document):
            try:
                doc = Document.objects.filter(id=doc).first()
            except Exception:
                doc = None
        # use DocumentURLSerializer (or direct logic) to get url
        if isinstance(doc, Document):
            return DocumentURLSerializer(doc).data.get("url")
        # fallback: none
        return None

    def get_portfolio_photos(self, obj):
        images = obj.supporting_images.all()[:3]
        return DocumentURLSerializer(images, many=True).data
