from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import cloudinary.uploader

from .serializers import DocumentUploadSerializer
from .models import Document

class DocumentUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Handle multiple files upload
        files = request.FILES.getlist('files')
        if not files:
            return Response({"error": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)

        if len(files) > 8:
            return Response({"error": "Maximum 8 files can be uploaded at a time."}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare data for serializer
        data = {
            'files': files,
            'file_type': request.data.get('file_type', 'image'),
            'tag': request.data.get('tag', '')
        }

        serializer = DocumentUploadSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            uploaded_documents = serializer.save()

            # Prepare response data
            documents_data = []
            for doc in uploaded_documents:
                documents_data.append({
                    "document_id": doc.id,
                    "file_name": doc.file_name,
                    "file_type": doc.file_type,
                    "tag": doc.tag,
                    "file_url": doc.file_url
                })

            return Response({
                "message": f"{len(uploaded_documents)} document(s) uploaded successfully.",
                "count": len(uploaded_documents),
                "documents": documents_data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
