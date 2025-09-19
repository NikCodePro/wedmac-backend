import cloudinary.uploader
from rest_framework import serializers
from .models import Document

class DocumentUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        max_length=8,
        allow_empty=False,
        help_text="List of files to upload (max 8)"
    )
    file_type = serializers.ChoiceField(choices=Document.FILE_TYPE_CHOICES, default='image')
    tag = serializers.CharField(max_length=50, allow_blank=True, required=False)

    def create(self, validated_data):
        files = validated_data.pop('files')
        user = self.context['request'].user
        file_type = validated_data.get('file_type', 'image')
        tag = validated_data.get('tag', '')

        documents = []
        for uploaded_file in files:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                uploaded_file,
                resource_type="auto",
                folder="artist_documents/"
            )
            # Save metadata to DB
            document = Document.objects.create(
                uploaded_by=user,
                file_name=uploaded_file.name,
                file_type=file_type,
                tag=tag,
                file_url=result.get("secure_url"),
                public_id=result.get("public_id"),
                is_active=True
            )
            documents.append(document)
        return documents
