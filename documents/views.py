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
            documents = serializer.save()
            response_data = {
                "message": f"{len(documents)} documents uploaded successfully.",
                "documents": [
                    {
                        "document_id": doc.id,
                        "file_name": doc.file_name,
                        "file_type": doc.file_type,
                        "tag": doc.tag,
                        "file_url": doc.file_url
                    } for doc in documents
                ]
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
