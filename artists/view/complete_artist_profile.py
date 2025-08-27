from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from artists.models.models import ArtistProfile, SocialLink
from artists.serializers.serializers import ArtistProfileSerializer
from documents.models import Document
from adminpanel.models import MakeupType
import json

class CompleteArtistProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.otp_verified:
            return Response({"error": "OTP not verified."}, status=403)

        try:
            artist_profile = user.artist_profile
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist profile not found. Please complete signup first."}, status=404)

        incoming_data = request.data.copy()
        trial_available = incoming_data.get('trial_available', False)
        trial_paid_type = incoming_data.get('trial_paid_type', None)

        if trial_available:
            # If trial_paid_type is not provided, set to 'paid' by default
            if not trial_paid_type:
                incoming_data['trial_paid_type'] = 'paid'
        else:
            # Remove trial_paid_type if trial is not available
            incoming_data.pop('trial_paid_type', None)

        # Handle makeup types
        makeup_types = incoming_data.pop('type_of_makeup', [])
        if makeup_types:
            artist_profile.type_of_makeup.clear()
            for makeup_type_id in makeup_types:
                try:
                    makeup_type = MakeupType.objects.get(id=makeup_type_id)
                    artist_profile.type_of_makeup.add(makeup_type)
                except MakeupType.DoesNotExist:
                    pass
                
                
        # Handle social links (now optional)
        try:
            social_links = incoming_data.pop('social_links', {})  # Accept empty dict
            # Only process if social_links is not empty
            if social_links:
                SocialLink.objects.filter(artist=artist_profile).delete()
                created_links = []
                for platform, url in social_links.items():
                    if not url or str(url).strip() == "":
                        continue  # Skip blank URLs
                    try:
                        social_link = SocialLink.objects.create(
                            artist=artist_profile,
                            platform=platform.lower(),
                            url=url
                        )
                        created_links.append({
                            'id': social_link.id,
                            'platform': social_link.platform,
                            'url': social_link.url
                        })
                        print(f"Created social link: {platform} - {url}")  # Debug line
                    except Exception as e:
                        print(f"Error creating social link: {str(e)}")
                        continue

                # Add created links to response
                incoming_data['social_links'] = created_links
                print(f"All created links: {created_links}")  # Debug line
                
        except Exception as e:
            print(f"Social links error: {str(e)}")  # Debug line
            # Do not return error, just continue

        # Handle documents
        profile_picture_id = incoming_data.get('profile_picture')
        certifications_ids = incoming_data.get('certifications', [])
        new_id_doc_ids = incoming_data.get('id_documents', [])
        new_supporting_image_ids = incoming_data.get('supporting_images', [])

        if profile_picture_id:
            if artist_profile.profile_picture:
                artist_profile.profile_picture.is_active = False
                artist_profile.profile_picture.save()
            Document.objects.filter(id=profile_picture_id).update(is_active=True)

        if certifications_ids:
            artist_profile.certifications.update(is_active=False)
            Document.objects.filter(id__in=certifications_ids).update(is_active=True)

        if new_id_doc_ids:
            artist_profile.id_documents.update(is_active=False)
            Document.objects.filter(id__in=new_id_doc_ids).update(is_active=True)

        if new_supporting_image_ids:
            artist_profile.supporting_images.update(is_active=False)
            Document.objects.filter(id__in=new_supporting_image_ids).update(is_active=True)

        # Update remaining fields
        serializer = ArtistProfileSerializer(
            artist_profile,
            data=incoming_data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully.",
                "data": serializer.data
            }, status=200)

        return Response(serializer.errors, status=400)
