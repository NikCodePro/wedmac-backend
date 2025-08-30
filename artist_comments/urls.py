from django.urls import path
from .views import send_otp_for_comment, add_comment_and_rating, get_artist_comments, update_comment_and_rating, delete_comment_and_rating

urlpatterns = [
    path('send-otp/', send_otp_for_comment, name='send_otp_for_comment'),
    path('add-comment-rating/<int:artist_id>/',
         add_comment_and_rating, name='add_comment_and_rating'),
    path('get-comments/<int:artist_id>/',
         get_artist_comments, name='get_artist_comments'),
    path('update-comment-rating/<int:artist_id>/<int:comment_id>/',
         update_comment_and_rating, name='update_comment_and_rating'),
    path('delete-comment-rating/<int:artist_id>/<int:comment_id>/',
         delete_comment_and_rating, name='delete_comment_and_rating'),
]
