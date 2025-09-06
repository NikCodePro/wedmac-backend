# views.py
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from superadmin_auth.permissions import IsSuperAdmin
from notifications.services import TwoFactorService
from .models import Blog, Photo, Comment
from django.db import transaction
import random


@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def create_blog(request):
    data = request.data
    images = request.FILES.getlist('images')  # Get list of uploaded files
    
    # Check if the number of photos exceeds the limit of 3
    if len(images) > 3:
        return Response({
            'error': 'You can only upload a maximum of 3 photos per blog post.'
        }, status=400)  
    
    with transaction.atomic():
        blog = Blog.objects.create(
            project_id=data['project_id'],
            title=data['title'],
            content=data['content'],
            hashtags=data['hashtags'],
            author_name=request.user.username,
            category=data['category'],
        )
        
            # Save each uploaded image to Cloudinary and link to the blog
        for image in images:
            Photo.objects.create(blog=blog, image=image)
            
    return Response({
        'id': blog.id, 
        'project_id': blog.project_id, 
        'message': 'Blog created'
    }, status=201)

@api_view(['PUT'])
@permission_classes([IsSuperAdmin])
def edit_blog(request, project_id):
    blog = get_object_or_404(Blog, project_id=project_id)
    data = request.data
    images = request.FILES.getlist('images')  # Get list of new uploaded files
    
    with transaction.atomic():
        # Update text fields first
        blog.title = data.get('title', blog.title)
        blog.content = data.get('content', blog.content)
        blog.hashtags = data.get('hashtags', blog.hashtags)
        blog.category = data.get('category', blog.category)
        blog.save()
        
        # Handle new image uploads with a queue logic
        if images:
            # Order existing photos by their ID to ensure we always get the oldest ones first
            existing_photos = list(blog.photos.all().order_by('id'))
            
            for new_image in images:
                # If there are already 3 photos, delete the oldest one
                if len(existing_photos) >= 3:
                    # Get the oldest photo (the first one in our ordered list)
                    oldest_photo = existing_photos.pop(0)
                    oldest_photo.delete()
                
                # Now, create and add the new photo
                new_photo = Photo.objects.create(blog=blog, image=new_image)
                # Add the new photo to our list to keep track of the count
                existing_photos.append(new_photo)

    return Response({'message': 'Blog updated'}, status=200)

@api_view(['DELETE'])
@permission_classes([IsSuperAdmin])
def delete_blog(request, project_id):
    blog = get_object_or_404(Blog, project_id=project_id)
    blog.delete()
    return Response({'message': 'Blog deleted'}, status=200)

@api_view(['GET'])
def get_blogs(request):
    category = request.GET.get('category')
    if category:
        blogs = Blog.objects.filter(category=category)
    else:
        blogs = Blog.objects.all()
    
    data = []
    for blog in blogs:
        blog_data = {
            "id": blog.id,
            "project_id": blog.project_id,
            "title": blog.title,
            "content": blog.content,
            "created_on": blog.created_on.strftime("%Y-%m-%d %H:%M:%S"),
            "hashtags": blog.hashtags,
            "author_name": blog.author_name,
            "category": blog.category,
            "photos": [photo.image.url for photo in blog.photos.all()] # Fetch photo URLs
        }
        data.append(blog_data)
        
    return Response(data, status=200)

@api_view(['GET'])
def get_blog_by_id(request, project_id):
    """
    Get a specific blog by its ID
    """
    blog = get_object_or_404(Blog, project_id=project_id)
    photos = [photo.image.url for photo in blog.photos.all()] # Fetch photo URLs
    comments = [
        {
            "id": comment.id,
            "name": comment.name,
            "phone_number": comment.phone_number,
            "location": comment.location,
            "comment": comment.comment,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for comment in blog.comments.all()
    ]
    
    data = {
        "id": blog.id,
        "project_id": blog.project_id,
        "title": blog.title,
        "content": blog.content,
        "created_on": blog.created_on.strftime("%Y-%m-%d %H:%M:%S"),
        "hashtags": blog.hashtags,
        "author_name": blog.author_name,
        "category": blog.category,
        "photos": photos,
        "comments": comments
    }
    return Response(data, status=200)

# New API View to send OTP for comment
@api_view(['POST'])
def send_otp_for_comment(request):
    phone_number = request.data.get('phone_number')
    if not phone_number:
        return Response({"error": "Phone number is required."}, status=400)
    
    # Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Initialize TwoFactorService and send OTP
    response = TwoFactorService(phone=phone_number, otp=otp).send_otp()

    if response.get("Status") == "Success":
        return Response({"message": "OTP sent successfully."}, status=200)
    else:
        return Response({"error": response.get("Details", "Failed to send OTP.")}, status=400)

# New API View to verify OTP and add comment
@api_view(['POST'])
def add_comment(request, project_id):
    try:
        blog = get_object_or_404(Blog, project_id=project_id)
        
        data = request.data
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        name = data.get('name')
        location = data.get('location')
        comment_content = data.get('comment')
        
        if not all([phone_number, name, comment_content]):
            return Response({"error": "Missing required fields."}, status=400)

        # Check if the user has already commented with this phone number
        user_verified = Comment.objects.filter(phone_number=phone_number).exists()

        if user_verified:
            # If the user has commented before, skip OTP verification
            Comment.objects.create(
                blog=blog,
                name=name,
                phone_number=phone_number,
                location=location,
                comment=comment_content
            )
            return Response({"message": "Comment added successfully (previous user)."}, status=201)
        else:
            # If it's a new user, proceed with OTP verification
            if not otp:
                return Response({"error": "OTP is required for first-time users."}, status=400)

            two_factor_service = TwoFactorService(phone=phone_number, otp=otp)
            verification_response = two_factor_service.verify_otp()

            if verification_response.get("Status") == "Success":
                # OTP is valid, create the comment
                Comment.objects.create(
                    blog=blog,
                    name=name,
                    phone_number=phone_number,
                    location=location,
                    comment=comment_content
                )
                return Response({"message": "Comment added successfully."}, status=201)
            else:
                return Response({"error": "OTP verification failed. Please try again."}, status=400)
            
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['PUT'])
def update_comment(request, project_id, comment_id):
    """
    Updates a user's existing comment.
    """
    try:
        comment = get_object_or_404(Comment, id=comment_id, blog__project_id=project_id)
        data = request.data
        
        # Security check: Ensure the phone number in the request matches the commenter's
        if data.get('phone_number') != comment.phone_number:
            return Response({"error": "Unauthorized: Phone number does not match commenter."}, status=403)
            
        comment.name = data.get('name', comment.name)
        comment.location = data.get('location', comment.location)
        comment.comment = data.get('comment', comment.comment)
        comment.save()

        return Response({"message": "Comment updated successfully."}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['DELETE'])
def delete_comment(request, project_id, comment_id):
    """
    Deletes a user's comment.
    """
    try:
        comment = get_object_or_404(Comment, id=comment_id, blog__project_id=project_id)
        data = request.data

        # Security check: Ensure the phone number in the request matches the commenter's
        if data.get('phone_number') != comment.phone_number:
            return Response({"error": "Unauthorized: Phone number does not match commenter."}, status=403)

        comment.delete()
        
        return Response({"message": "Comment deleted successfully."}, status=200)
    
    except Exception as e:
        return Response({"error": str(e)}, status=400)
