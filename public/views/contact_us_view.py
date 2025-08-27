from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from public.models import ContactUs
from public.serliazers.contact_us_serializer import ContactUsSerializer
from superadmin_auth.permissions import IsSuperAdmin

class ContactUsCreateAPIView(generics.CreateAPIView):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def get_contact_submissions(request):
    try:
        contacts = ContactUs.objects.all().order_by('-created_at')
        serializer = ContactUsSerializer(contacts, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
