from django.urls import path
from .views import create_blog, edit_blog, delete_blog, get_blogs, get_blog_by_id


urlpatterns = [
    path('create/', create_blog, name='create_blog'),
    path('edit/<int:project_id>/', edit_blog, name='edit_blog'),
    path('delete/<int:project_id>/', delete_blog, name='delete_blog'),
    path('get/', get_blogs, name='get_blogs'),
    path('get/<int:project_id>/', get_blog_by_id, name='get_blog_by_id'),  # New endpoint
]