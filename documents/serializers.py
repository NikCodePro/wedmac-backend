import cloudinary.uploader
from rest_framework import serializers
from .models import Document


class DocumentUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        max_length=8,
        min_length=1,
        help_text="Upload up to 8 files at a time"
    )
    file_type = serializers.ChoiceField(
        choices=Document.FILE_TYPE_CHOICES,
        default='image'
    )
    tag = serializers.CharField(max_length=50, required=False, default='')

    def validate_files(self, value):
        if len(value) > 8:
            raise serializers.ValidationError("Maximum 8 files can be uploaded at a time.")
        return value

    def create(self, validated_data):
        files = validated_data.pop('files')
        user = self.context['request'].user
        file_type = validated_data.get('file_type', 'other')
        tag = validated_data.get('tag', '')

        uploaded_documents = []

        for uploaded_file in files:
            # Deactivate previous document of same type and tag
            Document.objects.filter(
                uploaded_by=user,
                file_type=file_type,
                tag=tag,
                is_active=True
            ).update(is_active=False)

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                uploaded_file,
                resource_type="auto",  # Supports image, pdf, etc.
                folder="artist_documents/"  # Optional: Cloudinary folder
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
            uploaded_documents.append(document)

        return uploaded_documents
