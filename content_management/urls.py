# content_management/urls.py

from django.urls import path
from .views import create_review, update_review, delete_review, get_reviews, get_review_by_id, create_video_review, update_video_review, delete_video_review, get_video_reviews, get_video_review_by_id


urlpatterns = [
    # Admin-only endpoints for CRUD operations
    path('create/', create_review, name='create_review'),
    path('update/<int:review_id>/', update_review, name='update_review'),
    path('delete/<int:review_id>/', delete_review, name='delete_review'),

    # Public endpoints for fetching reviews
    path('get/', get_reviews, name='get_reviews'),
    path('get/<int:review_id>/', get_review_by_id, name='get_review_by_id'),

    # ===============================================
    # New video review URLs
    path('video-reviews/create/', create_video_review, name='create-video-review'),
    path('video-reviews/update/<int:video_review_id>/',
         update_video_review, name='update-video-review'),
    path('video-reviews/delete/<int:video_review_id>/',
         delete_video_review, name='delete-video-review'),
    path('video-reviews/get/', get_video_reviews, name='get-video-reviews'),
    path('video-reviews/get/<int:video_review_id>/',
         get_video_review_by_id, name='get-video-review-by-id'),
]
