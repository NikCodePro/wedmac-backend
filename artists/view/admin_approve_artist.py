from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status as http_status
from superadmin_auth.permissions import IsSuperAdmin
from artists.models.models import ArtistProfile
from artists.serializers.serializers import ArtistProfileSerializer
from credit_history.models import ArtistCreditBalance, CreditTransaction, CreditType

class AdminApproveOrRejectArtistView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, artist_id):
        try:
            with transaction.atomic():
                artist_profile = ArtistProfile.objects.get(id=artist_id)
                new_status = request.data.get("status")
                notes = request.data.get("internal_notes", "")

                # Check if already approved
                if artist_profile.status == "approved" and new_status == "approved":
                    return Response({
                        "error": "Artist already approved",
                        "artist_details": {
                            "id": artist_profile.id,
                            "name": f"{artist_profile.first_name} {artist_profile.last_name}".strip(),
                            "current_status": artist_profile.status
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)

                original_status = artist_profile.status

                # Handle referral reward when approving for the first time
                if new_status == "approved" and original_status != "approved":
                    referral_code_used = getattr(artist_profile, 'referel_code', None)
                    
                    if referral_code_used:
                        try:
                            # Find referring artist
                            referring_artist = ArtistProfile.objects.select_for_update().get(
                                my_referral_code=referral_code_used
                            )

                            # Check if this referral was already rewarded
                            existing_reward = CreditTransaction.objects.filter(
                                artist=referring_artist,
                                transaction_type='referral',
                                reference_id=f"REF_{artist_profile.id}",
                                credit_type=CreditType.REFFERAL
                            ).exists()

                            if not existing_reward:
                                # Get credit balance for referring artist
                                credit_balance = ArtistCreditBalance.objects.select_for_update().get(
                                    artist=referring_artist
                                )

                                # Add referral credits (3 leads)
                                credit_balance._create_transaction(
                                    credit_type=CreditType.REFFERAL,
                                    amount=3,
                                    transaction_type='referral',
                                    description=f"Referral reward for {artist_profile.first_name} {artist_profile.last_name}",
                                    reference_id=f"REF_{artist_profile.id}"
                                )

                                # Update available_leads in artist profile
                                referring_artist.available_leads = (referring_artist.available_leads or 0) + 3
                                referring_artist.save()

                                print(f"Added 3 leads to {referring_artist.first_name} for referral")
                        except ArtistProfile.DoesNotExist:
                            print(f"Invalid referral code used: {referral_code_used}")
                        except Exception as e:
                            print(f"Error processing referral: {str(e)}")

                # Update status and save
                artist_profile.status = new_status
                artist_profile.internal_notes = notes
                artist_profile.save()

                return Response({
                    "message": f"Artist profile has been {new_status}.",
                    "profile": ArtistProfileSerializer(artist_profile).data
                }, status=status.HTTP_200_OK)

        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error in approve/reject: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminChangePendingStatusView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, artist_id):
        try:
            artist_profile = ArtistProfile.objects.get(id=artist_id)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist profile not found."}, status=http_status.HTTP_404_NOT_FOUND)

        current_status = artist_profile.status
        notes = request.data.get("internal_notes", "")

        # Store current status in response
        previous_status = current_status

        # Always change to pending, regardless of current status
        artist_profile.status = "pending"
        artist_profile.internal_notes = notes
        artist_profile.save()

        return Response({
            "message": "Artist status changed to pending",
            "details": {
                "artist_id": artist_profile.id,
                "name": f"{artist_profile.first_name} {artist_profile.last_name}".strip(),
                "previous_status": previous_status,
                "current_status": "pending"
            },
            "profile": ArtistProfileSerializer(artist_profile).data
        }, status=http_status.HTTP_200_OK)

class AdminRejectArtistView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, artist_id):
        try:
            artist_profile = ArtistProfile.objects.get(id=artist_id)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist profile not found."}, status=http_status.HTTP_404_NOT_FOUND)

        current_status = artist_profile.status
        notes = request.data.get("internal_notes", "")

        # Store previous status for response
        previous_status = current_status

        # Set status to rejected
        artist_profile.status = "rejected"
        artist_profile.internal_notes = notes
        artist_profile.save()

        return Response({
            "message": "Artist status changed to rejected",
            "details": {
                "artist_id": artist_profile.id,
                "name": f"{artist_profile.first_name} {artist_profile.last_name}".strip(),
                "previous_status": previous_status,
                "current_status": "rejected",
                "rejection_notes": notes
            },
            "profile": ArtistProfileSerializer(artist_profile).data
        }, status=http_status.HTTP_200_OK)

class AdminDeleteArtistView(APIView):
    permission_classes = [IsSuperAdmin]

    def delete(self, request, artist_id):
        try:
            with transaction.atomic():
                # Get the artist profile
                artist_profile = ArtistProfile.objects.get(id=artist_id)
                
                # Store artist details for response
                artist_details = {
                    "id": artist_profile.id,
                    "name": f"{artist_profile.first_name} {artist_profile.last_name}".strip(),
                    "phone": artist_profile.phone,
                    "email": artist_profile.email
                }

                # Delete associated user
                if artist_profile.user:
                    artist_profile.user.delete()

                # Delete the artist profile
                artist_profile.delete()

                return Response({
                    "message": "Artist profile has been deleted successfully",
                    "deleted_artist": artist_details
                }, status=http_status.HTTP_200_OK)

        except ArtistProfile.DoesNotExist:
            return Response(
                {"error": "Artist profile not found"}, 
                status=http_status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to delete artist: {str(e)}"}, 
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdminSetArtistActiveView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, artist_id):
        try:
            artist = ArtistProfile.objects.get(id=artist_id)
            artist.is_active = True
            artist.save()
            return Response({"message": "Artist set to active", "artist_id": artist.id}, status=status.HTTP_200_OK)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminSetArtistInactiveView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, artist_id):
        try:
            artist = ArtistProfile.objects.get(id=artist_id)
            artist.is_active = False
            artist.save()
            return Response({"message": "Artist set to inactive", "artist_id": artist.id}, status=status.HTTP_200_OK)
        except ArtistProfile.DoesNotExist:
            return Response({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)