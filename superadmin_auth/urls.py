# superadmin_auth/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'superadmin_auth'

urlpatterns = [
    path('login/', views.superadmin_login, name='superadmin_login'),
    path('verify-otp/', views.superadmin_verify_otp, name='superadmin_verify_otp'),
    path('profile/', views.superadmin_profile, name='superadmin_profile'),
    path('logout/', views.superadmin_logout, name='superadmin_logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
