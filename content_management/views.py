# content_management/views.py

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from superadmin_auth.permissions import IsSuperAdmin
from .models import Review, VideoReview
from django.db import transaction


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def create_review(request):
    """
    Create a new review.
    """
    # Check if more than one image is uploaded and return an error if so.
    if len(request.FILES.getlist('images')) > 1:
        return Response({
            'error': 'You can only upload a single image.'
        }, status=400)
    
    data = request.data
    try:
        with transaction.atomic():
            review = Review.objects.create(
                description=data.get('description'),
                client_name=data.get('client_name'),
                location=data.get('location'),
                used_service=data.get('used_service'),
                rating=data.get('rating'),
                # Add the images field from the request data
                images=data.get('images') 
            )
        return Response({
            'message': 'Review created successfully.',
            'review_id': review.id
        }, status=201)
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to create review.'
        }, status=400)


@api_view(['PUT'])
@permission_classes([IsSuperAdmin])
def update_review(request, review_id):
    """
    Update an existing review by its ID.
    """
    # Check if more than one image is uploaded and return an error if so.
    if len(request.FILES.getlist('images')) > 1:
        return Response({
            'error': 'You can only upload a single image.'
        }, status=400)

    review = get_object_or_404(Review, id=review_id)
    data = request.data
    try:
        with transaction.atomic():
            review.description = data.get('description', review.description)
            review.client_name = data.get('client_name', review.client_name)
            review.location = data.get('location', review.location)
            review.used_service = data.get('used_service', review.used_service)
            review.rating = data.get('rating', review.rating)
            # Update the images field if it's present in the request
            if 'images' in data:
                review.images = data.get('images')
            review.save()
        return Response({
            'message': 'Review updated successfully.',
            'review_id': review.id
        }, status=200)
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to update review.'
        }, status=400)


@api_view(['DELETE'])
@permission_classes([IsSuperAdmin])
def delete_review(request, review_id):
    """
    Delete a review by its ID.
    """
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return Response({
        'message': 'Review deleted successfully.'
    }, status=200)


@api_view(['GET'])
def get_reviews(request):
    """
    Get a list of all reviews.
    """
    reviews = Review.objects.all()
    data = []
    for review in reviews:
        # Check if an image exists and get its URL, otherwise set to None
        image_url = review.images.url if review.images else None
        data.append({
            "id": review.id,
            "description": review.description,
            "client_name": review.client_name,
            "location": review.location,
            "used_service": review.used_service,
            "rating": review.rating,
            "images": image_url,
            "created_at": review.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return Response(data, status=200)


@api_view(['GET'])
def get_review_by_id(request, review_id):
    """
    Get a single review by its ID.
    """
    review = get_object_or_404(Review, id=review_id)
    # Check if an image exists and get its URL, otherwise set to None
    image_url = review.images.url if review.images else None
    data = {
        "id": review.id,
        "description": review.description,
        "client_name": review.client_name,
        "location": review.location,
        "used_service": review.used_service,
        "rating": review.rating,
        "images": image_url,
        "created_at": review.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }
    return Response(data, status=200)

# ======================================================================


# --- New API views for Video Reviews ---

@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def create_video_review(request):
    """
    Create a new video review.
    """
    # Check if more than one video is uploaded and return an error if so.
    if len(request.FILES.getlist('video')) > 1:
        return Response({
            'error': 'You can only upload a single video.'
        }, status=400)

    data = request.data
    try:
        with transaction.atomic():
            video_review = VideoReview.objects.create(
                comment=data.get('comment'),
                client_name=data.get('client_name'),
                location=data.get('location'),
                used_service=data.get('used_service'),
                video=data.get('video')
            )
        return Response({
            'message': 'Video review created successfully.',
            'video_review_id': video_review.id
        }, status=201)
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to create video review.'
        }, status=400)


@api_view(['PUT'])
@permission_classes([IsSuperAdmin])
def update_video_review(request, video_review_id):
    """
    Update an existing video review by its ID.
    """
    # Check if more than one video is uploaded and return an error if so.
    if len(request.FILES.getlist('video')) > 1:
        return Response({
            'error': 'You can only upload a single video.'
        }, status=400)

    video_review = get_object_or_404(VideoReview, id=video_review_id)
    data = request.data
    try:
        with transaction.atomic():
            video_review.comment = data.get('comment', video_review.comment)
            video_review.client_name = data.get('client_name', video_review.client_name)
            video_review.location = data.get('location', video_review.location)
            video_review.used_service = data.get('used_service', video_review.used_service)
            # Update the video field if it's present in the request
            if 'video' in data:
                video_review.video = data.get('video')
            video_review.save()
        return Response({
            'message': 'Video review updated successfully.',
            'video_review_id': video_review.id
        }, status=200)
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Failed to update video review.'
        }, status=400)


@api_view(['DELETE'])
@permission_classes([IsSuperAdmin])
def delete_video_review(request, video_review_id):
    """
    Delete a video review by its ID.
    """
    video_review = get_object_or_404(VideoReview, id=video_review_id)
    video_review.delete()
    return Response({
        'message': 'Video review deleted successfully.'
    }, status=200)


@api_view(['GET'])
def get_video_reviews(request):
    """
    Get a list of all video reviews.
    """
    video_reviews = VideoReview.objects.all()
    data = []
    for video_review in video_reviews:
        # Check if a video exists and get its URL, otherwise set to None
        video_url = video_review.video.url if video_review.video else None
        data.append({
            "id": video_review.id,
            "comment": video_review.comment,
            "client_name": video_review.client_name,
            "location": video_review.location,
            "used_service": video_review.used_service,
            "video": video_url,
            "created_at": video_review.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return Response(data, status=200)


@api_view(['GET'])
def get_video_review_by_id(request, video_review_id):
    """
    Get a single video review by its ID.
    """
    video_review = get_object_or_404(VideoReview, id=video_review_id)
    # Check if a video exists and get its URL, otherwise set to None
    video_url = video_review.video.url if video_review.video else None
    data = {
        "id": video_review.id,
        "comment": video_review.comment,
        "client_name": video_review.client_name,
        "location": video_review.location,
        "used_service": video_review.used_service,
        "video": video_url,
        "created_at": video_review.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }
    return Response(data, status=200)