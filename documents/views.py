from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import cloudinary.uploader

from .serializers import DocumentUploadSerializer
from .models import Document

class DocumentUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            file = request.FILES.get("file")
            file_type = serializer.validated_data.get("file_type")
            tag = serializer.validated_data.get("tag", "")
            user = request.user

            # Deactivate previous document
            Document.objects.filter(
                uploaded_by=user,
                file_type=file_type,
                tag=tag,
                is_active=True
            ).update(is_active=False)

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file,
                resource_type="auto",
                folder="artist_documents/"
            )

            # Save new document
            document = Document.objects.create(
                uploaded_by=user,
                file_name=file.name,
                file_type=file_type,
                tag=tag,
                file_url=result.get("secure_url"),
                public_id=result.get("public_id"),
                is_active=True
            )

            return Response({
                "message": "Document uploaded successfully.",
                "document_id": document.id,
                "file_name": document.file_name,
                "file_type": document.file_type,
                "tag": document.tag,
                "file_url": document.file_url
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)