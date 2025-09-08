from rest_framework import serializers
from documents.models import Document
from leads.models.false_lead_claim import FalseLeadClaim, FalseClaimDocument

class FalseClaimDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FalseClaimDocument
        fields = ['id', 'file_name', 'file_type', 'file_url', 'tag', 'created_at']

class FalseLeadClaimSerializer(serializers.ModelSerializer):
    # Write: accept list of document data
    proof_documents_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

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
            'reason', 'proof_documents_data', 'proof_documents',
            'status', 'admin_note', 'created_at'
        ]
        read_only_fields = ['status', 'admin_note', 'created_at', 'proof_documents']

    def get_proof_documents(self, obj):
        """Return documents from FalseClaimDocument model"""
        documents = obj.documents.all()
        return FalseClaimDocumentSerializer(documents, many=True).data

    def create(self, validated_data):
        documents_data = validated_data.pop('proof_documents_data', [])
        print(f"DEBUG: Received documents_data: {documents_data}")  # Debug log
        print(f"DEBUG: validated_data after pop: {validated_data}")  # Debug log

        claim = FalseLeadClaim.objects.create(**validated_data)
        print(f"DEBUG: Created claim with ID: {claim.id}")  # Debug log

        # Create FalseClaimDocument entries
        for i, doc_data in enumerate(documents_data):
            print(f"DEBUG: Processing document {i+1}: {doc_data}")  # Debug log
            try:
                document = FalseClaimDocument.objects.create(
                    false_claim=claim,
                    lead=claim.lead,
                    **doc_data
                )
                print(f"DEBUG: Created document with ID: {document.id}")  # Debug log
            except Exception as e:
                print(f"DEBUG: Error creating document: {str(e)}")  # Debug log

        return claim
