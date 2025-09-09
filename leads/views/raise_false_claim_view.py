# leads/views/raise_false_claim_view.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from media.cloudinary import CloudinaryUploader

from leads.models.models import Lead
from leads.serializers.false_lead_claim_serializer import FalseLeadClaimSerializer
from leads.models.false_lead_claim import FalseClaimDocument

class RaiseFalseLeadClaimView(APIView):
    """
    Artist API: Raise a false lead claim
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            artist = request.user.artist_profile
        except:
            return Response({"error": "Only artists can raise false claims."}, status=403)

        serializer = FalseLeadClaimSerializer(data=request.data)
        if serializer.is_valid():
            claim = serializer.save(artist=artist)

            # Handle document uploads separately
            files = request.FILES.getlist('proof_documents')
            uploaded_docs = []
            for file in files:
                upload_result = CloudinaryUploader.upload_file(file, folder="false_claim_documents/")
                if 'error' in upload_result:
                    return Response({"error": f"File upload failed: {upload_result['error']}"}, status=400)

                doc = FalseClaimDocument.objects.create(
                    false_claim=claim,
                    lead=claim.lead,
                    file_name=file.name,
                    file_type=file.content_type.split('/')[-1],
                    file_url=upload_result.get('url'),
                    public_id=upload_result.get('public_id'),
                    tag='proof'
                )
                uploaded_docs.append(doc)

            # Re-serialize to include proof_documents details
            response_serializer = FalseLeadClaimSerializer(claim)
            return Response({
                "message": "False lead claim raised successfully.",
                "claim": response_serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
