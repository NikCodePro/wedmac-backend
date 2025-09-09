from rest_framework import serializers
from documents.models import Document
from leads.models.false_lead_claim import FalseLeadClaim, FalseClaimDocument

class FalseClaimDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FalseClaimDocument
        fields = ['id', 'file_name', 'file_type', 'file_url', 'tag', 'created_at']

class FalseLeadClaimSerializer(serializers.ModelSerializer):
    # Read: show document details from FalseClaimDocument
    proof_documents = serializers.SerializerMethodField()

    lead_id = serializers.IntegerField(source='lead.id', read_only=True)
    lead_first_name = serializers.CharField(source='lead.first_name', read_only=True)
    lead_last_name = serializers.CharField(source='lead.last_name', read_only=True)
    lead_email = serializers.CharField(source='lead.email', read_only=True)
    lead_phone = serializers.CharField(source='lead.phone', read_only=True)

    class Meta:
        model = FalseLeadClaim
        fields = [
            'id', 'lead', 'lead_id','lead_first_name', 'lead_last_name','lead_email', 'lead_phone',
            'reason', 'proof_documents',
            'status', 'admin_note', 'created_at'
        ]
        read_only_fields = ['status', 'admin_note', 'created_at', 'proof_documents']

    def get_proof_documents(self, obj):
        """Return documents from FalseClaimDocument model"""
        documents = obj.documents.all()
        return FalseClaimDocumentSerializer(documents, many=True).data
