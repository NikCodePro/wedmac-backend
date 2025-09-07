import random
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from artists.models import ArtistProfile
from .models import CommentAndRating
from notifications.services import TwoFactorService # Assuming this service exists
from django.db import transaction
from superadmin_auth.permissions import IsSuperAdmin

@api_view(['POST'])
def send_otp_for_comment(request):
    """
    Sends an OTP to a phone number for comment verification.
    """
    phone_number = request.data.get('phone_number')
    if not phone_number:
        return Response({"error": "Phone number is required."}, status=400)
    
    # Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Initialize TwoFactorService and send OTP
    two_factor_service = TwoFactorService(phone=phone_number, otp=otp)
    response = two_factor_service.send_otp()
    
    if response.get("Status") == "Success":
        return Response({"message": "OTP sent successfully."}, status=200)
    else:
        return Response({"error": response.get("Details", "Failed to send OTP.")}, status=400)


@api_view(['POST'])
def add_comment_and_rating(request, artist_id):
    """
    Verifies OTP (if needed) and adds a comment and rating to an artist's profile.
    """
    try:
        artist = get_object_or_404(ArtistProfile, id=artist_id)
        
        data = request.data
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        name = data.get('name')
        location = data.get('location')
        comment_content = data.get('comment')
        rating = data.get('rating')
        
        if not all([phone_number, name, comment_content, rating]):
            return Response({"error": "Missing required fields (phone_number, name, comment, rating)."}, status=400)

        # Check if the user has already commented with this phone number
        user_verified = CommentAndRating.objects.filter(phone_number=phone_number).exists()

        if user_verified:
            # If the user has commented before, skip OTP verification
            pass
        else:
            # If it's a new user, proceed with OTP verification
            if not otp:
                return Response({"error": "OTP is required for first-time users."}, status=400)

            two_factor_service = TwoFactorService(phone=phone_number, otp=otp)
            verification_response = two_factor_service.verify_otp()

            if verification_response.get("Status") != "Success":
                return Response({"error": "OTP verification failed. Please try again."}, status=400)
        
        # All checks passed, create the new comment and rating
        with transaction.atomic():
            new_comment = CommentAndRating.objects.create(
                artist=artist,
                name=name,
                phone_number=phone_number,
                location=location,
                comment=comment_content,
                rating=rating
            )
            
            # Update the artist's average rating
            total_ratings = CommentAndRating.objects.filter(artist=artist).count()
            current_total_score = artist.average_rating * artist.total_ratings
            new_total_score = current_total_score + new_comment.rating
            
            artist.total_ratings = total_ratings
            artist.average_rating = new_total_score / total_ratings
            artist.save()

        return Response({"message": "Comment and rating added successfully."}, status=201)
            
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['PUT'])
def update_comment_and_rating(request, artist_id, comment_id):
    """
    Updates a user's existing comment and rating on an artist's profile.
    """
    try:
        comment = get_object_or_404(CommentAndRating, id=comment_id, artist_id=artist_id)
        data = request.data
        
        # Security check: Ensure the phone number in the request matches the commenter's
        if data.get('phone_number') != comment.phone_number:
            return Response({"error": "Unauthorized: Phone number does not match commenter."}, status=403)
            
        comment.comment = data.get('comment', comment.comment)
        comment.rating = data.get('rating', comment.rating)
        comment.save()

        # Recalculate and update the artist's average rating
        artist = comment.artist
        all_comments = CommentAndRating.objects.filter(artist=artist)
        total_score = sum([c.rating for c in all_comments])
        artist.average_rating = total_score / len(all_comments) if all_comments else 0
        artist.save()

        return Response({"message": "Comment and rating updated successfully."}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['DELETE'])
