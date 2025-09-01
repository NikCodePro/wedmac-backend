# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from appconfig.utils import MasterConfigManager
from artists.models.models import ArtistProfile , Location
import random
from django.utils import timezone
from django.db import transaction
from notifications.services import TwoFactorService
from notifications.services import NotificationService
from users.models import OTPVerification, User
import re
from users.views.utils import is_master_otp
from users.serializers import AdminArtistSerializer
# from users.permissions import IsAdminRole
from superadmin_auth.permissions import IsSuperAdmin
DUMMY_OTP = '123456'  #Simulated OTP for now

class RequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        required_fields = ['first_name', 'last_name', 'phone']
        for field in required_fields:
            if not data.get(field):
                return Response({f'error': f'{field.replace("_", " ").capitalize()} is required.'}, status=400)

        phone = data.get('phone', '').strip()
        if not re.fullmatch(r'\d{10}', phone):
            return Response({'error': 'Phone number must be exactly 10 digits.'}, status=400)
        if not re.fullmatch(r'[6-9]\d{9}', phone):
            return Response({'error': 'Enter a valid 10-digit Indian mobile number.'}, status=400)

        if User.objects.filter(phone=phone).exists():
            return Response({'error': 'Phone number already exists.'}, status=400)
        # Location data validation
        location_data = data.get('location')
        if not location_data:
            return Response({'error': 'Location is required.'}, status=400)

        city = location_data.get('city')
        state = location_data.get('state')
        pincode = location_data.get('pincode')
        if not city or not state :
            return Response({'error': 'Location (city, state) is required.'}, status=400)

        location_obj, _ = Location.objects.get_or_create(
            city=city,
            state=state,
            pincode=pincode,
            defaults={
                'lat': location_data.get('lat', 0.0),
                'lng': location_data.get('lng', 0.0)
            }
        )

        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                'username': phone,
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data.get('email', ''),
                'gender': data.get('gender', ''),
                'role': 'artist',
                'location': location_obj,
            }
        )

        # If user existed and missing location, update it
        if not created and not user.location:
            user.location = location_obj
            user.save()

        # Generate and save OTP
        otp = str(random.randint(100000, 999999))
        OTPVerification.objects.create(phone=phone, otp=otp)

        # Send OTP via 2FactorService (simulated here)
        two_factor_service = TwoFactorService(phone=phone, otp=otp)
        response = two_factor_service.send_otp()
        """{
            "Status": "Success",
            "Details": "ab88279e-0105-415f-912e-2f24162b8cbb"
            }
        """
        if response.get('Status') != 'Success':
            return Response({'error': response['error']}, status=500)
        if response.get('Details'):
            # Log the Details for debugging or tracking
            print(f"OTP sent successfully: {response['Details']}")

        return Response({'message': 'OTP sent successfully.', 'otp': otp}, status=200)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        otp = request.data.get('otp')

        if not phone or not otp:
            return Response({'error': 'Phone and OTP are required.'}, status=400)

        try:
            # Check for master OTP first
            if is_master_otp(otp, phone):
                user = User.objects.get(phone=phone)
                user.otp_verified = True
                user.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Verification successful using master OTP.',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user_id': user.id,
                    'role': user.role,
                })

            # Continue with normal OTP verification
            otp_obj = OTPVerification.objects.filter(phone=phone, otp=otp).latest('created_at')
            if otp_obj.is_expired():
                return Response({'error': 'OTP has expired.'}, status=400)
            
            two_factor_service = TwoFactorService(phone=phone, otp=otp)
            response = two_factor_service.verify_otp()
            print(f"OTP verification response: {response}")
            if response.get('Status') == 'Success': #  'Success' means Success OTP has been verified
                user = User.objects.get(phone=phone)
                user.otp_verified = True
                user.save()

                location = user.location
                ArtistProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'phone': user.phone,
                        'email': user.email,
                        'gender': user.gender,
                        'location': location
                    }
                )

                # send notification to admin
                # send notification to artist profile owner
                # Assuming you have a notification service to handle this
                self.send_notifications(user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'OTP verified successfully.',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user_id': user.id,
                    'role': user.role,
                })

        except OTPVerification.DoesNotExist:
            return Response({'error': 'Invalid OTP.'}, status=400)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)


    def send_notifications(self, user):
        """Send notification to admin and artist profile owner after OTP verification."""
        
        # Get admin numbers from config, fallback to a default number
        config = MasterConfigManager.get_config("NOTIFICATION_NUMBERS")
        raw_numbers = config.get("admin_phone", []) if config else []

        if isinstance(raw_numbers, list):
            admin_numbers = raw_numbers
        elif isinstance(raw_numbers, str):
            admin_numbers = raw_numbers.split(",")
        else:
            admin_numbers = [str(raw_numbers)]

        user_number = user.phone

        # Construct messages
        message_text = f"Artist {user.first_name} {user.last_name} and phone no {user.phone}has completed OTP verification."
        user_message = f"Hi {user.first_name}, your phone number has been successfully verified on Wedmac."

        messages = []

        # Message to each admin
        for admin_phone in admin_numbers:
            messages.append({
                "smsFrom": "TFACTR",
                "smsTo": f"+91{admin_phone.strip()[-10:]}",  # Normalize phone number
                "smsText": message_text
            })

        # Message to user
        messages.append({
            "smsFrom": "TFACTR",
            "smsTo": f"+91{user_number.strip()[-10:]}",
            "smsText": user_message
        })

        # Send bulk SMS
        response = NotificationService(messages=messages).send_notifications()
        print("Bulk SMS Response:", response)
        return response


class AdminCreateArtistView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        serializer = AdminArtistSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Validate phone format
        phone = data['phone'].strip()
        if not re.fullmatch(r'\d{10}', phone):
            return Response({'error': 'Phone number must be exactly 10 digits.'}, status=400)
        if not re.fullmatch(r'[6-9]\d{9}', phone):
            return Response({'error': 'Enter a valid 10-digit Indian mobile number.'}, status=400)

        # Check if phone already exists in User or ArtistProfile
        if User.objects.filter(phone=phone).exists() or ArtistProfile.objects.filter(phone=phone).exists():
            return Response({'error': 'Phone number already exists.'}, status=400)

        # Create Location
        location_obj, _ = Location.objects.get_or_create(
            city=data['city'],
            state=data['state'],
            pincode=data.get('pincode', ''),
            defaults={
                'lat': data.get('lat', 0.0),
                'lng': data.get('lng', 0.0)
            }
        )

        # Use transaction to ensure both User and ArtistProfile are created together
        with transaction.atomic():
            # Create User
            user = User.objects.create(
                username=phone,
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=phone,
                email=data.get('email', ''),
                gender=data.get('gender', ''),
                role='artist',
                location=location_obj,
                otp_verified=True,
                is_artist_approved=True
            )

            # Create ArtistProfile
            ArtistProfile.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                email=user.email,
                gender=user.gender,
                location=location_obj,
                status='approved',
                total_bookings=0
            )

        # Generate JWT tokens like normal registration
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Artist created successfully by admin.',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'role': user.role,
        }, status=status.HTTP_201_CREATED)

