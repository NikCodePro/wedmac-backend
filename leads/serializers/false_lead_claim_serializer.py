from rest_framework import serializers
from documents.models import Document
from leads.models.false_lead_claim import FalseLeadClaim

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'file_name', 'file_type', 'file_url', 'tag', 'created_at']

class FalseLeadClaimSerializer(serializers.ModelSerializer):
    # Write: accept list of doc IDs
    proof_documents_ids = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    # Read: show document details
    proof_documents = DocumentSerializer(many=True, read_only=True)

    lead_id = serializers.IntegerField(source='lead.id', read_only=True)
    lead_first_name = serializers.CharField(source='lead.first_name', read_only=True)
    lead_last_name = serializers.CharField(source='lead.last_name', read_only=True)
    lead_email = serializers.CharField(source='lead.email', read_only=True)
    lead_phone = serializers.CharField(source='lead.phone', read_only=True)

    class Meta:
        model = FalseLeadClaim
        fields = [
            'id', 'lead', 'lead_id','lead_first_name', 'lead_last_name','lead_email', 'lead_phone',
            'reason', 'proof_documents_ids', 'proof_documents',
            'status', 'admin_note', 'created_at'
        ]
        read_only_fields = ['status', 'admin_note', 'created_at', 'proof_documents']

    def create(self, validated_data):
        documents = validated_data.pop('proof_documents_ids', [])
        claim = FalseLeadClaim.objects.create(**validated_data)
        claim.proof_documents.set(documents)
        return claim
