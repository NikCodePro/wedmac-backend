from django.urls import path  # ✅ This is the correct import
from .views.contact_us_view import ContactUsCreateAPIView, get_contact_submissions
from public.views.views import get_locations

urlpatterns = [
    path('contact-us/', ContactUsCreateAPIView.as_view(), name='contact-us'),
    path('get-contact-submissions/', get_contact_submissions, name='get_contact_submissions'),
    path('locations/', get_locations, name='get_locations'),
]