def delete_comment_and_rating(request, artist_id, comment_id):
    """
    Deletes a user's comment and rating from an artist's profile.
    """
    try:
        comment = get_object_or_404(CommentAndRating, id=comment_id, artist_id=artist_id)
        data = request.data

        # Security check: Ensure the phone number in the request matches the commenter's
        if data.get('phone_number') != comment.phone_number:
            return Response({"error": "Unauthorized: Phone number does not match commenter."}, status=403)

        comment.delete()

        # Recalculate and update the artist's average rating
        artist = comment.artist
        all_comments = CommentAndRating.objects.filter(artist=artist)
        if all_comments.exists():
            total_score = sum([c.rating for c in all_comments])
            artist.total_ratings = all_comments.count()
            artist.average_rating = total_score / artist.total_ratings
        else:
            artist.total_ratings = 0
            artist.average_rating = 0.0
        artist.save()
        
        return Response({"message": "Comment and rating deleted successfully."}, status=200)
    
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['GET'])
def get_artist_comments(request, artist_id):
    """
    Retrieves all comments and ratings for a specific artist.
    """
    artist = get_object_or_404(ArtistProfile, id=artist_id)
    comments = CommentAndRating.objects.filter(artist=artist).order_by('-created_at')
    
    data = [
        {
            "id": comment.id,
            "name": comment.name,
            "location": comment.location,
            "comment": comment.comment,
            "rating": comment.rating,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for comment in comments
    ]
    
    return Response(data, status=200)

# Admin APIs for comment and rating management
@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def get_comments_admin(request):
    """
    Get all comments and ratings for admin, optionally filter by artist_id
    """
    artist_id = request.GET.get('artist_id')
    if artist_id:
        comments = CommentAndRating.objects.filter(artist_id=artist_id)
    else:
        comments = CommentAndRating.objects.all()

    data = [
        {
            "id": comment.id,
            "artist_id": comment.artist.id,
            "artist_name": f"{comment.artist.first_name} {comment.artist.last_name}",
            "name": comment.name,
            "phone_number": comment.phone_number,
            "location": comment.location,
            "comment": comment.comment,
            "rating": comment.rating,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for comment in comments
    ]
    return Response(data, status=200)

@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def get_comments_by_artist_admin(request, artist_id):
    """
    Get all comments and ratings for a specific artist by admin
    """
    comments = CommentAndRating.objects.filter(artist_id=artist_id)

    data = [
        {
            "id": comment.id,
            "artist_id": comment.artist.id,
            "artist_name": f"{comment.artist.first_name} {comment.artist.last_name}",
            "name": comment.name,
            "phone_number": comment.phone_number,
            "location": comment.location,
            "comment": comment.comment,
            "rating": comment.rating,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for comment in comments
    ]
    return Response(data, status=200)

@api_view(['PUT'])
@permission_classes([IsSuperAdmin])
def update_comment_admin(request, comment_id):
    """
    Update any comment and rating by admin
    """
    try:
        comment = get_object_or_404(CommentAndRating, id=comment_id)
        data = request.data

        comment.name = data.get('name', comment.name)
        comment.phone_number = data.get('phone_number', comment.phone_number)
        comment.location = data.get('location', comment.location)
        comment.comment = data.get('comment', comment.comment)
        comment.rating = data.get('rating', comment.rating)
        comment.save()

        # Recalculate and update the artist's average rating
        artist = comment.artist
        all_comments = CommentAndRating.objects.filter(artist=artist)
        if all_comments.exists():
            total_score = sum([c.rating for c in all_comments])
            artist.total_ratings = all_comments.count()
            artist.average_rating = total_score / artist.total_ratings
        else:
            artist.total_ratings = 0
            artist.average_rating = 0.0
        artist.save()

        return Response({"message": "Comment and rating updated successfully."}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['DELETE'])
@permission_classes([IsSuperAdmin])
def delete_comment_admin(request, comment_id):
    """
    Delete any comment and rating by admin
    """
    try:
        comment = get_object_or_404(CommentAndRating, id=comment_id)
        comment.delete()

        # Recalculate and update the artist's average rating
        artist = comment.artist
        all_comments = CommentAndRating.objects.filter(artist=artist)
        if all_comments.exists():
            total_score = sum([c.rating for c in all_comments])
            artist.total_ratings = all_comments.count()
            artist.average_rating = total_score / artist.total_ratings
        else:
            artist.total_ratings = 0
            artist.average_rating = 0.0
        artist.save()

        return Response({"message": "Comment and rating deleted successfully."}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)
