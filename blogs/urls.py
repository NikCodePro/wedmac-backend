#urls.py
from django.urls import path
from .views import create_blog, edit_blog, delete_blog, get_blogs, get_blog_by_id, send_otp_for_comment, add_comment, update_comment, delete_comment


urlpatterns = [
    path('create/', create_blog, name='create_blog'),
    path('edit/<int:project_id>/', edit_blog, name='edit_blog'),
    path('delete/<int:project_id>/', delete_blog, name='delete_blog'),
    path('get/', get_blogs, name='get_blogs'),
    path('get/<int:project_id>/', get_blog_by_id, name='get_blog_by_id'),  # New endpoint
    
    
    # Commenting Feature Endpoints (Public)
    path('send-otp-for-comment/', send_otp_for_comment, name='send_otp_for_comment'),
    path('add-comment/<int:project_id>/', add_comment, name='add_comment'),
    path('update-comment/<int:project_id>/<int:comment_id>/', update_comment, name='update_comment'),
    path('delete-comment/<int:project_id>/<int:comment_id>/', delete_comment, name='delete_comment'),
]