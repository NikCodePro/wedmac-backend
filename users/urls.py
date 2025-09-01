from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views.login_views import OTPLoginView, RequestLoginOTPView
from users.views.logout import LogoutView
from users.views.registration_views import RequestOTPView, VerifyOTPView, AdminCreateArtistView, AdminLoginAsArtistView
from users.views.token_views import CustomTokenObtainPairView


urlpatterns = [
    # Auth & JWT
    path('login/', CustomTokenObtainPairView.as_view(), name='login'), # this is the custom login view,
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # User Registration and Login services 
    # this is the OTP based login and registration
    path('request-otp/', RequestOTPView.as_view(), name='request_otp'),
    # Verify OTP for registration
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    # Login with OTP
    path("login/request-otp/", RequestLoginOTPView.as_view(), name="login-request-otp"),
    # Verify OTP for login
    path("login-otp/", OTPLoginView.as_view(), name="login-otp"),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Admin create artist without OTP
    path('admin/create-artist/', AdminCreateArtistView.as_view(), name='admin_create_artist'),
    # Admin login as artist
    path('admin/login-as-artist/', AdminLoginAsArtistView.as_view(), name='admin_login_as_artist'),

    # Protected route
]